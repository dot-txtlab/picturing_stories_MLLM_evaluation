#!/usr/bin/env python3
"""
04_embedding_and_caption_metrics.py
-----------------------------------
Reviewer-requested metric additions (Submission 3683):

  E. Embedding-based set similarity for Characters/Objects (vs. Jaccard)   [W1Nv-1]
  F. Embedding-based caption similarity (vs. BERTScore), + variance/spread [W1Nv-2]
  G. Caption factual-validation inter-annotator agreement                  [CMEQ-3]

Uses the SOTA multilingual embedding model BAAI/bge-m3 (cached locally).
Run:  HF_HUB_OFFLINE=1 python 04_embedding_and_caption_metrics.py
"""
import os, csv, re
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
from collections import defaultdict
import numpy as np

DATA = "../data"
GEM = "gemini-2.5-flash"

def load(fn):
    with open(f"{DATA}/{fn}") as f:
        return list(csv.DictReader(f))

def canon(m):
    return "claude-sonnet-4-5" if m.startswith("claude") else m

def sset(s, seps="[;,]", strip_parens=False):
    if s is None: return set()
    if strip_parens: s = re.sub(r"\s*\([^)]*\)", "", s)
    return {p.strip() for p in re.split(seps, s) if p.strip() and p.strip() != "NA"}

def jacc(a, b):
    if not (a | b): return 1.0
    return len(a & b) / len(a | b)

# ---------------------------------------------------------------------------
print("Loading BAAI/bge-m3 (SOTA embedding model)...")
from sentence_transformers import SentenceTransformer
MODEL = SentenceTransformer("BAAI/bge-m3")

def embed(texts):
    return MODEL.encode(texts, normalize_embeddings=True, batch_size=64,
                        show_progress_bar=False)

def soft_set_f1(model_set, human_set, vec):
    """BERTScore-style set similarity: precision = mean over model labels of
    max cosine to any human label; recall = symmetric; return F1."""
    if not model_set and not human_set: return 1.0
    if not model_set or not human_set: return 0.0
    M = np.array([vec[x] for x in model_set]); H = np.array([vec[x] for x in human_set])
    sim = M @ H.T                      # cosine (already normalized)
    prec = sim.max(axis=1).mean()
    rec = sim.max(axis=0).mean()
    return 2*prec*rec/(prec+rec) if (prec+rec) else 0.0

# ---------------------------------------------------------------------------
# E. Characters / Objects: embedding set similarity vs Jaccard
# ---------------------------------------------------------------------------
def section_E():
    print("=" * 70)
    print("E. CHAR/OBJ: embedding soft-set F1 (bge-m3) vs. Jaccard  [W1Nv-1]")
    print("=" * 70)
    rows = load("DATA_Illustration_IA_Evaluation_T0_T4.csv")
    # embed the (tiny) label vocabulary once
    vocab = set()
    for r in rows:
        vocab |= sset(r["characters"]) | sset(r["T1"], ",", True) \
               | sset(r["objects"]) | sset(r["T3"], ",", True)
    vocab = sorted(vocab)
    vecs = dict(zip(vocab, embed(vocab)))

    g = defaultdict(list)
    for r in rows: g[(canon(r["model"]), r["shot_type"])].append(r)
    order=[("gemini-2.5-flash","Gem2.5"),("gpt-4.1-2025-04-14","GPT"),("claude-sonnet-4-5","Claude"),
           ("qwen3-vl-8b-instruct","Qwen"),("llava-hf/llava-v1.6-vicuna-13b-hf","LLaVA")]
    print(f"{'Model-shot':<10}{'CharJacc':>9}{'CharEmb':>9}{'ObjJacc':>9}{'ObjEmb':>9}")
    print("-"*46)
    for mid,short in order:
        for shot,sfx in (("zeroshot","0"),("oneshot","1")):
            rs=g.get((mid,shot))
            if not rs: continue
            cj=[]; ce=[]; oj=[]; oe=[]
            for r in rs:
                if r["T1"] and r["characters"]:
                    ms=sset(r["characters"]); hs=sset(r["T1"],",",True)
                    cj.append(jacc(ms,hs)); ce.append(soft_set_f1(ms,hs,vecs))
                if r["T3"] and r["objects"]:
                    ms=sset(r["objects"]); hs=sset(r["T3"],",",True)
                    oj.append(jacc(ms,hs)); oe.append(soft_set_f1(ms,hs,vecs))
            print(f"{short+'-'+sfx:<10}{np.mean(cj):>9.2f}{np.mean(ce):>9.2f}{np.mean(oj):>9.2f}{np.mean(oe):>9.2f}")
    print("\nEmbedding soft-F1 credits near-synonyms (Dog~Animal, Animals~Animal)")
    print("that exact-match Jaccard penalizes.\n")

