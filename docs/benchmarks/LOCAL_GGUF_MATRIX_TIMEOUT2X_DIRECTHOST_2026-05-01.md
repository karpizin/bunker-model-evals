# Local GGUF Matrix (May 1, 2026)

This note captures the validated local GGUF comparison run performed on the local `M3 Max` host after:

- doubling benchmark timeouts;
- adding `Knowledge Raw` vs `Knowledge Recoverable` scoring;
- rerunning the suite in `--direct-host` mode to avoid nested-SSH `llama-server` contamination.

Source artifacts for the full run live under the ignored generated directory:

- [`docs/benchmarks/runs/local_gguf_matrix_20260501_timeout2x_full_directhost/local_gguf_matrix_results.json`](runs/local_gguf_matrix_20260501_timeout2x_full_directhost/local_gguf_matrix_results.json)
- [`docs/benchmarks/runs/local_gguf_matrix_20260501_timeout2x_full_directhost/local_gguf_matrix_summary.md`](runs/local_gguf_matrix_20260501_timeout2x_full_directhost/local_gguf_matrix_summary.md)
- [`docs/benchmarks/runs/local_gguf_matrix_20260501_timeout2x_full_directhost/final_matrix_analysis.md`](runs/local_gguf_matrix_20260501_timeout2x_full_directhost/final_matrix_analysis.md)

## Final Matrix

| Model | Size | Avg Latency | Knowledge Raw | Knowledge Recoverable | JSON | Think Leaks | Truncations | Instr. Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-3-12b.gguf` | 6.8G | 3.42s | 12/12 | 12/12 | Yes | 1 | 3 | 8.5/10 |
| `gemma-4-E4B-it-Q4_K_M.gguf` | 4.6G | 1.57s | 10/12 | 10/12 | Yes | 0 | 3 | 8.5/10 |
| `qwen3.5-9b.gguf` | 6.1G | 5.70s | 1/12 | 8/12 | Yes | 0 | 3 | 8.5/10 |
| `phi-4-mini.gguf` | 2.5G | 1.39s | 12/12 | 12/12 | Yes | 0 | 4 | 8.0/10 |
| `ministral-8b.gguf` | 2.3G | 1.11s | 8/12 | 8/12 | Yes | 0 | 4 | 8.0/10 |
| `gemma-4-E2B-it-Q4_K_M.gguf` | 2.9G | 0.97s | 3/12 | 3/12 | Yes | 0 | 4 | 8.0/10 |
| `qwen-35b-moe.gguf` | 20.1G | 2.72s | 10/12 | 10/12 | Yes | 6 | 3 | 6.5/10 |
| `ministral-14b.gguf` | 7.7G | 3.36s | 3/12 | 3/12 | Yes | 0 | 3 | 6.5/10 |
| `Qwen3.6-27B-UD-IQ2_M.gguf` | 10.1G | 7.44s | 11/12 | 11/12 | Yes | 6 | 4 | 6.0/10 |
| `qwen3-4b.gguf` | 2.7G | 3.99s | 8/12 | 12/12 | Yes | 1 | 6 | 6.0/10 |
| `gemma-4-26B-A4B-it-UD-Q5_K_M.gguf` | 19.7G | 2.23s | 5/12 | 11/12 | Yes | 0 | 6 | 6.0/10 |
| `qwen-35b-q3.gguf` | 15.2G | 2.75s | 7/12 | 9/12 | Yes | 6 | 1 | 5.5/10 |
| `qwen-27b-q3.gguf` | 12.6G | 16.99s | 1/12 | 8/12 | Yes | 6 | 3 | 4.5/10 |
| `gemma-4-31B-it-Q3_K_S.gguf` | 12.3G | 11.73s | 7/12 | 11/12 | No | 0 | 6 | 4.0/10 |
| `glm-4.7-flash.gguf` | 10.5G | 2.15s | 7/12 | 8/12 | No | 1 | 6 | 4.0/10 |
| `Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q3_K_P.gguf` | 17.7G | 2.24s | 2/12 | 8/12 | Yes | 6 | 6 | 4.0/10 |
| `qwen-27b-q5.gguf` | 18.3G | 21.53s | 2/12 | 8/12 | Yes | 6 | 4 | 4.0/10 |
| `gemma-4-26B-A4B-it-UD-Q3_K_M.gguf` | 11.7G | 11.55s | 2/12 | 6/12 | No | 0 | 5 | 4.0/10 |
| `qwen3.5-4b.gguf` | 2.9G | 4.11s | 0/12 | 4/12 | Yes | 6 | 6 | 4.0/10 |
| `phi-4.gguf` | 8.4G | 0.22s | 0/12 | 0/12 | No | 0 | 6 | 4.0/10 |
| `qwen3-8b.gguf` | 7.7G | 6.90s | 6/12 | 12/12 | No | 3 | 6 | 2.0/10 |
| `gemma-4-31B-it-uncensored-heretic-Q4_K_M.gguf` | 17.4G | 10.63s | 4/12 | 10/12 | No | 0 | 6 | 2.0/10 |
| `nemotron-70b.gguf` | 5.4G | 4.15s | 0/12 | 12/12 | No | 1 | 6 | 2.0/10 |
| `glm4-9b.gguf` | 5.4G | 4.18s | 0/12 | 11/12 | No | 4 | 5 | 0.0/10 |

## Practical Reading Guide

- `Size`: GGUF file size on disk.
- `Avg Latency`: mean wall-clock response time across all benchmark cases and knowledge questions.
- `Knowledge Raw` tells us whether the model answers in a parser-safe, contract-safe way.
- `Knowledge Recoverable` tells us whether the fact is still present after stripping obvious output junk.
- `JSON`: whether the strict JSON case passed with the exact required schema.
- `Think Leaks`: number of main cases where visible reasoning leaked into the answer.
- `Truncations`: number of main cases that ended in an obviously cut-off or incomplete response.
- `Instr. Score`: aggregate instruction-following score derived from JSON compliance, leakage, brevity, and truncation behavior.
- A large gap between those columns usually means the model knows the answer but is operationally unsafe for agent loops without post-processing.

## Main Takeaways

- Best overall balanced model in this run: `gemma-3-12b.gguf`.
- Strongest compact `Gemma 4` candidate: `gemma-4-E4B-it-Q4_K_M.gguf`.
- Strongest large Qwen-family candidate here: `qwen-35b-moe.gguf`.
- Best example of contract-vs-knowledge mismatch: `nemotron-70b.gguf` (`0/12` raw vs `12/12` recoverable).
- Best example of genuinely weak factual behavior: `phi-4.gguf` (`0/12` raw and `0/12` recoverable).
- `gemma-4-26B-A4B-it-UD-Q5_K_M.gguf` improved materially over the older `Q3` variant, but still leaks too much structure noise for strict agent-loop use.
- `gemma-4-31B-it-uncensored-heretic-Q4_K_M.gguf` shows much better recoverable knowledge than raw score suggests, but remains weak on contract adherence.
