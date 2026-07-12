# Category-level bias tests with Benjamini–Hochberg correction

Fisher exact tests per category (Gemini zero-shot; characters/objects on N = 890
illustration-present pages), with FDR (Benjamini–Hochberg) correction across the
categories within each task. `NA` (missing human annotation) is excluded.
*** = survives correction at FDR 0.05.

## Characters (9 categories)
| Category | OR | p (raw) | p (BH) | Survives |
|---|:--:|:--:|:--:|:--:|
| Other | 0.20 | .000 | **.000** | *** |
| Woman | 0.80 | .020 | .065 | — (marginal) |
| Mythical / Imaginary Being | 1.60 | .022 | .065 | — (marginal) |
| Boy | 1.25 | .031 | .070 | — (marginal) |
| Man | 0.85 | .042 | .075 | — (marginal) |
| Animal | 1.12 | .188 | .247 | — |
| None | 1.35 | .192 | .247 | — |
| Girl | 1.11 | .342 | .385 | — |
| Animate Object | 1.27 | .503 | .503 | — |

**Honest revision:** after correction, the character-level gender/type biases
(boys over-, women/men under-represented) are **marginal, not significant**
(p_BH ≈ .065–.075). We will soften these from "significant biases" to "suggestive
tendencies" and note they do not survive multiple-comparison correction. (The
strongly-significant "Other" reflects models using the catch-all label far less
than annotators — a label-usage difference, not a content bias.)

## Objects (8 categories)
| Category | OR | p (raw) | p (BH) | Survives |
|---|:--:|:--:|:--:|:--:|
| None | 0.11 | .000 | **.000** | *** |
| Toys | 2.97 | .000 | **.001** | *** |
| Household items and tools | 1.34 | .001 | **.003** | *** |
| Architecture | 0.80 | .005 | **.011** | *** |
| Reading and Art | 1.43 | .026 | **.042** | *** |
| Nature | 0.92 | .278 | .371 | — |
| Vehicles | 1.17 | .404 | .461 | — |
| Other | 1.11 | .534 | .534 | — |

**Robust:** object over-representation of Toys, Household items, Reading/Art and
under-representation of Architecture all survive correction (as claimed).

## Actions (21 categories)
Survive BH correction (p_BH < .05): **over** — LOOKING (1.94), TALKING (2.52),
WORKING (2.40), GIVING (3.08), GESTURING (1.39), PLAYING (1.80); **under** —
STANDING (0.45), SITTING (0.47), SLEEPING (0.32). All other action categories are
non-significant after correction. This supports the paper's Actions claims
(over-predicting active/social states, under-predicting passive states).

Regenerate with `code/03_rebuttal_analyses.py` (Section C).
