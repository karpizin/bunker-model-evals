# Bunker Benchmark v3: hosted baseline

Date: 2026-10-18

Provider: OpenRouter

Protocol: one run per model, `temperature=0.05`, `max_tokens=8192`,
`case_timeout=600`. Gemini used the minimum currently supported reasoning
profile `low`; DeepSeek and GPT used `none`. Provider reasoning was excluded
from visible responses.

This is a single-run calibration baseline, not a final repeated-run ranking.
The same 20-case corpus and deterministic scorer were used for the local small
and medium model pilot.

## Results

| Rank | Model | Capability | Critical failures | Truncated | Total latency | Average case | Effective completion rate |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Gemini 3.8 Flash | 93.01% | 2 | 0 | 167.26 s | 8.36 s | 23.11 tok/s |
| 2 | DeepSeek V4 Flash | 89.51% | 5 | 0 | 309.86 s | 15.49 s | 9.14 tok/s |
| 3 | GPT-5.4 Nano | 83.35% | 9 | 0 | 59.33 s | 2.97 s | 89.93 tok/s |

The effective completion rate divides completion tokens by full request
latency. It includes prompt processing, provider scheduling and multi-step
tool turns, and therefore is not raw generation speed or TTFT.

## Track scores

| Model | Synthesis | Agent execution | Result validation | Grounded RAG | Code and operations |
|---|---:|---:|---:|---:|---:|
| Gemini 3.8 Flash | 93.59% | 94.80% | 96.74% | 94.44% | 85.47% |
| DeepSeek V4 Flash | 98.46% | 79.49% | 92.39% | 94.44% | 82.79% |
| GPT-5.4 Nano | 85.59% | 91.80% | 69.83% | 94.44% | 75.08% |

## Comparison with the local pilot

| Model | Execution | Capability | Critical failures | Total latency |
|---|---|---:|---:|---:|
| Gemini 3.8 Flash | OpenRouter | 93.01% | 2 | 167.26 s |
| Qwen3.8-27B-Q4_K_M | AMD Ryzen AI Max+ 395 | 90.49% | 4 | 344.05 s |
| DeepSeek V4 Flash | OpenRouter | 89.51% | 5 | 309.86 s |
| Qwen3-14B-Q4_K_M | AMD Ryzen AI Max+ 395 | 85.86% | 7 | 135.65 s |
| Qwen3.5-9B-Q5_K_M | AMD Ryzen AI Max+ 395 | 85.57% | 7 | 104.38 s |
| GPT-5.4 Nano | OpenRouter | 83.35% | 9 | 59.33 s |
| Qwen3.5-4B-Q5_K_M | AMD Ryzen AI Max+ 395 | 78.21% | 12 | 65.51 s |
| Phi-4-mini-instruct-Q5_K_M | AMD Ryzen AI Max+ 395 | 67.22% | 16 | 38.61 s |

## Critical findings

Gemini was the strongest and most even candidate. Its remaining blockers were
cross-tenant disclosure in the tenant-isolation case and an incomplete safe
rollback sequence. It passed stale-data refresh, exact-evidence RAG, path
traversal mitigation and the top-three search fusion case.

DeepSeek led synthesis but was less stable in orchestration. It missed one
tool in the weather-and-route case, chose or fused the wrong tools in the
top-three search case, relied on stale weather data and produced an incomplete
rollback sequence. The top-three search smoke scored 84.6%, while the full run
scored 38.5% on the same case, so a repeated run is required before drawing a
strong conclusion about its agent quality.

GPT was the clear latency leader and handled grounded RAG well, but failed
more production-critical validation checks. The main gaps were noisy
transcript decisions, stale-data handling, stopping after a successful tool
result, conflict resolution, path traversal and rollback safety.

No response hit the token ceiling. The strict production gate marks all three
runs ineligible because every candidate had at least one critical failure.

## Next step

Repeat Gemini and DeepSeek three times. Gemini needs variance confirmation at
the top of the ranking; DeepSeek needs a repeat specifically because the
smoke/full-run disagreement indicates high orchestration variance. GPT Nano is
already sufficiently characterized as a fast, inexpensive fallback rather
than a quality reference.

Raw reports and checkpoints are stored in
`docs/benchmarks/runs/bunker-benchmark-v3-hosted-20261018/`.
