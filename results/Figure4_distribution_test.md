# Figure 4 — distributional tests for the emotional-intensity skew

Replaces the purely descriptive treatment of Figure 4 with formal tests
(Gemini and other models, zero-shot). Two paired quantities per image: the model's
integer rating and the mean of the human ratings. Tests: Wilcoxon signed-rank
(paired location), matched-pairs rank-biserial effect size, two-sample
Kolmogorov–Smirnov (distribution shape, on pooled ratings), Wasserstein (earth-mover)
distance, and skewness of each distribution.

| Model (0-shot) | P(model≤2) | P(human≤2) | Wilcoxon p | rank-biserial r | KS p | Wasserstein | skew model / human |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Gemini2.5 | 0.64 | 0.41 | 1.9e-56 | −0.73 | 2.1e-45 | 0.74 | 0.86 / 0.07 |
| GPT | 0.75 | 0.41 | 1.4e-63 | −0.77 | 2.3e-70 | 0.72 | 0.94 / 0.07 |
| Claude | 0.74 | 0.41 | 3.6e-72 | −0.81 | 3.7e-65 | 0.79 | 0.80 / 0.07 |
| Qwen | 0.65 | 0.41 | 3.5e-38 | −0.59 | 2.8e-38 | 0.62 | 0.80 / 0.07 |
| LLaVA | 0.01 | 0.41 | 1.5e-07 | +0.23 | 6.6e-69 | 0.92 | −2.38 / 0.07 |

**Rating-level distribution (Gemini zero-shot), P(level):**

| Level | 1 | 2 | 3 | 4 | 5 |
|---|:--:|:--:|:--:|:--:|:--:|
| Model | 0.51 | 0.17 | 0.14 | 0.14 | 0.05 |
| Human | 0.21 | 0.20 | 0.29 | 0.21 | 0.10 |

**Findings:**
- Frontier models rate emotional intensity **significantly lower** than the human
  mean (Wilcoxon signed-rank p < 1e-37; large negative rank-biserial r = −0.59 to
  −0.81) and the two rating distributions **differ in shape** (KS p < 1e-37).
- The model distribution is strongly right-skewed toward low arousal
  (skew ≈ 0.8–0.9) whereas the human distribution is near-symmetric (skew ≈ 0.07),
  clustering around the mid-point (human P(3)=0.29 vs model P(3)=0.14; model
  P(1)=0.51 vs human P(1)=0.21). This is the effect Figure 4 shows.
- Nuance worth adding: the weakest model, **LLaVA, fails in the opposite direction**
  (over-selecting high intensity; skew −2.38, positive rank-biserial), i.e., the
  divergence is systematic but not identical across models.

Regenerate with `code/03_rebuttal_analyses.py` (Section H).
