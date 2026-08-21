#!/usr/bin/env python3
"""
03_rebuttal_analyses.py
-----------------------
Numeric analyses requested by reviewers (Submission 3683), all from the released
CSVs (no new model inference). Sections:

  A. Revised Table 2 (model metrics and human agreement in separate panels)        [CMEQ-1]
  B. Actions micro-F1 robustness: all vs. n=1-entity subset                        [CMEQ-2]
  C. Category-level bias tests with Benjamini-Hochberg correction                  [CMEQ-4]
  D. Corpus-level (aggregate) agreement, per model, not just Gemini                [CMEQ-5]

Run:  python 03_rebuttal_analyses.py
"""
import csv, re
from collections import defaultdict
import numpy as np
from scipy.stats import fisher_exact, pearsonr
from statsmodels.stats.multitest import multipletests

DATA = "../data"
GEM = "gemini-2.5-flash"

def load(fn):
    with open(f"{DATA}/{fn}") as f:
        return list(csv.DictReader(f))

def canon(m):
    return "claude-sonnet-4-5" if m.startswith("claude") else m

def sset(s, seps="[;,]", strip_parens=False, drop_na=False):
    if s is None: return set()
    if strip_parens: s = re.sub(r"\s*\([^)]*\)", "", s)
    out = {p.strip() for p in re.split(seps, s) if p.strip()}
    if drop_na: out.discard("NA")   # 'NA' = missing human annotation, not a label choice
    return out

def jacc(a, b):
    if not (a | b): return 1.0
    return len(a & b) / len(a | b)

def hmean_intensity(t4):
    d = re.findall(r"\d", t4 or "")
    return sum(map(int, d)) / len(d) if d else None

# ---------------------------------------------------------------------------
# A. Revised Table 2
# ---------------------------------------------------------------------------
def section_A():
    print("=" * 70)
    print("A. REVISED TABLE 2  (model metrics and human agreement separated)")
    print("=" * 70)
    rows = load("DATA_Illustration_IA_Evaluation_T0_T4.csv")
    t5 = load("DATA_Illustration_IA_Evaluation_T5.csv")
    g = defaultdict(list)
    for r in rows: g[(canon(r["model"]), r["shot_type"])].append(r)
    ga = defaultdict(list)
    for r in t5: ga[(canon(r["model"]), r["shot_type"])].append(r)

    def actions_f1(rs, only_n1=True):
        tp = fp = fn = 0
        for r in rs:
            m = re.search(re.escape(r["entity"].strip()) + r"\[n=(\d+)\]\{([^}]*)\}", r["T5"] or "")
            if not m: continue
            if only_n1 and int(m.group(1)) != 1: continue
            H = {a.strip() for a in m.group(2).split(";") if a.strip()}
            M = {a.strip() for a in (r["actions"] or "").split(";") if a.strip()}
            tp += len(M & H); fp += len(M - H); fn += len(H - M)
        p = tp/(tp+fp) if tp+fp else 0; rc = tp/(tp+fn) if tp+fn else 0
        return 2*p*rc/(p+rc) if p+rc else float("nan")

    order = [("claude-sonnet-4-5","Claude"),(GEM,"Gem2.5"),("gpt-4.1-2025-04-14","GPT"),
             ("qwen3-vl-8b-instruct","Qwen"),("llava-hf/llava-v1.6-vicuna-13b-hf","LLaVA")]
    print("Panel A: Model performance against human consensus annotations")
    hdr = f"{'Model':<10}{'Illus%':>8}{'Set%':>7}{'CharJ':>7}{'ObjJ':>7}{'IntD':>7}{'ActF1(n=1)':>12}"
    print(hdr); print("-"*len(hdr))
    for mid, short in order:
        for shot, sfx in (("zeroshot","0"),("oneshot","1")):
            rs = g.get((mid, shot))
            if not rs: continue
            ill = [r for r in rs if r["T0"] and r["T0"]!="NA"]
            illv = 100*sum(r["illustration_present"].strip()==r["T0"].strip() for r in ill)/len(ill)
            st = [r for r in rs if r["T2"] and r["T2"]!="NA" and "," not in r["T2"]]
            stv = 100*sum(r["scene_setting"].strip()==r["T2"].strip() for r in st)/len(st)
            cj = np.mean([jacc(sset(r["characters"]), sset(r["T1"],",",True)) for r in rs if r["T1"] and r["characters"]])
            oj = np.mean([jacc(sset(r["objects"]), sset(r["T3"],",",True)) for r in rs if r["T3"] and r["objects"]])
            dd = []
            for r in rs:
                h = hmean_intensity(r["T4"])
                try: mv = float(r["emotional_intensity"])
                except: continue
                if h is not None: dd.append(abs(mv-h))
            f1 = actions_f1(ga.get((mid, shot), []))
            print(f"{short+'-'+sfx:<10}{illv:>8.1f}{stv:>7.1f}{cj:>7.2f}{oj:>7.2f}{np.mean(dd):>7.2f}{f1:>12.2f}")

    print("\nPanel B: Human inter-annotator agreement")
    print(f"{'Task':<22}{'Full%':>8}{'Majority%':>11}{'Jaccard':>10}{'OrdDist':>10}")
    print("-" * 61)
    ag = {r["Task"]: r for r in load("Agreement_Table.csv")}
    for task, label in (("T0", "Illustration"), ("T1", "Characters"),
                        ("T2", "Setting"), ("T3", "Objects"),
                        ("T4", "Emotional intensity"), ("T5", "Actions")):
        r = ag[task]
        print(f"{label:<22}{r['Full Agree']:>8}{r['Majority']:>11}"
              f"{r['Jaccard']:>10}{r['Ordinal Distance']:>10}")
    print("\nNotes: Panel A uses the corrected mean-based intensity distance and"
          " singleton-only Actions micro-F1. Panel B reports human agreement in"
          " each measure's native units; it is an interpretive reference, not a"
          " model-performance row.\n")

