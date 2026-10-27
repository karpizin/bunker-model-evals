# Bunker Benchmark v3.1: semantic re-evaluation

Generated: `2026-10-28T06:30:56+08:00`
Rubric: `bunker_benchmark_v3_1_semantic_concepts_20261027`

## Outcome

Scanned **121** archived result files and **229** complete 20-case runs. After removing byte-equivalent duplicate runs, **219** runs across **74** model configurations were re-scored. The new rubric changed **1116** formerly failed literal checks to pass after accepting equivalent wording, and changed **0** passes to failures.

The candidate answers were not regenerated. Empty leading reasoning close delimiters emitted by some chat templates were normalized as transport residue; complete reasoning blocks remain visible and fail the deterministic leak check. Tool selection, call arguments, parallelism, ordering, approval, exact evidence IDs, numeric values, JSON contracts, truncation and visible-reasoning checks remain deterministic. Only explicitly versioned free-text checks now accept equivalent Russian and English formulations and stable technical aliases.

## Representative ranking

For each model configuration, this table selects the newest canonical cohort available: verified 2026-10-27 quantization and vendor cohorts first, then the October wave, hosted/full-GPU corrected runs, and the original medium/large wave. Diagnostic smoke and tool-compat runs remain in the audit JSON but are excluded here.

