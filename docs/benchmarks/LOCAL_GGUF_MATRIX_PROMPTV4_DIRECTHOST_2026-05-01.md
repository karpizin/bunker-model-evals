# Local GGUF Matrix Prompt-Tuned Run (May 1, 2026)

This note captures the validated prompt-tuned local GGUF rerun performed on the local `M3 Max` host with:

- `--direct-host` execution;
- doubled timeouts from the validated baseline harness;
- prompt profile `knowledge_contract_v4`, which keeps the main reasoning/planning prompts close to baseline and only tightens the factual answer contract.

Source artifacts for the full run live under the ignored generated directory:

- [`docs/benchmarks/runs/local_gguf_matrix_20260501_promptv4_full_directhost/local_gguf_matrix_results.json`](runs/local_gguf_matrix_20260501_promptv4_full_directhost/local_gguf_matrix_results.json)
- [`docs/benchmarks/runs/local_gguf_matrix_20260501_promptv4_full_directhost/local_gguf_matrix_summary.md`](runs/local_gguf_matrix_20260501_promptv4_full_directhost/local_gguf_matrix_summary.md)

Reference baseline:

- [`docs/benchmarks/LOCAL_GGUF_MATRIX_TIMEOUT2X_DIRECTHOST_2026-05-01.md`](LOCAL_GGUF_MATRIX_TIMEOUT2X_DIRECTHOST_2026-05-01.md)

## Final Matrix

