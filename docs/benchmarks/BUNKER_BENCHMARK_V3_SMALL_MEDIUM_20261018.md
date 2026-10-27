# Bunker Benchmark v3: small and medium model pilot

Date: 2026-10-18

Hardware: AMD Ryzen AI Max+ 395, 96 GiB GPU allocation

Protocol: one run per model, `temperature=0.05`, `max_tokens=8192`,
`case_timeout=600`, `ctx_size=32768`, full GPU offload, visible reasoning off.

This is a calibration wave, not a final ranking. The score is the macro mean of
five capability tracks. Runtime performance and strict production eligibility
are reported separately.

## Results

| Rank | Model | GGUF size | Capability | Critical failures | Truncated | Total latency | Effective completion rate |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Qwen3.8-27B-Q4_K_M | 17.67 GiB | 90.49% | 4 | 0 | 344.05 s | 9.93 tok/s |
| 2 | Qwen3-14B-Q4_K_M | 8.38 GiB | 85.86% | 7 | 0 | 135.65 s | 22.04 tok/s |
| 3 | Qwen3.5-9B-Q5_K_M | 6.13 GiB | 85.57% | 7 | 0 | 104.38 s | 28.90 tok/s |
| 4 | Qwen3.5-4B-Q5_K_M | 2.93 GiB | 78.21% | 12 | 0 | 65.51 s | 49.63 tok/s |
| 5 | Phi-4-mini-instruct-Q5_K_M | 2.65 GiB | 67.22% | 16 | 0 | 38.61 s | 62.19 tok/s |

The effective completion rate is completion tokens divided by full request
latency across all cases. It includes prompt processing and multi-step tool
turns, so it must not be interpreted as raw llama.cpp generation speed. TTFT
was not measured because the v3 pilot used non-streaming responses.

## Track scores

| Model | Synthesis | Agent execution | Result validation | Grounded RAG | Code and operations |
|---|---:|---:|---:|---:|---:|
| Qwen3.8-27B-Q4_K_M | 96.92% | 93.37% | 85.87% | 94.44% | 81.84% |
| Qwen3-14B-Q4_K_M | 93.72% | 81.88% | 85.87% | 94.44% | 73.38% |
| Qwen3.5-9B-Q5_K_M | 91.42% | 93.06% | 86.96% | 90.28% | 66.14% |
| Qwen3.5-4B-Q5_K_M | 87.32% | 77.22% | 68.48% | 91.88% | 66.14% |
| Phi-4-mini-instruct-Q5_K_M | 60.66% | 77.31% | 63.09% | 80.79% | 54.24% |

## Findings

1. v3 separates the models much better than the historical contract suite. The
   capability score rises with model strength, but does not blindly reward
   parameter count.
2. Qwen3.5-9B and Qwen3-14B are effectively tied after one run. The 9B model is
   stronger in agent execution and faster; the 14B model is stronger in RAG,
   synthesis and code safety.
3. Qwen3.8-27B is the clear quality leader. It is the only model that passed
   top-3 search fusion, path traversal and tenant isolation without a critical
   failure in the same run.
4. No response reached the output-token ceiling. The `8192/600` protocol
   removed the score cliffs caused by truncation in the historical benchmark.
5. None of the five runs is production-eligible under the strict rule that any
   critical failure is disqualifying. The rule is working as designed rather
   than hiding safety failures inside a high average.

## Blocking cases

Qwen3.8-27B has two remaining blocking scenarios:

- `v3_validate_stale_weather`: it did not refresh stale data and then relied on
  the stale result;
- `v3_ops_failed_update_rollback`: it missed the root cause and the complete
  safe recovery sequence.

All smaller models also fail parts of tenant isolation or safe rollback. These
cases should be reviewed manually before changing their wording or weights;
they represent product-critical behavior and should not be weakened merely to
produce eligible models.

## Next comparison

Repeat the top three candidates three times to measure variance:

- Qwen3.8-27B-Q4_K_M;
- Qwen3-14B-Q4_K_M;
- Qwen3.5-9B-Q5_K_M.

The raw checkpoint and generated case report are stored in
`docs/benchmarks/runs/bunker-benchmark-v3-small-medium-20261018/`.
