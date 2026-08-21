#!/usr/bin/env python3
"""
02_table2_metrics.py
--------------------
Regenerates Table 2 of "Evaluating Multi-Modal LLMs on Historical Book
Illustrations" from the released evaluation CSVs. No model inference required.

Table 2 columns (per model x prompting condition):
  - Illustration  : exact-match accuracy (%)   vs human majority label T0
  - Setting       : exact-match accuracy (%)   vs human majority label T2
  - Characters    : mean Jaccard (M)           model set vs human set T1
  - Objects       : mean Jaccard (M)           model set vs human set T3
  - Intensity     : mean absolute distance (M) |model - human| on 1-5 scale (T4)
  - Actions       : micro-averaged F1          vs human set for the queried entity (T5)

Human inter-annotator agreement is printed as a separate panel, in each
agreement measure's native units, from data/Agreement_Table.csv.

Usage:
    python 02_table2_metrics.py --actions-n1          # camera-ready Table 2
    python 02_table2_metrics.py                        # all-query robustness
    python 02_table2_metrics.py --actions-n1 --csv out.csv
"""

import csv
import re
import argparse
from collections import defaultdict

DATA = "../data"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def split_set(s, seps="[;,]", strip_parens=False):
    """Split a delimited label string into a normalized set of labels.

    NOTE: 'None' and 'NA' are kept as literal labels, matching the published
    Table 2 convention. 'None' is a valid annotation ("no characters/objects"),
    so agreement on 'None' is meaningful; a model that outputs 'None' where the
    human label is absent ('NA') therefore scores 0 rather than a free match.
    """
    if s is None:
        return set()
    if strip_parens:
        s = re.sub(r"\s*\([^)]*\)", "", s)      # drop human "(examples)" hints
    parts = [p.strip() for p in re.split(seps, s)]
    return {p for p in parts if p}


def canon_model(name):
    """Normalize model ids that differ across files (e.g. Claude carries a
    date suffix in the T0-T4 outputs but not in T5)."""
    if name.startswith("claude"):
        return "claude-sonnet-4-5"
    return name


def jaccard(a, b):
    if not a and not b:
        return 1.0
    if not (a | b):
        return 1.0
    return len(a & b) / len(a | b)


def human_intensity(t4):
    """Human T4 may hold one or more digits; paper averages them."""
    digs = re.findall(r"\d", t4 or "")
    if not digs:
        return None
    return sum(int(d) for d in digs) / len(digs)


def parse_entity_actions(t5, entity):
    """Extract the action set for the queried entity from a T5 block string
    of the form  ENTITY[n=k]{ACT;ACT;...} | OTHER[n=..]{...}."""
    if not t5 or not entity:
        return None
    m = re.search(re.escape(entity.strip()) + r"\[n=\d+\]\{([^}]*)\}", t5)
    if not m:
        return None
    return {a.strip() for a in m.group(1).split(";") if a.strip()}


def entity_instance_count(t5, entity):
    m = re.search(re.escape(entity.strip()) + r"\[n=(\d+)\]", t5 or "")
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# metric computations
# ---------------------------------------------------------------------------

def load(fn):
    with open(f"{DATA}/{fn}") as f:
        return list(csv.DictReader(f))


def compute_t0_t4(rows):
    """Returns {(model, shot): {metric: value}} for illustration/setting/
    characters/objects/intensity."""
    out = defaultdict(dict)
    groups = defaultdict(list)
    for r in rows:
        groups[(canon_model(r["model"]), r["shot_type"])].append(r)

    for key, rs in groups.items():
        # Illustration exact match (T0 present)
        ill = [r for r in rs if r["T0"] and r["T0"] != "NA"]
        out[key]["illustration"] = 100 * sum(
            r["illustration_present"].strip() == r["T0"].strip() for r in ill
        ) / len(ill) if ill else float("nan")

        # Setting exact match (drop multi-label human rows and NA)
        st = [r for r in rs if r["T2"] and r["T2"] != "NA" and "," not in r["T2"]]
        out[key]["setting"] = 100 * sum(
            r["scene_setting"].strip() == r["T2"].strip() for r in st
        ) / len(st) if st else float("nan")

        # Characters Jaccard
        cj = [jaccard(split_set(r["characters"]),
                      split_set(r["T1"], seps=",", strip_parens=True))
              for r in rs if r["T1"] and r["characters"]]
        out[key]["characters"] = sum(cj) / len(cj) if cj else float("nan")

        # Objects Jaccard
        oj = [jaccard(split_set(r["objects"]),
                      split_set(r["T3"], seps=",", strip_parens=True))
              for r in rs if r["T3"] and r["objects"]]
        out[key]["objects"] = sum(oj) / len(oj) if oj else float("nan")

        # Emotional intensity mean absolute distance
        dists = []
        for r in rs:
            h = human_intensity(r["T4"])
            try:
                m = float(r["emotional_intensity"])
            except (TypeError, ValueError):
                m = None
            if h is not None and m is not None:
                dists.append(abs(m - h))
        out[key]["intensity"] = sum(dists) / len(dists) if dists else float("nan")

    return out