| Model | Size | Avg Latency | Knowledge Raw | Knowledge Recoverable | JSON | Think Leaks | Truncations | Instr. Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-3-12b.gguf` | 6.8G | 6.88s | 12/12 | 12/12 | Yes | 1 | 1 | 9.5/10 |
| `ministral-8b.gguf` | 2.3G | 2.12s | 12/12 | 12/12 | Yes | 0 | 4 | 8.0/10 |
| `gemma-4-E4B-it-Q4_K_M.gguf` | 4.6G | 2.48s | 12/12 | 12/12 | Yes | 0 | 4 | 8.0/10 |
| `phi-4-mini.gguf` | 2.5G | 2.96s | 12/12 | 12/12 | Yes | 0 | 5 | 8.0/10 |
| `gemma-4-E2B-it-Q4_K_M.gguf` | 2.9G | 1.13s | 9/12 | 9/12 | Yes | 0 | 5 | 8.0/10 |
| `qwen-27b-q5.gguf` | 18.3G | 22.01s | 0/12 | 0/12 | Yes | 6 | 1 | 7.5/10 |
| `qwen3.5-9b.gguf` | 6.1G | 6.36s | 6/12 | 6/12 | Yes | 0 | 2 | 7.0/10 |
| `qwen-27b-q3.gguf` | 12.6G | 17.76s | 0/12 | 0/12 | Yes | 6 | 2 | 7.0/10 |
| `ministral-14b.gguf` | 7.7G | 6.86s | 12/12 | 12/12 | Yes | 1 | 3 | 6.5/10 |
| `Qwen3.6-27B-UD-IQ2_M.gguf` | 10.1G | 14.54s | 12/12 | 12/12 | Yes | 6 | 3 | 6.5/10 |
| `qwen-35b-moe.gguf` | 20.1G | 3.08s | 12/12 | 12/12 | Yes | 6 | 4 | 6.0/10 |
| `qwen3-4b.gguf` | 2.7G | 4.04s | 11/12 | 12/12 | Yes | 1 | 6 | 6.0/10 |
| `gemma-4-26B-A4B-it-UD-Q5_K_M.gguf` | 19.7G | 6.20s | 11/12 | 11/12 | Yes | 0 | 6 | 6.0/10 |
| `qwen-35b-q3.gguf` | 15.2G | 2.84s | 10/12 | 10/12 | Yes | 6 | 3 | 4.5/10 |
| `qwen3.5-4b.gguf` | 2.9G | 4.12s | 4/12 | 4/12 | Yes | 6 | 3 | 4.5/10 |
| `gemma-4-26B-A4B-it-UD-Q3_K_M.gguf` | 11.7G | 3.10s | 11/12 | 12/12 | No | 0 | 4 | 4.0/10 |
| `gemma-4-31B-it-uncensored-heretic-Q4_K_M.gguf` | 17.4G | 17.53s | 7/12 | 7/12 | No | 0 | 5 | 4.0/10 |
| `gemma-4-31B-it-Q3_K_S.gguf` | 12.3G | 22.94s | 7/12 | 7/12 | No | 0 | 5 | 4.0/10 |
| `Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q3_K_P.gguf` | 17.7G | 3.43s | 6/12 | 10/12 | Yes | 6 | 6 | 4.0/10 |
| `phi-4.gguf` | 8.4G | 1.07s | 3/12 | 3/12 | No | 0 | 6 | 4.0/10 |
| `qwen3-8b.gguf` | 7.7G | 7.19s | 12/12 | 12/12 | No | 2 | 5 | 2.0/10 |
| `glm4-9b.gguf` | 5.4G | 7.63s | 12/12 | 12/12 | No | 1 | 6 | 2.0/10 |
| `glm-4.7-flash.gguf` | 10.5G | 3.31s | 8/12 | 10/12 | No | 0 | 4 | 2.0/10 |
| `nemotron-70b.gguf` | 5.4G | 7.31s | 12/12 | 12/12 | No | 3 | 5 | 0.0/10 |

## How To Read This Run

- `Knowledge Raw` is the strict parser-safe score.
- `Knowledge Recoverable` is the score after stripping obvious output junk such as `<think>` and boilerplate markers.
- The factual prompt was tightened specifically to favor short exact answers:

```text
Answer with only the shortest correct answer and no explanation.
Q: <question>
A:
```

- This means a raw-score gain in this run should be read as: the model became better at obeying a tight short-answer contract, not necessarily that its world knowledge improved.

## Delta Vs Baseline

Biggest raw-knowledge gains:

- `glm4-9b.gguf`: `0/12 -> 12/12`
- `ministral-14b.gguf`: `3/12 -> 12/12`
- `gemma-4-26B-A4B-it-UD-Q3_K_M.gguf`: `2/12 -> 11/12`
- `qwen3-8b.gguf`: `6/12 -> 12/12`
- `gemma-4-E2B-it-Q4_K_M.gguf`: `3/12 -> 9/12`
- `qwen3.5-9b.gguf`: `1/12 -> 6/12`

Models that stayed strong and became slightly cleaner:

- `gemma-3-12b.gguf`: stayed `12/12`, `Instr. Score 8.5 -> 9.5`, `Truncations 3 -> 1`
- `Qwen3.6-27B-UD-IQ2_M.gguf`: `11/12 -> 12/12`, `Truncations 4 -> 3`
- `qwen-35b-moe.gguf`: `10/12 -> 12/12`, but still high reasoning leakage

Models that improved on factual contract but still remain operationally messy:

- `Qwen3.6-35B-A3B-Uncensored...`: `2/12 -> 6/12`, `Recoverable 8/12 -> 10/12`, still `Think Leaks 6`, `Truncations 6`
- `qwen-35b-q3.gguf`: `7/12 -> 10/12`, but `Instr. Score 5.5 -> 4.5` because truncation got worse
- `gemma-4-26B-A4B-it-UD-Q5_K_M.gguf`: `5/12 -> 11/12`, but still high truncation and limited instruction cleanliness

Models that regressed under the tighter factual contract:

- `qwen-27b-q3.gguf`: `1/12 -> 0/12`
- `qwen-27b-q5.gguf`: `2/12 -> 0/12`
- `gemma-4-31B-it-Q3_K_S.gguf`: `Recoverable 11/12 -> 7/12`
- `gemma-4-31B-it-uncensored-heretic-Q4_K_M.gguf`: `Recoverable 10/12 -> 7/12`

## Practical Takeaways

- The tighter knowledge prompt was worth it for models whose main failure mode was format drift rather than missing knowledge.
- Small and medium models benefited the most.
- The effect is not universal: some large Qwen models reacted poorly, likely because the shorter contract removed room for them to "self-correct" after visible reasoning.
- For future benchmark suites, it makes sense to keep both views:
  - baseline prompts for broad agent-style behavior;
  - `knowledge_contract_v4` for short factual contract adherence.

## Follow-up Candidate Runs

After the main `v4` matrix, two additional follow-up candidates were tested separately with the same `knowledge_contract_v4` profile.

Artifacts:

- [`docs/benchmarks/runs/local_gguf_matrix_20260501_qwen36_27b_q5km_v4/local_gguf_matrix_results.json`](runs/local_gguf_matrix_20260501_qwen36_27b_q5km_v4/local_gguf_matrix_results.json)
- [`docs/benchmarks/runs/local_gguf_matrix_20260501_qwen36_27b_q5km_v4/local_gguf_matrix_summary.md`](runs/local_gguf_matrix_20260501_qwen36_27b_q5km_v4/local_gguf_matrix_summary.md)
- [`docs/benchmarks/runs/local_gguf_matrix_20260501_mixtral8x7b_q3km_v4/local_gguf_matrix_results.json`](runs/local_gguf_matrix_20260501_mixtral8x7b_q3km_v4/local_gguf_matrix_results.json)

| Model | Status | Avg Latency | Knowledge Raw | Knowledge Recoverable | JSON | Think Leaks | Truncations | Instr. Score |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `Qwen3.6-27B-Q5_K_M.gguf` | completed | 20.91s | 12/12 | 12/12 | Yes | 6 | 6 | 4.0/10 |
| `mixtral-8x7b-instruct-v0.1.Q3_K_M.gguf` | failed to load | — | — | — | — | — | — | — |

Comparison against the already-validated `Qwen3.6-27B-UD-IQ2_M.gguf`:

| Model | Size | Avg Latency | Knowledge Raw | JSON | Think Leaks | Truncations | Instr. Score |
|---|---:|---:|---:|---:|---:|---:|---:|
| `Qwen3.6-27B-UD-IQ2_M.gguf` | 10.1G | 14.54s | 12/12 | Yes | 6 | 3 | 6.5/10 |
| `Qwen3.6-27B-Q5_K_M.gguf` | 18.2G | 20.91s | 12/12 | Yes | 6 | 6 | 4.0/10 |

Takeaways:

- `Qwen3.6-27B-Q5_K_M.gguf` did not improve factual correctness over `UD-IQ2_M`.
- It was materially slower and less operationally clean, with worse truncation behavior and a lower instruction-following score.
- `mixtral-8x7b-instruct-v0.1.Q3_K_M.gguf` was not benchmarkable in the current runtime. A direct `llama-cli` smoke test failed with:
  - `missing tensor 'blk.0.ffn_down_exps.weight'`

That failure suggests a broken or incompatible GGUF conversion for the current `llama.cpp` stack, not merely a weak benchmark result.
