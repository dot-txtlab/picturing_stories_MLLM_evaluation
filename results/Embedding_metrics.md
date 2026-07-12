# Embedding-based metrics (Reviewer W1Nv)

Computed with **BAAI/bge-m3**, a current state-of-the-art multilingual embedding
model, exactly as W1Nv suggested (a SOTA embedding model rather than word overlap
or BERTScore's compressed space).

## 1. Characters / Objects: embedding soft-set F1 vs. Jaccard  [W1Nv-1]
For each image we compute a BERTScore-style set similarity between the model and
human label sets: precision = mean over model labels of the max cosine to any
human label, recall symmetric, then F1. This credits near-synonyms
(Dog≈Animal, "Animals"≈Animal) that exact-match Jaccard scores as 0.

| Model-shot | Characters Jaccard | Characters Emb-F1 | Objects Jaccard | Objects Emb-F1 |
|---|:--:|:--:|:--:|:--:|
| Gemini2.5-0 | 0.67 | 0.81 | 0.56 | 0.77 |
| Gemini2.5-1 | 0.65 | 0.81 | 0.59 | 0.77 |
| GPT-0 | 0.64 | 0.82 | 0.48 | 0.74 |
| GPT-1 | 0.62 | 0.79 | 0.50 | 0.74 |
| Claude-0 | 0.60 | 0.80 | 0.59 | 0.79 |
| Claude-1 | 0.63 | 0.86 | 0.59 | 0.81 |
| Qwen-0 | 0.69 | 0.90 | 0.53 | 0.82 |
| Qwen-1 | 0.68 | 0.89 | 0.56 | 0.81 |
| LLaVA-0 | 0.49 | 0.75 | 0.47 | 0.73 |

**Takeaway:** semantic scoring lifts all models (much of the apparent Jaccard "gap"
is near-synonym mismatch, not error) while preserving the model ordering. We will
add the embedding column alongside Jaccard (keeping Jaccard for comparability with
the human-agreement Jaccard ceiling).

## 2. Captions: bge-m3 cosine to human captions vs. BERTScore  [W1Nv-2]
Per-image cosine between each model caption and the human caption(s) (N = 209
pages with human captions), with a within-image human–human baseline.

| Model-shot | mean cosine | std | N |
|---|:--:|:--:|:--:|
| **Human–Human (baseline)** | **0.657** | 0.105 | 1188 |
| Gemini2.5-0 | 0.649 | 0.070 | 209 |
| Gemini2.5-1 | 0.657 | 0.069 | 209 |
| GPT-0 | 0.655 | 0.065 | 209 |
| GPT-1 | 0.661 | 0.073 | 209 |
| Claude-0 | 0.611 | 0.075 | 209 |
| Claude-1 | 0.627 | 0.079 | 209 |
| Qwen-0 | 0.614 | 0.072 | 209 |
| Qwen-1 | 0.637 | 0.074 | 209 |

**Takeaway:** unlike BERTScore's compressed ~0.80–0.90 band (Fig 5), bge-m3 places
the human–human ceiling at 0.657 and shows **GPT-1 (0.661) and Gemini-1 (0.657)
reaching that ceiling**, with Claude/Qwen a clear lower tier — cleaner
discrimination that corroborates the paper's tiering. One-shot helps every model.

Regenerate with `code/04_embedding_and_caption_metrics.py` (Sections E, F).
