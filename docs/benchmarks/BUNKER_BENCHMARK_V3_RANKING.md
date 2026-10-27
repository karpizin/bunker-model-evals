# Bunker Benchmark v3: unified ranking

Updated: 2026-10-26

The table combines runs that use the same 20-case v3 corpus, deterministic
scorer, `temperature=0.05`, `max_tokens=8192`, `case_timeout=600` and one
measured run per model. Capability and runtime are reported independently. A
model is production eligible only when it has no critical failures.

## Current ranking

| Rank | Model | Execution | Capability | Critical failures | Truncated | Total latency | Effective completion rate |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Qwen3.8-27B-UD-Q6_K_M-MTP | AMD 395+ / Vulkan+MTP | 94.57% | 1 | 0 | 191.48 s | 18.09 tok/s |
| 2 | Gemini 3.8 Flash | OpenRouter | 93.01% | 2 | 0 | 167.26 s | 23.11 tok/s |
| 3 | gemma-4-31B-it-Q4_K_M | AMD 395+ / Vulkan | 91.76% | 2 | 0 | 339.76 s | 9.38 tok/s |
| 4 | Qwen3.8-27B-Q4_K_M | AMD 395+ / Vulkan | 90.49% | 4 | 0 | 344.05 s | 9.93 tok/s |
| 5 | Qwen3.6-27B-UD-IQ3_XXS-MTP | AMD 395+ / Vulkan+MTP | 89.90% | 3 | 0 | 179.20 s | 20.17 tok/s |
| 6 | Qwen3.6-27B-Q4_K_M-MTP | AMD 395+ / Vulkan+MTP | 89.55% | 4 | 0 | 177.34 s | 19.10 tok/s |
| 7 | DeepSeek V4 Flash | OpenRouter | 89.51% | 5 | 0 | 309.86 s | 9.14 tok/s |
| 8 | Qwen3.6-27B-Q4_K_M | AMD 395+ / Vulkan | 89.27% | 4 | 0 | 309.56 s | 10.91 tok/s |
| 9 | Qwen3.6-27B-UD-IQ2_M | AMD 395+ / Vulkan | 87.94% | 5 | 0 | 243.42 s | 13.51 tok/s |
| 10 | gemma-4-26B-A4B-it-UD-Q4_K_M | AMD 395+ / Vulkan | 87.19% | 6 | 0 | 80.36 s | 41.35 tok/s |
| 11 | gemma-4-E4B-it-Q4_K_M | AMD 395+ / Vulkan | 86.76% | 8 | 0 | 70.10 s | 52.35 tok/s |
| 12 | Qwen3-14B-Q4_K_M | AMD 395+ / Vulkan | 85.86% | 7 | 0 | 135.65 s | 22.04 tok/s |
| 13 | Qwen3.5-9B-Q5_K_M | AMD 395+ / Vulkan | 85.57% | 7 | 0 | 104.38 s | 28.90 tok/s |
| 14 | Qwen3.6-35B-A3B-Uncensored-Q3_K_P | AMD 395+ / Vulkan | 85.35% | 7 | 0 | 61.94 s | 58.41 tok/s |
| 15 | Huihui-Qwen3.6-35B-A3B-abliterated-Q4_K-MTP | AMD 395+ / Vulkan+MTP | 84.57% | 9 | 0 | 54.30 s | 65.51 tok/s |
| 16 | Qwen3.6-35B-A3B-UD-Q4_K_M | AMD 395+ / Vulkan | 83.94% | 8 | 0 | 73.43 s | 49.95 tok/s |
| 17 | gemma-4-E4B-it-Q5_K_M | AMD 395+ / Vulkan | 83.67% | 9 | 0 | 71.26 s | 46.45 tok/s |
| 18 | GPT-5.4 Nano | OpenRouter | 83.35% | 9 | 0 | 59.33 s | 89.93 tok/s |
| 19 | Qwen3-8B-Q4_K_M | AMD 395+ / Vulkan | 81.43% | 11 | 0 | 69.63 s | 38.45 tok/s |
| 20 | Qwen3.6-35B-A3B-UD-Q5_K_M-MTP | AMD 395+ / Vulkan+MTP | 81.33% | 10 | 0 | 61.61 s | 56.94 tok/s |
| 21 | Qwen3.6-35B-A3B-UD-Q6_K-MTP | AMD 395+ / Vulkan+MTP | 80.66% | 12 | 0 | 65.05 s | 56.62 tok/s |
| 22 | Qwen3.5-9B-DeepSeek-V4-Flash-MTP-Q4_K_M | AMD 395+ / Vulkan+MTP | 79.29% | 15 | 2 | 624.30 s | 60.72 tok/s |
| 23 | Qwen3.5-4B-Q5_K_M | AMD 395+ / Vulkan | 78.21% | 12 | 0 | 65.51 s | 49.63 tok/s |
| 24 | Spark-X2.6-4B-Q5_K_M | AMD 395+ / Vulkan | 75.38% | 15 | 0 | 74.82 s | 51.70 tok/s |
| 25 | Qwen3-4B-Q5_K_M | AMD 395+ / Vulkan | 74.65% | 17 | 1 | 192.10 s | 56.10 tok/s |
| 26 | Qwopus3.5-9B-Coder-MTP-Q4_K_M | AMD 395+ / Vulkan+MTP | 72.80% | 21 | 3 | 547.05 s | 69.96 tok/s |
| 27 | gemma-4-E2B-it-Q4_K_M | AMD 395+ / Vulkan | 71.70% | 21 | 0 | 36.34 s | 100.39 tok/s |
| 28 | Phi-4-mini-instruct-Q5_K_M | AMD 395+ / Vulkan | 67.22% | 16 | 0 | 38.61 s | 62.19 tok/s |
| 29 | gemma-3-12b-it-heretic-v2-Q4_K_M | AMD 395+ / Vulkan | 65.72% | 21 | 0 | 95.00 s | 21.38 tok/s |
| 30 | Llama-3.2-3B-Instruct-Q5_K_M | AMD 395+ / Vulkan | 56.79% | 29 | 0 | 28.42 s | 74.42 tok/s |
| 31 | Phi-4-mini-instruct-Q5_K_S | AMD 395+ / Vulkan | 56.70% | 30 | 0 | 41.71 s | 64.15 tok/s |

