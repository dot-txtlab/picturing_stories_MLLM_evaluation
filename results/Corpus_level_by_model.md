# Corpus-level (aggregate) agreement — all five models

Reviewer CMEQ noted the aggregate-alignment result (RQ2) was demonstrated only for
Gemini zero-shot. We replicate it for every model. For each categorical task we
correlate model vs. human **category proportions** across the corpus (Pearson r)
and report mean absolute difference (MAD); emotional intensity is the image-level
Pearson r of numeric ratings.

| Model (zero-shot) | Characters r | Char MAD | Objects r | Obj MAD | Setting r | Intensity r |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| Gemini2.5 | 0.95 | 0.023 | 0.98 | 0.023 | 0.99 | 0.67 |
| GPT | 0.96 | 0.021 | 0.71 | 0.050 | 0.99 | 0.65 |
| Claude | 0.94 | 0.021 | 0.99 | 0.015 | 0.97 | 0.64 |
| Qwen | 0.96 | 0.023 | 0.91 | 0.041 | 0.94 | 0.58 |
| LLaVA | 0.87 | 0.031 | 0.94 | 0.032 | 0.90 | 0.15 |

**Takeaways for a more calibrated claim:**
- Corpus-level alignment for **characters and settings is a general property of
  frontier models** (r ≥ 0.94), not a Gemini artifact.
- It is **not uniform**: GPT's object distribution diverges (r = 0.71), and the
  weakest model (LLaVA) drops on characters and collapses on intensity (r = 0.15).
- **Emotional intensity is the consistent weak point** (r = 0.58–0.67 for frontier
  models, 0.15 for LLaVA), reinforcing that aggregate recovery is strong for
  concrete visual categories but only moderate for subjective ones.
- This supports the *modest* framing CMEQ requested: "some aggregate statistics can
  be reliably recovered (concrete categories), while subjective distributions are
  recovered only approximately," rather than a blanket reliability claim.

(These r-values differ slightly from the submitted RQ2 text because `NA` is now
excluded and proportions use the cleaned label set; the pattern is unchanged.)

Regenerate with `code/03_rebuttal_analyses.py` (Section D).