def compute_actions(rows, restrict_n1=False):
    """Micro-averaged F1 for the Actions task, per (model, shot)."""
    out = {}
    groups = defaultdict(list)
    for r in rows:
        groups[(canon_model(r["model"]), r["shot_type"])].append(r)

    for key, rs in groups.items():
        tp = fp = fn = 0
        for r in rs:
            H = parse_entity_actions(r["T5"], r["entity"])
            if H is None:
                continue
            if restrict_n1 and entity_instance_count(r["T5"], r["entity"]) != 1:
                continue
            M = {a.strip() for a in (r["actions"] or "").split(";") if a.strip()}
            tp += len(M & H)
            fp += len(M - H)
            fn += len(H - M)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        out[key] = 2 * prec * rec / (prec + rec) if (prec + rec) else float("nan")
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

MODEL_ORDER = [
    "claude-sonnet-4-5", "gemini-2.5-flash", "gpt-4.1-2025-04-14",
    "qwen3-vl-8b-instruct", "llava-hf/llava-v1.6-vicuna-13b-hf",
]
SHOT_ORDER = ["zeroshot", "oneshot"]
SHORT = {
    "claude-sonnet-4-5": "Claude", "gemini-2.5-flash": "Gem2.5",
    "gpt-4.1-2025-04-14": "GPT", "qwen3-vl-8b-instruct": "Qwen",
    "llava-hf/llava-v1.6-vicuna-13b-hf": "LLaVA",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="optional path to write a tidy CSV")
    ap.add_argument("--actions-n1", action="store_true",
                    help="restrict Actions micro-F1 to entities with exactly one "
                         "instance (n=1) in the human annotation")
    args = ap.parse_args()

    t04 = compute_t0_t4(load("DATA_Illustration_IA_Evaluation_T0_T4.csv"))
    act = compute_actions(load("DATA_Illustration_IA_Evaluation_T5.csv"),
                          restrict_n1=args.actions_n1)

    # Human agreement is reported separately from model-versus-consensus scores.
    human = {}
    with open(f"{DATA}/Agreement_Table.csv") as f:
        for r in csv.DictReader(f):
            human[r["Task"]] = r

    print("Panel A: Model performance against human consensus annotations")
    hdr = f"{'Model':<10} {'Illus%':>7} {'Set%':>7} {'CharJ':>6} {'ObjJ':>6} {'IntD':>6} {'ActF1':>6}"
    print(hdr)
    print("-" * len(hdr))

    tidy = []
    for model in MODEL_ORDER:
        for shot in SHOT_ORDER:
            key = (model, shot)
            if key not in t04 and key not in act:
                continue
            m = t04.get(key, {})
            f1 = act.get(key, float("nan"))
            tag = f"{SHORT[model]}-{0 if shot == 'zeroshot' else 1}"
            print(f"{tag:<10} {m.get('illustration', float('nan')):>7.1f} "
                  f"{m.get('setting', float('nan')):>7.1f} "
                  f"{m.get('characters', float('nan')):>6.2f} "
                  f"{m.get('objects', float('nan')):>6.2f} "
                  f"{m.get('intensity', float('nan')):>6.2f} {f1:>6.2f}")
            tidy.append({
                "model": model, "shot": shot,
                "illustration_exact_match": m.get("illustration"),
                "setting_exact_match": m.get("setting"),
                "characters_jaccard": m.get("characters"),
                "objects_jaccard": m.get("objects"),
                "intensity_distance": m.get("intensity"),
                "actions_micro_f1": f1,
            })

    print("\nPanel B: Human inter-annotator agreement")
    print(f"{'Task':<22} {'Full%':>7} {'Majority%':>10} {'Jaccard':>9} {'OrdDist':>9}")
    print("-" * 61)
    for task, label in (("T0", "Illustration"), ("T1", "Characters"),
                        ("T2", "Setting"), ("T3", "Objects"),
                        ("T4", "Emotional intensity"), ("T5", "Actions")):
        r = human[task]
        print(f"{label:<22} {r['Full Agree']:>7} {r['Majority']:>10} "
              f"{r['Jaccard']:>9} {r['Ordinal Distance']:>9}")

    print("\nHuman agreement is an interpretive reference, not a model-performance row.")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(tidy[0].keys()))
            w.writeheader()
            w.writerows(tidy)
        print(f"\nWrote tidy metrics to {args.csv}")


if __name__ == "__main__":
    main()
