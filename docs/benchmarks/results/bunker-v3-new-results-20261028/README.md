# Bunker Benchmark v3 — public result bundle (2026-10-28)

Publication ID: `bunker-v3-new-results-20261028`  
Published: `2026-10-28T01:37:12+03:00`

This bundle contains **3 included result files** and **0 explicitly excluded audit files**. It preserves every complete recent cohort collected for this publication; superseded or non-comparable runs are retained under `excluded/` and never enter the ranking.

`v3` scores below are the immutable scores stored by the original runner. The companion v3.1 report re-evaluates the same answers with the versioned semantic rubric. Effective completion tokens/s is completion tokens divided by end-to-end case latency; it is not raw llama.cpp generation throughput.

## Included cohorts

| Model configuration | Runs | v3 mean | Range | Critical failures | Eligible | Mean latency | Effective tok/s |
|---|---:|---:|---:|---:|---:|---:|---:|
| `Ornith-1.5-122B-UD-IQ3_XXS-MTP` | 4 | 85.18% | 83.22–87.31% | 8–11 | 0/4 | 211.70 s | 25.02 |
| `NVIDIA-Nemotron-3.5-Bolt-74B-A9B-AD-IQ4_XS` | 3 | 80.89% | 80.63–81.40% | 28 | 0/3 | 191.61 s | 18.95 |
| `NVIDIA-Nemotron-3.5-Bolt-74B-A9B-UD-IQ2_M` | 4 | 78.44% | 76.27–80.03% | 28–31 | 0/4 | 150.66 s | 23.24 |

## Excluded but retained

No exclusions.

## Files

- `manifest.json` — source and published hashes, inclusion decision, and per-file summary.
- `summary.csv` — compact included-result table.
- `included/` — sanitized complete raw runner outputs used for comparison.
- `excluded/` — sanitized raw outputs retained for audit but omitted from rankings.

Machine-local paths and private network addresses are redacted. Model answers, scores, traces, usage, and timings are otherwise preserved.