| Rank | Model | Runs | v3.1 mean | Range | Old v3 | Delta | Critical failures | Eligible | Mean latency |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `Qwen3.8-27B-Q8_0-MTP` | 5 | 96.91% | 95.77–97.74% | 93.80% | +3.12 pp | 0–1 | 4/5 | 229.32 s |
| 2 | `google/gemini-3.8-flash` | 1 | 96.40% | 96.40% | 93.01% | +3.39 pp | 0 | 1/1 | 167.26 s |
| 3 | `Qwen3.8-27B-UD-Q6_K_M-MTP` | 5 | 96.22% | 95.61–96.76% | 94.09% | +2.13 pp | 0–1 | 4/5 | 197.82 s |
| 4 | `MiMo-V2.6-Flash-MOPD-full-Q3_K` | 1 | 95.45% | 95.45% | 93.14% | +2.31 pp | 2 | 0/1 | 15757.48 s |
| 5 | `gemma-4-31B-it-Q6_K` | 5 | 95.34% | 94.98–95.93% | 92.84% | +2.50 pp | 0 | 5/5 | 474.77 s |
| 6 | `gemma-4-31B-it-Q8_0` | 5 | 94.99% | 94.24–95.27% | 92.84% | +2.16 pp | 0–1 | 3/5 | 559.36 s |
| 7 | `Qwen3.8-27B-Uncensored-Q6_K-MTP` | 5 | 94.81% | 93.79–95.16% | 89.21% | +5.61 pp | 2 | 0/5 | 188.84 s |
| 8 | `gemma-4-31B-it-uncensored-heretic-Q8_0` | 5 | 94.16% | 93.95–94.98% | 91.38% | +2.78 pp | 0–1 | 1/5 | 543.56 s |
| 9 | `Qwen3.8-27B-UD-IQ3_XXS` | 5 | 93.94% | 92.54–95.16% | 90.82% | +3.12 pp | 2–3 | 0/5 | 221.54 s |
| 10 | `gemma-4-31B-it-Q5_K_M` | 5 | 93.93% | 93.68–94.35% | 92.64% | +1.29 pp | 1 | 0/5 | 404.00 s |
| 11 | `gemma-4-31B-it-uncensored-heretic-Q6_K` | 5 | 93.80% | 93.11–94.14% | 90.82% | +2.98 pp | 0–1 | 2/5 | 449.81 s |
| 12 | `gemma-4-31B-it-Q4_K_M` | 5 | 93.79% | 93.68–94.24% | 91.62% | +2.17 pp | 1 | 0/5 | 346.08 s |
| 13 | `gemma-4-31B-it-uncensored-heretic-Q4_K_M` | 5 | 93.78% | 93.78% | 90.71% | +3.07 pp | 1 | 0/5 | 355.31 s |
| 14 | `Qwen3.8-27B-Q4_K_M` | 5 | 93.66% | 92.47–94.26% | 90.31% | +3.35 pp | 2–3 | 0/5 | 343.39 s |
| 15 | `NVIDIA-Nemotron-3.5-Bolt-74B-A9B-AD-IQ4_XS` | 3 | 93.50% | 93.50% | 80.89% | +12.61 pp | 3 | 0/3 | 191.61 s |
| 16 | `Qwen3.6-27B-UD-IQ3_XXS-MTP` | 5 | 93.03% | 92.04–94.51% | 90.94% | +2.08 pp | 0–2 | 1/5 | 180.03 s |
| 17 | `Qwen3.6-27B-Q4_K_M-MTP` | 5 | 92.25% | 91.58–93.18% | 89.31% | +2.94 pp | 2–3 | 0/5 | 190.78 s |
| 18 | `Qwen3.5-122B-A10B-UD-IQ4_NL-MTP` | 1 | 92.09% | 92.09% | 87.88% | +4.21 pp | 5 | 0/1 | 141.45 s |
| 19 | `Qwen3.5-122B-A10B-Q3_K_M` | 1 | 91.74% | 91.74% | 88.79% | +2.95 pp | 4 | 0/1 | 202.90 s |
| 20 | `deepseek/deepseek-v4-flash` | 1 | 91.25% | 91.25% | 89.51% | +1.74 pp | 5 | 0/1 | 309.86 s |
| 21 | `Qwen3.6-27B-Q4_K_M` | 5 | 91.13% | 89.76–92.16% | 87.82% | +3.32 pp | 3–5 | 0/5 | 312.94 s |
| 22 | `Huihui-Qwen3.6-35B-A3B-abliterated-Q8_0-MTP` | 1 | 90.89% | 90.89% | 84.08% | +6.81 pp | 3 | 0/1 | 62.78 s |
| 23 | `gemma-4-26B-A4B-it-UD-Q4_K_M` | 1 | 90.83% | 90.83% | 86.87% | +3.96 pp | 4 | 0/1 | 80.98 s |
| 24 | `Qwen3.8-Flash-Next-UD-IQ3_XXS-MTP` | 1 | 90.77% | 90.77% | 87.38% | +3.39 pp | 9 | 0/1 | 153.09 s |
| 25 | `Qwen3-Coder-Next-Q4_K_M` | 1 | 90.73% | 90.73% | 87.79% | +2.94 pp | 5 | 0/1 | 84.70 s |
| 26 | `Huihui-Qwen3.6-35B-A3B-abliterated-Q6_K-MTP` | 5 | 90.58% | 89.80–91.46% | 84.28% | +6.30 pp | 2–3 | 0/5 | 51.94 s |
| 27 | `NVIDIA-Nemotron-3.5-Bolt-74B-A9B-UD-IQ2_M` | 4 | 90.58% | 88.61–92.37% | 78.44% | +12.15 pp | 5–8 | 0/4 | 150.66 s |
| 28 | `Qwen3.8-27B-IQ2_M` | 5 | 89.86% | 88.76–90.45% | 88.29% | +1.56 pp | 4–6 | 0/5 | 209.68 s |
| 29 | `Qwen3.6-27B-UD-IQ2_M` | 5 | 89.78% | 89.31–89.99% | 88.00% | +1.78 pp | 4–5 | 0/5 | 243.95 s |
| 30 | `gemma-4-E4B-it-Q6_K` | 5 | 89.57% | 89.09–90.01% | 86.34% | +3.22 pp | 4–5 | 0/5 | 80.49 s |
| 31 | `gemma-4-26B-A4B-it-UD-Q3_K_M` | 1 | 89.56% | 89.56% | 86.70% | +2.86 pp | 3 | 0/1 | 77.34 s |
| 32 | `Qwen3.6-35B-A3B-Uncensored-Q3_K_P` | 5 | 89.56% | 89.04–90.86% | 84.14% | +5.42 pp | 4 | 0/5 | 57.88 s |
| 33 | `Qwen3.8-Flash-Next-Q2_K-MTP` | 1 | 89.41% | 89.41% | 84.18% | +5.23 pp | 9 | 0/1 | 148.27 s |
| 34 | `Qwen3.6-35B-A3B-UD-Q4_K_M` | 1 | 89.37% | 89.37% | 83.94% | +5.43 pp | 5 | 0/1 | 73.43 s |
| 35 | `Ornith-1.5-122B-UD-IQ3_XXS-MTP` | 4 | 89.34% | 86.93–90.68% | 85.18% | +4.16 pp | 6–9 | 0/4 | 211.70 s |
| 36 | `gemma-4-26B-A4B-it-UD-Q5_K_M` | 5 | 89.12% | 89.01–89.29% | 88.18% | +0.94 pp | 4 | 0/5 | 88.73 s |
| 37 | `gemma-4-E4B-it-Q4_K_M` | 1 | 89.05% | 89.05% | 85.86% | +3.19 pp | 6 | 0/1 | 71.69 s |
| 38 | `Mistral-Medium-3.5-128B-Q3_K_M` | 1 | 89.04% | 89.04% | 86.30% | +2.74 pp | 5 | 0/1 | 998.03 s |
| 39 | `Qwen3.6-35B-A3B-Uncensored-Q6_K_P` | 1 | 88.39% | 88.39% | 84.02% | +4.37 pp | 5 | 0/1 | 75.42 s |
| 40 | `gemma-4-E4B-it-Q8_0` | 5 | 87.68% | 86.55–89.37% | 84.59% | +3.08 pp | 5–7 | 0/5 | 91.08 s |
| 41 | `Qwen3.6-35B-A3B-UD-Q6_K-MTP` | 1 | 86.91% | 86.91% | 80.66% | +6.25 pp | 7 | 0/1 | 65.05 s |
| 42 | `Huihui-Qwen3.6-35B-A3B-abliterated-Q4_K-MTP` | 1 | 86.87% | 86.87% | 84.57% | +2.30 pp | 7 | 0/1 | 54.30 s |
| 43 | `gemma-4-E4B-it-Q5_K_M` | 1 | 86.53% | 86.53% | 83.67% | +2.86 pp | 7 | 0/1 | 71.26 s |
| 44 | `Qwen3-14B-Q4_K_M` | 1 | 86.27% | 86.27% | 83.79% | +2.48 pp | 7 | 0/1 | 140.61 s |
| 45 | `openai/gpt-5.4-nano` | 1 | 86.17% | 86.17% | 83.35% | +2.82 pp | 7 | 0/1 | 59.33 s |
| 46 | `Nanbeige4.3-33B-Q4_K_M` | 1 | 85.71% | 85.71% | 82.72% | +2.99 pp | 10 | 0/1 | 532.91 s |
| 47 | `Qwen3.5-9B-Q5_K_M` | 1 | 85.53% | 85.53% | 84.02% | +1.51 pp | 7 | 0/1 | 110.81 s |
| 48 | `Qwen3.6-35B-A3B-Uncensored-Q8_K_P` | 5 | 85.33% | 84.71–85.86% | 82.14% | +3.19 pp | 6–8 | 0/5 | 90.37 s |
| 49 | `Qwen3.6-35B-A3B-UD-Q5_K_M-MTP` | 1 | 85.25% | 85.25% | 81.33% | +3.92 pp | 8 | 0/1 | 61.61 s |
| 50 | `NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-Q4_0-MTP` | 1 | 84.07% | 84.07% | 72.72% | +11.35 pp | 11 | 0/1 | 162.88 s |
| 51 | `NVIDIA-Nemotron-3-Super-120B-A12B-UD-Q3_K_M` | 1 | 83.90% | 83.90% | 72.77% | +11.13 pp | 10 | 0/1 | 231.28 s |
| 52 | `Llama-3.3-70B-Instruct-Q4_K_M` | 1 | 83.65% | 83.65% | 82.11% | +1.54 pp | 8 | 0/1 | 469.02 s |
| 53 | `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0-MTP` | 1 | 83.44% | 83.44% | 70.60% | +12.84 pp | 9 | 0/1 | 47.79 s |
| 54 | `Qwen3-8B-Q4_K_M` | 1 | 82.72% | 82.72% | 81.43% | +1.29 pp | 10 | 0/1 | 69.63 s |
| 55 | `Qwen3.5-9B-DeepSeek-V4-Flash-MTP-Q4_K_M` | 1 | 81.84% | 81.84% | 79.29% | +2.55 pp | 13 | 0/1 | 624.30 s |
| 56 | `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-UD-Q6_K_XL-MTP` | 1 | 81.39% | 81.39% | 70.05% | +11.34 pp | 10 | 0/1 | 60.00 s |
| 57 | `Qwen3.5-4B-Q5_K_M` | 1 | 80.92% | 80.92% | 78.21% | +2.71 pp | 11 | 0/1 | 65.51 s |
| 58 | `NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-UD-Q4_K_XL-MTP` | 1 | 79.80% | 79.80% | 70.26% | +9.54 pp | 15 | 0/1 | 178.23 s |
| 59 | `Qwen3-4B-Q5_K_M` | 1 | 77.22% | 77.22% | 74.65% | +2.57 pp | 16 | 0/1 | 192.10 s |
| 60 | `Flint-Q4_K_M` | 1 | 76.88% | 76.88% | 76.24% | +0.64 pp | 16 | 0/1 | 75.29 s |
| 61 | `Spark-X2.6-4B-Q5_K_M` | 1 | 76.08% | 76.08% | 75.38% | +0.70 pp | 15 | 0/1 | 74.82 s |
| 62 | `Qwopus3.5-9B-Coder-MTP-Q4_K_M` | 1 | 75.62% | 75.62% | 72.80% | +2.82 pp | 19 | 0/1 | 547.05 s |
| 63 | `gemma-4-E2B-it-Q4_K_M` | 1 | 74.10% | 74.10% | 71.70% | +2.40 pp | 18 | 0/1 | 36.34 s |
| 64 | `Phi-4-mini-instruct-Q5_K_M` | 1 | 71.83% | 71.83% | 67.22% | +4.61 pp | 13 | 0/1 | 38.61 s |
| 65 | `Qwen3.6-27B-Abliterated-Q4_K_M-MTP` | 1 | 71.56% | 71.56% | 70.24% | +1.32 pp | 23 | 0/1 | 193.17 s |
| 66 | `Sakura-MiMo-V2.6-Flash-MOPD-P160-IQ2_XS` | 1 | 70.16% | 70.16% | 67.47% | +2.69 pp | 27 | 0/1 | 420.26 s |
| 67 | `gemma-3-12b-it-heretic-v2-Q4_K_M` | 1 | 69.32% | 69.32% | 65.72% | +3.60 pp | 19 | 0/1 | 95.00 s |
| 68 | `YandexGPT-5-Lite-8B-Instruct-Q4_K_M` | 5 | 69.30% | 67.58–70.02% | 66.78% | +2.52 pp | 18–20 | 0/5 | 52.60 s |
| 69 | `MiniMax-M2.7-Q2_K` | 1 | 65.54% | 65.54% | 63.40% | +2.14 pp | 29 | 0/1 | 1017.49 s |
| 70 | `GigaChat3.1-10B-A1.8B-Q6_K` | 5 | 62.69% | 59.89–66.11% | 61.73% | +0.96 pp | 23–27 | 0/5 | 22.78 s |
| 71 | `Llama-3.2-3B-Instruct-Q5_K_M` | 1 | 57.73% | 57.73% | 56.79% | +0.94 pp | 29 | 0/1 | 28.42 s |
| 72 | `Phi-4-mini-instruct-Q5_K_S` | 1 | 57.16% | 57.16% | 56.70% | +0.46 pp | 30 | 0/1 | 41.71 s |
| 73 | `LFM2.5-24B-A2B-Q4_K_M` | 1 | 43.50% | 43.50% | 43.50% | +0.00 pp | 48 | 0/1 | 175.40 s |
| 74 | `LFM2.5-24B-A2B-UD-Q6_K_XL` | 1 | 37.78% | 37.78% | 37.46% | +0.32 pp | 52 | 0/1 | 159.93 s |

