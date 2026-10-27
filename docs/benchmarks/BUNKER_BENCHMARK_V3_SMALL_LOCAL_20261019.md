# Bunker Benchmark v3: compact local model wave

Date: 2026-10-19

Hardware: AMD Ryzen AI Max+ 395 with Radeon 8060S, 96 GiB UMA reserved for the
GPU. Inference used the Vulkan backend with full GPU offload.

Runtime: upstream `llama.cpp` 0.7.0-dev, commit `b76b133`. Protocol: one run per
model, `temperature=0.05`, `max_tokens=8192`, `case_timeout=600`,
`ctx_size=32768`, visible reasoning off. The two MTP models additionally used
`draft-mtp`, draft length 1-4 and `p_min=0.75`.

The compact pool is defined by a primary GGUF size no greater than 10 GiB. It
excludes embeddings, rerankers, vocab files, `mmproj`, standalone draft or
assistant artifacts and incomplete shards. Four already comparable full-GPU
v3 results were reused; ten previously untested primary models were run here.

## New results

| Rank | Model | Capability | Critical failures | Truncated | Total latency | Average case | Effective completion rate |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | gemma-4-E4B-it-Q4_K_M | 86.76% | 8 | 0 | 70.10 s | 3.50 s | 52.35 tok/s |
| 2 | gemma-4-E4B-it-Q5_K_M | 83.67% | 9 | 0 | 71.26 s | 3.56 s | 46.45 tok/s |
| 3 | Qwen3-8B-Q4_K_M | 81.43% | 11 | 0 | 69.63 s | 3.48 s | 38.45 tok/s |
| 4 | Qwen3.5-9B-DeepSeek-V4-Flash-MTP-Q4_K_M | 79.29% | 15 | 2 | 624.30 s | 31.21 s | 60.72 tok/s |
| 5 | Qwen3-4B-Q5_K_M | 74.65% | 17 | 1 | 192.10 s | 9.61 s | 56.10 tok/s |
| 6 | Qwopus3.5-9B-Coder-MTP-Q4_K_M | 72.80% | 21 | 3 | 547.05 s | 27.35 s | 69.96 tok/s |
| 7 | gemma-4-E2B-it-Q4_K_M | 71.70% | 21 | 0 | 36.34 s | 1.82 s | 100.39 tok/s |
| 8 | gemma-3-12b-it-heretic-v2-Q4_K_M | 65.72% | 21 | 0 | 95.00 s | 4.75 s | 21.38 tok/s |
| 9 | Llama-3.2-3B-Instruct-Q5_K_M | 56.79% | 29 | 0 | 28.42 s | 1.42 s | 74.42 tok/s |
| 10 | Phi-4-mini-instruct-Q5_K_S | 56.70% | 30 | 0 | 41.71 s | 2.09 s | 64.15 tok/s |

TTFT is unavailable because the v3 runner uses non-streaming responses. The
effective completion rate includes prompt processing, multi-turn tool traces
and hidden reasoning, so it must not be read as raw decode throughput.

## Track scores

| Model | Synthesis | Agent execution | Result validation | Grounded RAG | Code and operations |
|---|---:|---:|---:|---:|---:|
| gemma-4-E4B-it-Q4_K_M | 91.93% | 85.49% | 92.74% | 94.44% | 69.22% |
| gemma-4-E4B-it-Q5_K_M | 88.85% | 84.07% | 75.35% | 90.28% | 79.79% |
| Qwen3-8B-Q4_K_M | 87.26% | 77.27% | 81.52% | 90.60% | 70.48% |
| Qwen3.5-9B-DeepSeek-V4-Flash-MTP-Q4_K_M | 82.18% | 93.06% | 76.09% | 90.28% | 54.82% |
| Qwen3-4B-Q5_K_M | 78.71% | 65.89% | 81.52% | 86.43% | 60.67% |
| Qwopus3.5-9B-Coder-MTP-Q4_K_M | 58.92% | 91.80% | 76.09% | 91.67% | 45.53% |
| gemma-4-E2B-it-Q4_K_M | 74.82% | 55.65% | 74.17% | 87.71% | 66.14% |
| gemma-3-12b-it-heretic-v2-Q4_K_M | 60.53% | 55.62% | 69.09% | 80.02% | 63.33% |
| Llama-3.2-3B-Instruct-Q5_K_M | 59.31% | 36.58% | 63.09% | 68.80% | 56.17% |
| Phi-4-mini-instruct-Q5_K_S | 63.73% | 37.75% | 56.09% | 71.07% | 54.88% |

## Findings

1. Gemma 4 E4B is the strongest compact family in this wave. Q4 leads the
   one-run macro score, while Q5 is materially stronger in code/operations.
   The reversal is driven by variable validation cases, not evidence that the
   lower quant is intrinsically more accurate.
2. Qwen3.5-9B-Q5_K_M from the earlier pilot remains the most balanced ordinary
   9B model at 85.57%. The DeepSeek MTP distill improves agent execution to
   93.06% but loses code safety, truncates twice and takes six times longer.
3. Qwen3.5-4B from the pilot leads Qwen3-4B by 3.56 points and has no
   truncations. The older Qwen3 artifact ran into one 8,192-token output loop.
4. The 12B Heretic fine-tune is not competitive for BunkerAI agent work. Its
   65.72% score is below both Gemma 4 E2B and E4B, showing that parameter count
   does not compensate for an unsuitable instruction/fine-tuning profile.
5. The Q5_K_S Phi artifact scores 10.52 points below the existing Q5_K_M run.
   This gap is too large to attribute to quantization alone without repeated
   runs and source-artifact verification.

## MTP behavior

Qwopus achieved 97.90% weighted draft acceptance with sampled generation near
69 tok/s. The DeepSeek distill achieved 96.37% acceptance and about 58 tok/s.
MTP therefore works correctly and provides useful throughput, but both models
continue generating large hidden reasoning traces after the answer should be
short. Qwopus truncated three cases and DeepSeek two. High token throughput did
not translate into low end-to-end latency.

## Test integrity

The first diagnostic launch exposed a CPU-only `llama.cpp` binary behind a
working `--gpu-layers` flag. Those diagnostic results were rejected. The final
runs in this report used an explicit `Vulkan0` device and full GPU offload; the
GPU profile approximately doubled decode speed and tripled prompt processing
on the 3B smoke model. Production inference on port 11435 was not interrupted.

No candidate in the compact pool passes the strict zero-critical-failure gate.
The recommended next step is three runs each for Gemma 4 E4B Q4, Gemma 4 E4B
Q5 and Qwen3.5-9B Q5, followed by per-case variance and paired quant analysis.

Raw checkpoints and generated reports are stored in
`docs/benchmarks/runs/bunker-benchmark-v3-small-local-20261018/`.
