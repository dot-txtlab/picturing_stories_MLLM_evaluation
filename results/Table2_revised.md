# Revised Table 2 (drop-in replacement)

Two changes vs. the submitted Table 2:
1. **Intensity Distance** column corrected to the intended mean-based rule (when
   annotators disagreed, the human value is the mean of their ratings). The
   submitted column read ≈0.1 high across all rows; the corrected values are
   lower (models are *closer* to human ratings than originally reported).
2. **Human baseline** is now shown as an explicit **agreement ceiling** with two
   rows — *full* inter-annotator agreement and *majority-vote* agreement — rather
   than a single row that mixed conventions. The submitted Intensity human value
   of 0.98 was a typo (correct: 0.67).

| Model | Illustration Exact-Match % | Setting Exact-Match % | Characters Jaccard (M) | Objects Jaccard (M) | Intensity Distance (M) ↓ | Actions Micro-F1 |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|
| **Human (full agreement)** | 85.4 | 75.3 | 0.78 | 0.56 | **0.67** | 0.44 |
| **Human (majority agreement)** | — | 95.5 | — | — | — | 0.53 |
| Claude-0 | 97.6 | 83.7 | 0.60 | 0.59 | **0.87** | 0.57 |
| Claude-1 | 97.9 | 84.4 | 0.63 | 0.59 | **0.87** | 0.57 |
| Gemini2.5-0 | 96.8 | **88.1** | **0.67** | 0.56 | **0.88** | 0.57 |
| Gemini2.5-1 | 98.0 | 87.3 | 0.65 | 0.59 | **0.95** | 0.62 |
| GPT-0 | 97.6 | 85.4 | 0.64 | 0.48 | **0.81** | 0.61 |
| GPT-1 | 98.0 | 85.0 | 0.62 | 0.50 | **0.82** | 0.62 |
| Qwen-0 | 97.8 | 83.0 | **0.69** | 0.53 | **0.83** | 0.49 |
| Qwen-1 | 97.6 | 83.2 | 0.68 | 0.56 | **0.79** | 0.52 |
| LLaVA-0 | 89.0 | 78.8 | 0.49 | 0.47 | **0.91** | 0.35 |

Notes:
- ↓ = lower is better (mean absolute distance on the 1–5 scale).
- The two human rows are **agreement ceilings**, not competitor scores: model
  cells are computed against the human majority/consensus label, whereas the
  human rows report agreement *among* annotators. Models should be read as
  *approaching* this ceiling, not "beating humans."
- Regenerate with `code/02_table2_metrics.py` (metrics) and the intensity /
  human-row logic in `code/03_rebuttal_analyses.py` (Section A).