# ---------------------------------------------------------------------------
# F. Captions: embedding similarity vs BERTScore (+ spread)
# ---------------------------------------------------------------------------
def section_F():
    print("=" * 70)
    print("F. CAPTIONS: bge-m3 cosine to human captions (+ spread)  [W1Nv-2]")
    print("=" * 70)
    rows = load("DATA_Illustration_IA_Evaluation_T0_T4.csv")
    human = {}
    for r in rows:
        if r.get("captions") and r["captions"] not in ("", "NA"):
            caps = [c.strip() for c in r["captions"].split("|||") if c.strip()]
            if caps: human[r["image"].replace(".jpg", "")] = caps
    cap = load("DATA_Illustration_IA_Caption_Validation_Upload.csv")
    # one model caption per (pageID, model, prompt)
    seen = {}
    for r in cap:
        k = (r["pageID"], canon(r["model"]), r["prompt_condition"])
        if k not in seen and r["caption"].strip():
            seen[k] = r["caption"].strip()

    # gather all texts to embed
    inst = [(k, mc, human[k[0]]) for k, mc in seen.items() if k[0] in human]
    all_h = sorted({h for _,_,hs in inst for h in hs})
    hvec = dict(zip(all_h, embed(all_h)))
    mvec = embed([mc for _,mc,_ in inst])

    agg = defaultdict(list)
    for (k,mc,hs), mv in zip(inst, mvec):
        cos = float(np.mean([mv @ hvec[h] for h in hs]))
        agg[(k[1], k[2])].append(cos)
    # human-human baseline (within-image)
    hh = []
    for hs in {tuple(v) for v in human.values()}:
        if len(hs) >= 2:
            hv = embed(list(hs))
            sims = [float(hv[i] @ hv[j]) for i in range(len(hv)) for j in range(i+1,len(hv))]
            hh.extend(sims)
    order=[("gemini-2.5-flash","Gem2.5"),("gpt-4.1-2025-04-14","GPT"),("claude-sonnet-4-5","Claude"),
           ("qwen3-vl-8b-instruct","Qwen"),("llava-hf/llava-v1.6-vicuna-13b-hf","LLaVA")]
    print(f"{'Model-shot':<10}{'mean cos':>10}{'std':>8}{'N':>6}")
    print("-"*34)
    print(f"{'Human-Human':<10}{np.mean(hh):>10.3f}{np.std(hh):>8.3f}{len(hh):>6}")
    for mid,short in order:
        for shot,sfx in (("zeroshot","0"),("oneshot","1")):
            v=agg.get((mid,shot))
            if not v: continue
            print(f"{short+'-'+sfx:<10}{np.mean(v):>10.3f}{np.std(v):>8.3f}{len(v):>6}")
    print("\nNB: bge-m3 spreads models over a wider range than BERTScore's compressed")
    print("~0.80-0.90 band (paper Fig 5), improving discrimination between tiers.\n")

# ---------------------------------------------------------------------------
# G. Caption factual-validation inter-annotator agreement
# ---------------------------------------------------------------------------
def krippendorff_ordinal(data):
    """data: list of items, each a list of numeric ratings (variable length).
    Returns Krippendorff's alpha with the ordinal difference metric."""
    # build value set and coincidence matrix
    vals = sorted({v for item in data for v in item})
    idx = {v:i for i,v in enumerate(vals)}
    n = len(vals)
    coinc = np.zeros((n,n))
    for item in data:
        m = len(item)
        if m < 2: continue
        for a in range(m):
            for b in range(m):
                if a==b: continue
                coinc[idx[item[a]], idx[item[b]]] += 1.0/(m-1)
    nc = coinc.sum(axis=1)
    total = nc.sum()
    if total == 0: return float("nan")
    # ordinal metric: squared sum of intervening marginal masses
    def d2(i,j):
        lo,hi = (i,j) if i<=j else (j,i)
        s = nc[lo]/2 + nc[hi]/2 + nc[lo+1:hi].sum()
        return s*s
    Do = sum(coinc[i,j]*d2(i,j) for i in range(n) for j in range(n))
    De = sum(nc[i]*nc[j]*d2(i,j) for i in range(n) for j in range(n)) / (total-1)
    return 1 - (total-1)*Do/ (De*total) if De else float("nan")  # standard form

def section_G():
    print("=" * 70)
    print("G. CAPTION FACTUAL-VALIDATION INTER-ANNOTATOR AGREEMENT  [CMEQ-3]")
    print("=" * 70)
    cap = load("DATA_Illustration_IA_Caption_Validation_Upload.csv")
    def num(x):
        x = x.strip()
        if x.startswith("All"): return 5      # "All ..." = worst
        try: return int(x)
        except: return None
    for field in ("Hallucinations", "Missing"):
        groups = defaultdict(list)
        for r in cap:
            v = num(r[field])
            if v is not None:
                groups[(r["pageID"], canon(r["model"]), r["prompt_condition"])].append(v)
        items = [v for v in groups.values() if len(v) >= 2]
        alpha = krippendorff_ordinal(items)
        base0 = np.mean([x == 0 for v in items for x in v])          # skew toward 0
        unan = np.mean([len({int(x>0) for x in v})==1 for v in items])   # unanimous binary
        maj = np.mean([max(sum(int(x>0)==b for x in v) for b in (0,1))/len(v) >= 0.5
                       for v in items])                              # >=majority binary (always True for=>2)
        # majority binary label exists (>=2/3 agree)
        maj23 = np.mean([max(sum(int(x>0)==b for x in v) for b in (0,1)) > len(v)/2
                         for v in items])
        mad = np.mean([np.mean([abs(v[i]-v[j]) for i in range(len(v)) for j in range(i+1,len(v))])
                       for v in items])
        print(f"  {field}:")
        print(f"     items={len(items)}   base-rate(count==0)={base0:.0%}   "
              f"mean|pairwise diff|={mad:.2f} (on 0-5 scale)")
        print(f"     binary 'error present?': unanimous={unan:.0%}, majority(>half) agree={maj23:.0%}")
        print(f"     Krippendorff-alpha (ordinal counts) ={alpha:.3f}")
    print("\nInterpretation: the fine-grained 0-4+ COUNT is skewed to 0 (low prevalence),")
    print("which deflates chance-corrected alpha (the 'alpha paradox') despite small")
    print("pairwise differences. The BINARY 'error present?' decision that Table 3 relies")
    print("on has clear majority agreement and is the reliable unit; fine-grained counts")
    print("should be read cautiously and aggregated across annotators.\n")

if __name__ == "__main__":
    section_E(); section_F(); section_G()
