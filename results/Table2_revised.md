# Revised Table 2 (two-panel replacement)

The submitted table mixed model-versus-consensus metrics with several different
human inter-annotator agreement measures in the same rows. The revision separates
them into two panels. Panel A contains only model scores computed against the
human majority/consensus annotation. Panel B reports human agreement in each
measure's native units; these values are interpretive references, not competitor
scores.

The revision also:

1. corrects the Intensity Distance column to the intended mean-based rule (when
   annotators disagreed, the target is the mean of their ratings);
2. corrects the submitted human ordinal-distance value from 0.98 to 0.67; and
3. reports Actions micro-F1 on the singleton-only (`n=1`) entity subset.

## Panel A: Model performance against human consensus annotations

| Model | Illustration Exact-Match % | Setting Exact-Match % | Characters Jaccard (M) | Objects Jaccard (M) | Intensity Distance (M) ↓ | Actions Micro-F1 (n=1) |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|
| Claude-0 | 97.6 | 83.7 | 0.60 | **0.59** | 0.87 | 0.57 |
| Claude-1 | 97.9 | 84.4 | 0.63 | **0.59** | 0.87 | 0.58 |
| Gemini2.5-0 | 96.8 | **88.1** | 0.67 | 0.56 | 0.88 | 0.57 |
| Gemini2.5-1 | **98.0** | 87.3 | 0.65 | **0.59** | 0.95 | **0.62** |
| GPT-0 | 97.6 | 85.4 | 0.64 | 0.48 | 0.81 | 0.61 |
| GPT-1 | **98.0** | 85.0 | 0.62 | 0.50 | 0.82 | **0.62** |
| Qwen-0 | 97.8 | 83.0 | **0.69** | 0.53 | 0.83 | 0.49 |
| Qwen-1 | 97.6 | 83.2 | 0.68 | 0.56 | **0.79** | 0.52 |
| LLaVA-0 | 89.0 | 78.8 | 0.49 | 0.47 | 0.91 | 0.35 |

## Panel B: Human inter-annotator agreement

| Task | Full Agreement % | Majority Agreement % | Jaccard | Ordinal Distance ↓ |
|------|:--:|:--:|:--:|:--:|
| Illustration | 85.4 | — | — | — |
| Characters | 52.5 | 72.9 | 0.78 | — |
| Setting | 75.3 | 95.5 | — | — |
| Objects | 33.7 | 60.8 | 0.56 | — |
| Emotional intensity | 15.3 | 68.9 | — | 0.67 |
| Actions | 24.7 | 52.9 | 0.44 | — |

### Notes

- In Panel A, model cells are computed against the human majority-vote or
  consensus annotation. Suffixes `0` and `1` denote zero-shot and one-shot
  prompting, respectively.
- Intensity is mean absolute distance from the mean human rating on the 1–5
  scale; lower values indicate closer agreement.
- Actions are evaluated with micro-averaged F1 after restricting to queried
  entity types with exactly one instance in the human annotation.
- Panel B describes agreement among human annotators. Its Jaccard and ordinal
  distance values are not placed under model columns that use different metrics.
- The camera-ready LaTeX version is `results/Table2_two_panel.tex`.
- Regenerate the model metrics with
  `cd code && python 02_table2_metrics.py --actions-n1 --csv ../results/Table2_model_metrics.csv`.
