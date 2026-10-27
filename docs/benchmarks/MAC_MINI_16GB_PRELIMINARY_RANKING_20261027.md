# Preliminary model ranking for Mac mini 16 GB

Updated: `2026-10-27`

This document is a preliminary shortlist for a Mac mini with Apple M4 and
16 GB unified memory. It is not a new hardware benchmark. Quality scores come
from the canonical Bunker Benchmark v3.1 runs on AMD Ryzen AI Max+ 395, while
the size filter and operational recommendations target the 16 GB Mac mini.

## Selection rules

- Model weights must not exceed 12 GiB.
- The ranking is ordered by the representative v3.1 capability score.
- File size is not peak memory use. The runtime also needs memory for the
  KV cache, compute buffers, Metal, the operating system and Bunker AI.
- Models above roughly 10 GiB are therefore marked as constrained even when
  their weight file satisfies the 12 GiB filter.
- Latency below was measured on AMD/Vulkan and must not be interpreted as
  expected Mac mini latency.

## Preliminary ranking

| Rank | Model | Weight size | v3.1 | Runs | Critical failures | 16 GB assessment |
|---:|---|---:|---:|---:|---:|---|
| 1 | `Qwen3.8-27B-UD-IQ3_XXS` | about 11.4 GiB | **93.94%** | 5 | 2-3 | Maximum quality candidate; constrained to a short or quantized KV cache |
| 2 | `Qwen3.8-27B-IQ2_M` | about 10.1 GiB | **89.86%** | 5 | 4-6 | Better memory margin than IQ3; preferred Qwen candidate for first Mac validation |
| 3 | `Qwen3.6-27B-UD-IQ2_M` | 10.10 GiB | **89.78%** | 5 | 4-5 | Practical fallback if Qwen3.8 runtime compatibility is weaker |
| 4 | `gemma-4-E4B-it-Q6_K` | about 7.1 GB | **89.57%** | 5 | 4-5 | Comfortable fit; strong balance of quality and memory headroom |
| 5 | `gemma-4-26B-A4B-it-UD-Q3_K_M` | **11.67 GiB** | **89.56%** | 1 | 3 | Fits by file size only; tight runtime budget and limited context recommended |
| 6 | `gemma-4-E4B-it-Q4_K_M` | 4.64 GiB | **89.05%** | 1 | 6 | Best compact Gemma candidate; ample memory for context and services |
| 7 | `Qwen3.5-9B-Q5_K_M` | 6.13 GiB | **85.53%** | 1 | 7 | Balanced ordinary dense model with comfortable memory use |
| 8 | `Qwen3-8B-Q4_K_M` | about 4.7 GiB | **82.72%** | 1 | 10 | Compact general-purpose fallback |
| 9 | `Qwen3.5-4B-Q5_K_M` | 2.93 GiB | **80.92%** | 1 | 11 | Fast helper model for simple routing and transformations |
| 10 | `Qwen3-4B-Q5_K_M` | 2.69 GiB | **77.22%** | 1 | 16 | Lightweight, but materially weaker than Qwen3.5 4B |
| 11 | `gemma-4-E2B-it-Q4_K_M` | 2.89 GiB | **74.10%** | 1 | 18 | Very compact Gemma option; not suitable as the only assistant |
| 12 | `Phi-4-mini-instruct-Q5_K_M` | 2.65 GiB | **71.83%** | 1 | 13 | Small specialist/helper candidate |
| 13 | `gemma-3-12b-it-heretic-v2-Q4_K_M` | 6.80 GiB | **69.32%** | 1 | 19 | No quality advantage over newer compact candidates |
| 14 | `Llama-3.2-3B-Instruct-Q5_K_M` | about 2.3 GiB | **57.73%** | 1 | 29 | Emergency lightweight fallback only |

Differences below approximately one percentage point should not be treated as
meaningful without repeated runs. In particular, positions 4 and 5 differ by
only 0.01 percentage point.

## Gemma 4 26B lower-quant candidates

The Mac mini already has an Ollama model named `bunker-gemma26` with a
9.29 GiB model blob. Its original quant label is not preserved by the Ollama
manifest. File size, tensor types and the historical inventory indicate that
it is most likely the `UD-IQ2_M` build, but this identification is not yet
considered definitive.

| Variant | Approximate size | Existing evidence | Status |
|---|---:|---|---|
| `gemma-4-26B-A4B-it-UD-IQ1_M` | about 9.9 GB | April smoke passed; 33.80 generated tok/s | No v3.1 score |
| `gemma-4-26B-A4B-it-UD-IQ2_M` | about 10.0 GB | April smoke passed; 32.42 generated tok/s | Likely installed as `bunker-gemma26`; no v3.1 score |
| `gemma-4-26B-A4B-it-UD-IQ3_S` | about 11.2 GB | April run produced compute errors | Do not recommend before runtime retest |
| `gemma-4-26B-A4B-it-UD-Q3_K_M` | 11.67 GiB | v3.1 89.56%; one complete run | Ranked, but memory-constrained |

The IQ1/IQ2 smoke results are useful readiness evidence, not quality scores and
must not be compared numerically with Bunker Benchmark v3.1.

## Current recommendation

1. Use `Qwen3.8-27B-IQ2_M` as the first high-capability candidate if a native
   Mac run confirms stable loading with the required context.
2. Use `gemma-4-E4B-it-Q6_K` as the balanced default when Bunker AI services
   run on the same 16 GB machine.
3. Keep `gemma-4-E4B-it-Q4_K_M` as the compact operational fallback.
4. Treat `Qwen3.8 IQ3` and `Gemma 4 26B Q3` as maximum-quality experiments,
   not safe defaults, until peak-memory and context tests are complete.
5. Run v3.1 directly on the installed `bunker-gemma26` before assigning it a
   position in this ranking.

## Sources

- [`BUNKER_BENCHMARK_V3_1_RESCORE_20261027.md`](BUNKER_BENCHMARK_V3_1_RESCORE_20261027.md)
- [`mac_mini_model_quality_smoke_2026-04-11.json`](mac_mini_model_quality_smoke_2026-04-11.json)
- [`mac_mini_model_speed_2026-04-11.json`](mac_mini_model_speed_2026-04-11.json)
- [`model-comparison-20260518/combined_summary.csv`](model-comparison-20260518/combined_summary.csv)

