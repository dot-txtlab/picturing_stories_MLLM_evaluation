# Caption factual-validation inter-annotator agreement (Reviewer CMEQ)

The factual-validation task (Prolific) asked annotators to count hallucinated and
missing items (0, 1, 2, 3, 4+, or "All") per caption. Every caption instance
(page × model × prompt) was rated by ≥2 annotators (mostly 3); N = 2,950 instances.

| Measure | Hallucinations | Missing |
|---|:--:|:--:|
| Base rate (count == 0) | 58% | 65% |
| Mean pairwise \|difference\| (0–5 scale) | 0.93 | 0.83 |
| Binary "error present?" — unanimous | 45% | 43% |
| Binary "error present?" — **majority (>half) agree** | **95%** | **95%** |
| Krippendorff's α (ordinal counts) | 0.049 | 0.017 |

**How to report this honestly:**
- The **fine-grained count is heavily skewed toward 0** (58–65% of ratings), which
  deflates chance-corrected α (the well-known "α paradox": low variance → low α
  even when raw disagreement is small, here <1 scale point on average).
- The **binary "is there an error?" decision — the unit Table 3 actually uses — has
  95% majority agreement**, i.e., annotators reliably agree on presence/absence.
- **Recommended revision:** (a) add these reliability statistics to §4.2.2; (b) frame
  Table 3 around the reliable binary/aggregate quantities; (c) treat exact error
  counts as noisier and interpret them only in aggregate across annotators.

Regenerate with `code/04_embedding_and_caption_metrics.py` (Section G).