Effective completion rate divides reported completion tokens by full request
latency. It includes prompt processing, tool turns, hidden reasoning and
provider scheduling. It is not raw generation speed or TTFT. This especially
matters for MTP fine-tunes: they process tokens quickly but can still have high
end-to-end latency because they generate thousands of hidden reasoning tokens.

## Interpretation

`Qwen3.8-27B-UD-Q6_K_M-MTP` is the current single-run capability leader at
94.57%, but its one critical failure still blocks production eligibility. The
result remains provisional until the queued five-run stability phase finishes.

The corrected post-normalizer Gemma results replace their pre-normalizer
scores. `gemma-4-31B-it-Q4_K_M` rises from 84.15% to 91.76% and has two
critical failures; `gemma-4-26B-A4B-it-UD-Q4_K_M` rises from 75.63% to 87.19%
and has six. The earlier deficit was primarily parser incompatibility in agent
execution and result validation, not model capability. A fresh six-quant Gemma
sweep is queued to verify these positions on the current runtime.

`gemma-4-E4B-it-Q4_K_M` is the strongest newly tested compact local candidate
and ranks eleventh overall after one run. Its 86.76% capability score is paired
with eight critical failures, so it is not production eligible without runtime
guards and repeated validation.

The Q4/Q5 Gemma comparison is not a clean quantization verdict. Q4 leads the
single-run macro score by 3.09 points, while Q5 is 10.57 points stronger in
code/operations. The difference comes mainly from variable validation outcomes;
both variants need three repeated runs before choosing a default quant.

The two specialized MTP 9B models achieve 96-98% draft acceptance and high raw
throughput, but their uncontrolled hidden reasoning causes two to three
truncations and 9-10x higher total latency than the ordinary compact leaders.
They should not be selected as general-purpose defaults on this evidence.

No model passes the strict zero-critical-failure production gate. The ranking
is therefore a candidate ordering, not a deployment allowlist.

`Spark-X2.6-4B-Q5_K_M` is close to the existing compact 4B baselines: it is
0.73 points ahead of Qwen3-4B and 2.83 points behind Qwen3.5-4B. It avoids
truncation but still has 15 critical failures, concentrated in top-3 tool
fusion and fallback/result-validation scenarios.

Detailed compact-wave results are in
[`BUNKER_BENCHMARK_V3_SMALL_LOCAL_20261019.md`](BUNKER_BENCHMARK_V3_SMALL_LOCAL_20261019.md).
The October-wave protocol and results are in
[`BUNKER_BENCHMARK_V3_OCTOBER_WAVE_20261026.md`](BUNKER_BENCHMARK_V3_OCTOBER_WAVE_20261026.md).
The complete October 26–27 raw evidence is published in the
[`public result bundle`](results/bunker-v3-public-results-20261027/README.md),
while the newest canonical cross-provider ordering is in the
[`v3.1 semantic re-evaluation`](BUNKER_BENCHMARK_V3_1_RESCORE_20261027.md).