# ---------------------------------------------------------------------------
# B. Actions robustness (n=1 subset)
# ---------------------------------------------------------------------------
def section_B():
    print("=" * 70)
    print("B. ACTIONS micro-F1 ROBUSTNESS (all queried entities vs. n=1 subset)")
    print("=" * 70)
    t5 = load("DATA_Illustration_IA_Evaluation_T5.csv")
    g = defaultdict(list)
    for r in t5: g[(canon(r["model"]), r["shot_type"])].append(r)
    def f1(rs, only_n1):
        tp=fp=fn=0; used=0
        for r in rs:
            mm = re.search(re.escape(r["entity"].strip()) + r"\[n=(\d+)\]\{([^}]*)\}", r["T5"] or "")
            if not mm: continue
            if only_n1 and int(mm.group(1))!=1: continue
            used += 1
            H={a.strip() for a in mm.group(2).split(";") if a.strip()}
            M={a.strip() for a in (r["actions"] or "").split(";") if a.strip()}
            tp+=len(M&H); fp+=len(M-H); fn+=len(H-M)
        p=tp/(tp+fp) if tp+fp else 0; rc=tp/(tp+fn) if tp+fn else 0
        return (2*p*rc/(p+rc) if p+rc else float("nan")), used
    print(f"{'Model-shot':<10}{'F1(all)':>9}{'N(all)':>8}{'F1(n=1)':>9}{'N(n=1)':>8}")
    print("-"*44)
    order=[("gemini-2.5-flash","Gem2.5"),("gpt-4.1-2025-04-14","GPT"),("claude-sonnet-4-5","Claude"),
           ("qwen3-vl-8b-instruct","Qwen"),("llava-hf/llava-v1.6-vicuna-13b-hf","LLaVA")]
    for mid,short in order:
        for shot,sfx in (("zeroshot","0"),("oneshot","1")):
            rs=g.get((mid,shot))
            if not rs: continue
            fa,na=f1(rs,False); fn1,nn1=f1(rs,True)
            print(f"{short+'-'+sfx:<10}{fa:>9.3f}{na:>8}{fn1:>9.3f}{nn1:>8}")
    # entity selection facts (Gemini zeroshot)
    gz=g[(GEM,"zeroshot")]
    present=0; n1=0; ncount=defaultdict(int); tot=0
    for r in gz:
        mm=re.search(re.escape(r["entity"].strip())+r"\[n=(\d+)\]", r["T5"] or "")
        if r["T5"]: tot+=1
        if mm:
            present+=1; ncount[int(mm.group(1))]+=1
            if int(mm.group(1))==1: n1+=1
    print(f"\nEntity-selection facts (Gemini zeroshot, N={tot}):")
    print(f"  queried entity present in human annotation: {present}/{tot}")
    print(f"  instance-count distribution of queried entity: {dict(sorted(ncount.items()))}")
    print(f"  fraction with exactly one instance (n=1): {n1/present:.3f}\n")

# ---------------------------------------------------------------------------
# C. Category-level bias tests with BH correction
# ---------------------------------------------------------------------------
def bias_table(cat_counts_model, cat_counts_human, label):
    cats = sorted(set(cat_counts_model) | set(cat_counts_human))
    Nm = sum(cat_counts_model.values()); Nh = sum(cat_counts_human.values())
    rows=[]
    for c in cats:
        nm=cat_counts_model.get(c,0); nh=cat_counts_human.get(c,0)
        if nm+nh < 10:  # skip ultra-rare cells
            continue
        table=[[nm, Nm-nm],[nh, Nh-nh]]
        orv,p = fisher_exact(table)
        rows.append([c,nm,nh,orv,p])
    ps=[r[4] for r in rows]
    rej,padj,_,_=multipletests(ps, alpha=0.05, method="fdr_bh")
    print(f"\n[{label}]  ({len(rows)} categories tested, BH-corrected)")
    print(f"  {'category':<32}{'OR':>6}{'p_raw':>9}{'p_adj':>9}  sig")
    for (c,nm,nh,orv,p),pa,rj in sorted(zip(rows,padj,rej), key=lambda z:z[0][4]):
        star = "***" if rj else ""
        print(f"  {c[:32]:<32}{orv:>6.2f}{p:>9.3f}{pa:>9.3f}  {star}")

