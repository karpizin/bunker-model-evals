# Bunker Benchmark v3 — public result bundle (2026-10-27)

Publication ID: `bunker-v3-public-results-20261027`  
Published: `2026-10-27T15:10:00+03:00`

This bundle contains **42 included result files** and **3 explicitly excluded audit files**. It preserves every complete recent cohort collected for this publication; superseded or non-comparable runs are retained under `excluded/` and never enter the ranking.

`v3` scores below are the immutable scores stored by the original runner. The companion v3.1 report re-evaluates the same answers with the versioned semantic rubric. Effective completion tokens/s is completion tokens divided by end-to-end case latency; it is not raw llama.cpp generation throughput.

## Included cohorts

| Model configuration | Runs | v3 mean | Range | Critical failures | Eligible | Mean latency | Effective tok/s |
|---|---:|---:|---:|---:|---:|---:|---:|
| `Qwen3.8-27B-UD-Q6_K_M-MTP` | 5 | 94.09% | 93.62–94.57% | 1 | 0/5 | 197.82 s | 17.48 |
| `Qwen3.8-27B-Q8_0-MTP` | 5 | 93.80% | 92.68–94.33% | 1–2 | 0/5 | 229.32 s | 15.22 |
| `MiMo-V2.6-Flash-MOPD-full-Q3_K` | 1 | 93.14% | 93.14% | 4 | 0/1 | 15757.48 s | 0.30 |
| `gemma-4-31B-it-Q6_K` | 5 | 92.84% | 92.33–93.61% | 2–3 | 0/5 | 474.77 s | 7.16 |
| `gemma-4-31B-it-Q8_0` | 5 | 92.84% | 92.33–93.00% | 2–3 | 0/5 | 559.36 s | 5.96 |
| `gemma-4-31B-it-Q5_K_M` | 5 | 92.64% | 92.39–93.06% | 2 | 0/5 | 404.00 s | 8.14 |
| `gemma-4-31B-it-Q4_K_M` | 5 | 91.62% | 91.11–92.32% | 2–3 | 0/5 | 346.08 s | 9.21 |
| `gemma-4-31B-it-uncensored-heretic-Q8_0` | 5 | 91.38% | 91.38% | 3 | 0/5 | 543.56 s | 5.94 |
| `Qwen3.6-27B-UD-IQ3_XXS-MTP` | 5 | 90.94% | 89.90–91.93% | 2–3 | 0/5 | 180.03 s | 20.08 |
| `gemma-4-31B-it-uncensored-heretic-Q6_K` | 5 | 90.82% | 90.54–91.38% | 3 | 0/5 | 449.81 s | 7.19 |
| `Qwen3.8-27B-UD-IQ3_XXS` | 5 | 90.82% | 90.29–91.11% | 4–5 | 0/5 | 221.54 s | 13.85 |
| `gemma-4-31B-it-uncensored-heretic-Q4_K_M` | 5 | 90.71% | 90.59–91.21% | 3–4 | 0/5 | 355.31 s | 9.17 |
| `Qwen3.8-27B-Q4_K_M` | 5 | 90.31% | 90.12–90.58% | 4 | 0/5 | 343.39 s | 9.86 |
| `Qwen3.6-27B-Q4_K_M-MTP` | 5 | 89.31% | 88.90–89.55% | 4–5 | 0/5 | 190.78 s | 18.03 |
| `Qwen3.8-27B-Uncensored-Q6_K-MTP` | 5 | 89.21% | 88.80–89.40% | 7 | 0/5 | 188.84 s | 17.62 |
| `Qwen3.8-27B-IQ2_M` | 5 | 88.29% | 87.71–89.81% | 4–6 | 0/5 | 209.68 s | 13.45 |
| `gemma-4-26B-A4B-it-UD-Q5_K_M` | 5 | 88.18% | 87.75–88.65% | 4–5 | 0/5 | 88.73 s | 40.88 |
| `Qwen3.6-27B-UD-IQ2_M` | 5 | 88.00% | 86.77–89.23% | 4–7 | 0/5 | 243.95 s | 13.50 |
| `Qwen3.6-27B-Q4_K_M` | 5 | 87.82% | 86.51–89.27% | 4–7 | 0/5 | 312.94 s | 10.86 |
| `gemma-4-26B-A4B-it-UD-Q4_K_M` | 1 | 86.87% | 86.87% | 7 | 0/1 | 80.98 s | 41.69 |
| `gemma-4-26B-A4B-it-UD-Q3_K_M` | 1 | 86.70% | 86.70% | 5 | 0/1 | 77.34 s | 45.46 |
| `gemma-4-E4B-it-Q6_K` | 5 | 86.34% | 85.86–86.79% | 6–7 | 0/5 | 80.49 s | 43.26 |
| `gemma-4-E4B-it-Q4_K_M` | 1 | 85.86% | 85.86% | 9 | 0/1 | 71.69 s | 52.47 |
| `gemma-4-E4B-it-Q8_0` | 5 | 84.59% | 83.32–85.53% | 8–9 | 0/5 | 91.08 s | 36.87 |
| `Huihui-Qwen3.6-35B-A3B-abliterated-Q4_K-MTP` | 1 | 84.57% | 84.57% | 9 | 0/1 | 54.30 s | 65.51 |
| `Huihui-Qwen3.6-35B-A3B-abliterated-Q6_K-MTP` | 5 | 84.28% | 83.46–86.00% | 8–9 | 0/5 | 51.94 s | 65.80 |
| `Qwen3.6-35B-A3B-Uncensored-Q3_K_P` | 5 | 84.14% | 82.93–85.35% | 7–9 | 0/5 | 57.88 s | 63.06 |
| `Huihui-Qwen3.6-35B-A3B-abliterated-Q8_0-MTP` | 1 | 84.08% | 84.08% | 9 | 0/1 | 62.78 s | 56.38 |
| `Qwen3.5-9B-Q5_K_M` | 1 | 84.02% | 84.02% | 7 | 0/1 | 110.81 s | 29.10 |
| `Qwen3.6-35B-A3B-Uncensored-Q6_K_P` | 1 | 84.02% | 84.02% | 8 | 0/1 | 75.42 s | 48.02 |
| `Qwen3.6-35B-A3B-UD-Q4_K_M` | 1 | 83.94% | 83.94% | 8 | 0/1 | 73.43 s | 49.95 |
| `Qwen3-14B-Q4_K_M` | 1 | 83.79% | 83.79% | 9 | 0/1 | 140.61 s | 22.02 |
| `Nanbeige4.3-33B-Q4_K_M` | 1 | 82.72% | 82.72% | 12 | 0/1 | 532.91 s | 10.13 |
| `Qwen3.6-35B-A3B-Uncensored-Q8_K_P` | 5 | 82.14% | 81.63–82.52% | 8–10 | 0/5 | 90.37 s | 40.14 |
| `Qwen3.6-35B-A3B-Uncensored-Q8_K_P` | 1 | 81.81% | 81.81% | 10 | 0/1 | 97.75 s | 37.05 |
| `Qwen3.6-35B-A3B-UD-Q5_K_M-MTP` | 1 | 81.33% | 81.33% | 10 | 0/1 | 61.61 s | 56.94 |
| `Qwen3.6-35B-A3B-UD-Q6_K-MTP` | 1 | 80.66% | 80.66% | 12 | 0/1 | 65.05 s | 56.62 |
| `Flint-Q4_K_M` | 1 | 76.24% | 76.24% | 16 | 0/1 | 75.29 s | 48.06 |
| `Spark-X2.6-4B-Q5_K_M` | 1 | 75.38% | 75.38% | 15 | 0/1 | 74.82 s | 51.70 |
| `Qwen3.6-27B-Abliterated-Q4_K_M-MTP` | 1 | 70.24% | 70.24% | 24 | 0/1 | 193.17 s | 18.24 |
| `YandexGPT-5-Lite-8B-Instruct-Q4_K_M` | 5 | 66.78% | 66.78% | 20 | 0/5 | 52.60 s | 41.85 |
| `GigaChat3.1-10B-A1.8B-Q6_K` | 5 | 61.73% | 58.93–65.15% | 24–28 | 0/5 | 22.78 s | 84.38 |

## Excluded but retained

- `Spark-X2.6-4B-Q5_K_M` — Pre-pinned-runtime diagnostic. The fd8f845 cohort is the comparable published Spark result.
- `gemma-4-31B-it-Q8_0` — Superseded: the sparse aria2 artifact exposed its final logical size before all data blocks were complete. Use the complete-redownload cohort.
- `gemma-4-E4B-it-Q6_K` — Superseded by the verified complete-redownload control. Retained only as excluded audit evidence.

## Files

- `manifest.json` — source and published hashes, inclusion decision, and per-file summary.
- `summary.csv` — compact included-result table.
- `included/` — sanitized complete raw runner outputs used for comparison.
- `excluded/` — sanitized raw outputs retained for audit but omitted from rankings.

Machine-local paths and private network addresses are redacted. Model answers, scores, traces, usage, and timings are otherwise preserved.
