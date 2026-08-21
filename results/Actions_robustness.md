# Actions task — pipeline facts and n=1 robustness

## Entity-selection facts (Gemini zero-shot, N = 995 images)
- **One action query was issued per image** (995 images = 995 queries).
- The queried `<ENTITY_TYPE>` was always one the humans had annotated as present:
  **993/995** queried entities appear in the human annotation (the 2 misses are
  images with no parsed human entity block).
- Instance counts of the queried entity in the human data: **n=1 for 967 (97.4%)**,
  n=2 for 20, n=3 for 6. The prompt's "exactly ONE such entity" reflects this
  selection rule (entities annotated as singletons).

## Robustness: micro-F1 on all queried entities vs. the n=1 subset
Dropping the 2.6% of images where the queried entity had >1 instance changes
nothing (differences ≤ 0.002 F1):

| Model-shot | F1 (all) | N (all) | F1 (n=1 only) | N (n=1) |
|---|:--:|:--:|:--:|:--:|
| Gemini2.5-0 | 0.572 | 993 | 0.574 | 967 |
| Gemini2.5-1 | 0.620 | 993 | 0.622 | 967 |
| GPT-0 | 0.607 | 992 | 0.609 | 966 |
| GPT-1 | 0.618 | 993 | 0.620 | 967 |
| Claude-0 | 0.573 | 988 | 0.573 | 962 |
| Claude-1 | 0.573 | 991 | 0.575 | 965 |
| Qwen-0 | 0.487 | 998 | 0.488 | 972 |
| Qwen-1 | 0.516 | 993 | 0.518 | 967 |
| LLaVA-0 | 0.349 | 993 | 0.349 | 967 |

**Takeaway:** the multi-instance cases do not drive any result. The camera-ready
Table 2 reports the `n=1` scores, while the all-query scores above are retained
as a robustness check. The precise selection protocol is documented in the
paper's Appendix B.2.

Regenerate with `code/03_rebuttal_analyses.py` (Section B).