The current representative leader is `Qwen3.8-27B-Q8_0-MTP` at **96.91%** across 5 run(s).
The highest-ranked repeated cohort is `Qwen3.8-27B-Q8_0-MTP` at **96.91%** across 5 runs (4/5 eligible).
Capability score and production eligibility are separate: any critical failure keeps a run out of the eligible set even when its mean score is high.

## Where the old scorer was brittle

| Case / check | Failed → passed | Passed → failed |
|---|---:|---:|
| `v3_agent_public_private_reconciliation` / `concepts_all` | 176 | 0 |
| `v3_validate_timeout_fallback` / `honest_freshness_limit` | 111 | 0 |
| `v3_ops_failed_update_rollback` / `correct_root_cause` | 92 | 0 |
| `v3_ops_failed_update_rollback` / `safe_recovery_sequence` | 85 | 0 |
| `v3_agent_top3_search_fusion` / `correct_public_local_fusion` | 58 | 0 |
| `v3_ops_failed_update_rollback` / `json_path_concepts_all` | 48 | 0 |
| `v3_code_tenant_isolation` / `cross_tenant_disclosure` | 37 | 0 |
| `v3_agent_approval_restart_recovery` / `concepts_all` | 36 | 0 |
| `v3_code_path_traversal` / `json_path_concepts_any` | 35 | 0 |
| `v3_code_tenant_isolation` / `cross_tenant_impact` | 28 | 0 |
| `v3_agent_diagnosis_parallel` / `concepts_all` | 25 | 0 |
| `v3_agent_weather_route_parallel` / `concepts_any` | 24 | 0 |
| `v3_validate_stop_after_success` / `concepts_all` | 20 | 0 |
| `v3_code_path_traversal` / `correct_vulnerability` | 20 | 0 |
| `v3_ops_failed_update_rollback` / `json_path_concepts_any` | 16 | 0 |
| `v3_validate_timeout_fallback` / `no_visible_reasoning` | 13 | 0 |
| `v3_validate_stop_after_success` / `no_visible_reasoning` | 13 | 0 |
| `v3_validate_stale_weather` / `no_visible_reasoning` | 13 | 0 |
| `v3_validate_conflict_resolution` / `no_visible_reasoning` | 13 | 0 |
| `v3_syn_policy_revision` / `no_visible_reasoning` | 13 | 0 |
| `v3_syn_noisy_transcript` / `no_visible_reasoning` | 13 | 0 |
| `v3_syn_meeting_decisions` / `no_visible_reasoning` | 13 | 0 |
| `v3_syn_incident_causal_chain` / `no_visible_reasoning` | 13 | 0 |
| `v3_syn_capacity_placement` / `no_visible_reasoning` | 13 | 0 |
| `v3_rag_temporal_conflict` / `no_visible_reasoning` | 13 | 0 |
| `v3_rag_evidence_exact` / `no_visible_reasoning` | 13 | 0 |
| `v3_rag_abstain_missing_evidence` / `no_visible_reasoning` | 13 | 0 |
| `v3_ops_failed_update_rollback` / `no_visible_reasoning` | 13 | 0 |
| `v3_code_tenant_isolation` / `no_visible_reasoning` | 13 | 0 |
| `v3_code_path_traversal` / `no_visible_reasoning` | 13 | 0 |
| `v3_agent_weather_route_parallel` / `no_visible_reasoning` | 13 | 0 |
| `v3_agent_top3_search_fusion` / `no_visible_reasoning` | 13 | 0 |
| `v3_agent_public_private_reconciliation` / `no_visible_reasoning` | 13 | 0 |
| `v3_agent_diagnosis_parallel` / `no_visible_reasoning` | 13 | 0 |
| `v3_agent_approval_restart_recovery` / `no_visible_reasoning` | 13 | 0 |
| `v3_syn_policy_revision` / `json_path_concepts_any` | 12 | 0 |
| `v3_code_path_traversal` / `canonical_containment_fix` | 11 | 0 |
| `v3_syn_policy_revision` / `json_path_concepts_all` | 7 | 0 |
| `v3_agent_diagnosis_parallel` / `concepts_any` | 7 | 0 |
| `v3_code_tenant_isolation` / `json_path_concepts_all` | 4 | 0 |
| `v3_rag_temporal_conflict` / `json_path_concepts_all` | 2 | 0 |
| `v3_validate_conflict_resolution` / `safe_decision` | 1 | 0 |
| `v3_syn_noisy_transcript` / `json_path_concepts_all` | 1 | 0 |

## Interpretation guardrails

- v3.1 is a new evaluation version; it does not overwrite the published v3 result files.
- Score changes mean the evaluator changed, not the models or their latency.
- Repeated runs remain separate observations. Exact duplicate copies are counted once.
- Incomplete runs are listed in the audit JSON and excluded from all scores.
- The complete per-run and per-case audit is stored in the companion JSON file.
