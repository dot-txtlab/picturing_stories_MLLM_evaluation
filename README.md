# Replication Package — Evaluating Multi-Modal LLMs on Historical Book Illustrations

This package reproduces the evaluation in *"Evaluating Multi-Modal LLMs on
Historical Book Illustrations"* (Submission 3683). It contains the sampled
illustrations, the raw model outputs, the human annotations, and code to
regenerate the paper's tables, figures, and analyses **without any new model
inference**.

> **Anonymity note:** intended for anonymized hosting during review. Do not add
> author-identifying metadata (git author, ORCID, institutional paths) before
> the review period ends.

## Contents

```
replication_package/
├── README.md
├── code/
│   ├── Picturing_Evaluation.R          # original analysis (load + error + RQ1/RQ2)
│   ├── 02_table2_metrics.py            # regenerates Table 2 from the eval CSVs
│   ├── 03_rebuttal_analyses.py         # revised Table 2, actions robustness,
│   │                                   #   BH-corrected bias tests, corpus-level by model
│   └── 04_embedding_and_caption_metrics.py  # bge-m3 label/caption similarity;
│                                       #   caption inter-annotator agreement
├── results/                           # regenerated result tables + raw outputs
├── data/
│   ├── model_outputs/
│   │   ├── T0-T4_All_Models_Output.jsonl   # raw model responses, tasks T0–T4
│   │   └── T5_All_Models_Output.jsonl      # raw model responses, actions (T5)
│   ├── DATA_Illustration_IA_Evaluation_T0_T4.csv   # model outputs joined to human labels
│   ├── DATA_Illustration_IA_Evaluation_T5.csv      # actions, joined to human labels
│   ├── DATA_Illustration_IA_Annotations_Consensus_All.csv  # human consensus annotations + metadata (decade, etc.)
│   ├── DATA_Illustration_IA_Caption_Validation_Upload.csv   # Prolific factual-validation results
│   └── Agreement_Table.csv          # human inter-annotator agreement (full + majority) per task
└── images/                          # 1,969 sampled illustrations (the evaluation set)
```

## Data provenance

Images are drawn from the **PICTURING STORIES** corpus (27,889 images from 2,827
books, 1728–1932), sourced from the Internet Archive Children's Library. The
underlying page scans are public domain; the visual–narrative annotations were
produced by 6,981 citizen-science volunteers (>700k annotations). This package
ships the **1,969-page random evaluation sample** used in the paper, not the full
corpus. Filenames follow `<book_id>_page<N>.jpg` (the normalized IA identifier).

## Quick start

```bash
# Table 2 (all models × prompting conditions) — pure Python stdlib, no deps
cd code
python 02_table2_metrics.py
python 02_table2_metrics.py --csv table2.csv          # also write a tidy CSV
python 02_table2_metrics.py --actions-n1              # actions restricted to n=1 entities

# Error analyses, RQ1 (date), RQ2 (corpus-level): R (dplyr, stringr, ggplot2, rstatix)
Rscript Picturing_Evaluation.R

# Rebuttal analyses (revised Table 2, actions robustness, BH-corrected bias
# tests, corpus-level agreement by model): needs numpy, scipy, statsmodels
python 03_rebuttal_analyses.py

# Embedding metrics (labels + captions) and caption agreement:
# needs sentence-transformers + a local/downloadable BAAI/bge-m3
HF_HUB_OFFLINE=1 python 04_embedding_and_caption_metrics.py
```

Python deps for the rebuttal scripts: `numpy scipy statsmodels sentence-transformers`.
Outputs for all of the above are archived in `results/`.

`Picturing_Evaluation.R` expects the JSONL outputs and CSVs; adjust the paths at
the top of the script to point at `../data/` (they currently assume a flat
working directory).

## Task schema

| Code | Task | Type | Column(s) |
|------|------|------|-----------|
| T0 | Illustration present | Binary | `illustration_present` / `T0` |
| T1 | Characters | Multi-label (9) | `characters` / `T1` |
| T2 | Setting | Single-label (3) | `scene_setting` / `T2` |
| T3 | Objects | Multi-label (8) | `objects` / `T3` |
| T4 | Emotional intensity | Ordinal (1–5) | `emotional_intensity` / `T4` |
| T5 | Actions | Multi-label (21) | `actions` / `T5` (per queried `entity`) |
| T6 | Caption | Free-text | see caption-validation CSV |

Human columns (`T0`…`T5`) hold consensus/annotation values; model columns hold
the parsed model output. See `prompts/prompts.md` for the exact prompts.

## Reproduction notes (metric conventions)

Reconstructed from the released CSVs; verified against the paper's Table 2.
Values match within rounding except where noted:

- **Exact match (Illustration, Setting):** proportion of predictions equal to the
  human label. Setting drops the rare multi-value human rows and `NA`.
- **Jaccard (Characters, Objects):** mean over pages of |intersection|/|union| of
  label sets. **`None` and `NA` are kept as literal labels** (agreement on
  "no characters/objects" is meaningful); this convention reproduces the paper
  (dropping them inflates Jaccard by ≈0.09).
- **Actions micro-F1:** TP/FP/FN pooled across images for the queried entity's
  action set. Reproduces the paper to ±0.01.
- **Intensity distance:** mean |model − human| on the 1–5 scale. When annotators
  disagreed, the consensus file records **all** distinct ratings for an image
  (69% of images have a single rating; 31% list ≥2). The human value is the
  **mean of those ratings** (the intended rule). NB: the paper's original Table 2
  intensity column was computed slightly differently and reads ≈0.1 high; the
  mean-based (reproducible) values are lower across all models — update the
  revised Table 2 accordingly.
- The paper's Table 2 **Intensity human value of 0.98 is a typo**; the correct
  human ordinal distance is **0.67** (see `Agreement_Table.csv`). Confirm this
  agreement-table value uses the same mean-based collapse for a like-for-like
  human baseline.

## Software / environment

- Python ≥ 3.8 (standard library only for `02_table2_metrics.py`).
- R ≥ 4.0 with `jsonlite`, `dplyr`, `stringr`, `tidyr`, `ggplot2`, `rstatix`.
- Model/API versions and dates are listed in `prompts/prompts.md`. Proprietary
  models may change over time; the raw outputs in `data/model_outputs/` are the
  frozen responses used in the paper.