def section_C():
    print("=" * 70)
    print("C. CATEGORY-LEVEL BIAS TESTS w/ BENJAMINI-HOCHBERG (Gemini zeroshot)")
    print("=" * 70)
    rows = load("DATA_Illustration_IA_Evaluation_T0_T4.csv")
    df=[r for r in rows if r["model"]==GEM and r["shot_type"]=="zeroshot"
        and r["T0"]=="Yes" and r["illustration_present"]=="Yes"]
    def counts(field, seps, strip=False):
        c=defaultdict(int)
        for r in df:
            for x in sset(r[field], seps, strip, drop_na=True): c[x]+=1
        return c
    section_C._n = len(df)
    bias_table(counts("characters","[;,]"), counts("T1",",",True), "Characters")
    bias_table(counts("objects","[;,]"), counts("T3",",",True), "Objects")
    # actions
    t5=load("DATA_Illustration_IA_Evaluation_T5.csv")
    da=[r for r in t5 if r["model"]==GEM and r["shot_type"]=="zeroshot"]
    mc=defaultdict(int); hc=defaultdict(int)
    for r in da:
        for a in (r["actions"] or "").split(";"):
            if a.strip(): mc[a.strip()]+=1
        mm=re.search(re.escape(r["entity"].strip())+r"\[n=\d+\]\{([^}]*)\}", r["T5"] or "")
        if mm:
            for a in mm.group(1).split(";"):
                if a.strip(): hc[a.strip()]+=1
    bias_table(mc, hc, "Actions")
    print(f"\n(Character/object tests on N={section_C._n} illustration-present pages)\n")

# ---------------------------------------------------------------------------
# D. Corpus-level agreement per model
# ---------------------------------------------------------------------------
def section_D():
    print("=" * 70)
    print("D. CORPUS-LEVEL (AGGREGATE) AGREEMENT, PER MODEL  [not just Gemini]")
    print("=" * 70)
    rows = load("DATA_Illustration_IA_Evaluation_T0_T4.csv")
    g=defaultdict(list)
    for r in rows: g[canon(r["model"])].append(r)
    def props(rs, field, seps, strip=False):
        c=defaultdict(int)
        for r in rs:
            for x in sset(r[field],seps,strip, drop_na=True): c[x]+=1
        tot=sum(c.values())
        return {k:v/tot for k,v in c.items()}
    def agree(rs, mfield, hfield, seps_h):
        pm=props(rs, mfield, "[;,]"); ph=props(rs, hfield, seps_h, True)
        cats=sorted(set(pm)|set(ph))
        a=np.array([pm.get(c,0) for c in cats]); b=np.array([ph.get(c,0) for c in cats])
        r,_=pearsonr(a,b); mad=np.mean(np.abs(a-b))
        return r, mad
    print(f"{'Model':<10}{'Char r':>8}{'Char MAD':>9}{'Obj r':>8}{'Obj MAD':>9}{'Set r':>8}{'Int r':>8}")
    print("-"*60)
    order=[("gemini-2.5-flash","Gem2.5"),("gpt-4.1-2025-04-14","GPT"),("claude-sonnet-4-5","Claude"),
           ("qwen3-vl-8b-instruct","Qwen"),("llava-hf/llava-v1.6-vicuna-13b-hf","LLaVA")]
    for mid,short in order:
        rs=[r for r in g[mid] if r["shot_type"]=="zeroshot"]
        if not rs: continue
        cr,cm=agree(rs,"characters","T1",",")
        orr,om=agree(rs,"objects","T3",",")
        sr,sm=agree(rs,"scene_setting","T2",",")
        # intensity corpus corr
        mv=[]; hv=[]
        for r in rs:
            h=hmean_intensity(r["T4"])
            try: m=float(r["emotional_intensity"])
            except: continue
            if h is not None: mv.append(m); hv.append(h)
        ir,_=pearsonr(mv,hv)
        print(f"{short:<10}{cr:>8.2f}{cm:>9.3f}{orr:>8.2f}{om:>9.3f}{sr:>8.2f}{ir:>8.2f}")
    print("\nSet r uses the 3-category setting distribution; Int r is image-level.\n")

if __name__ == "__main__":
    section_A(); section_B(); section_C(); section_D()
