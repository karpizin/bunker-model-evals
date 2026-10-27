# Bunker Benchmark v3

Generated: `2026-10-19T05:21:55`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Qwen3.5-9B-DeepSeek-V4-Flash-MTP-Q4_K_M` | 1 | 79.29% | 79.29% | 0.00 | 79.29% | 2 | 15 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `Qwen3.5-9B-DeepSeek-V4-Flash-MTP-Q4_K_M` | 1 | 79.29% | 2 | 15 | no | agent_execution 93.1%; code_ops 54.8%; grounded_rag 90.3%; result_validation 76.1%; synthesis 82.2% |

## Case results

### Qwen3.5-9B-DeepSeek-V4-Flash-MTP-Q4_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 19.16s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 21.98s |
| `v3_syn_capacity_placement` | synthesis | hard | 100.0% | stop |  | 44.55s |
| `v3_syn_policy_revision` | synthesis | hard | 26.9% | length | structured_answer, check_7:final_answer_present, check_8:answer_not_truncated | 120.08s |
| `v3_syn_noisy_transcript` | synthesis | hard | 84.0% | stop |  | 50.94s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 92.9% | stop,stop |  | 11.99s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 84.0% | stop,stop |  | 11.33s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 100.0% | stop,stop |  | 13.25s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 100.0% | stop,stop,stop,stop |  | 8.66s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 88.5% | stop,stop | check_6:final_answer_present | 21.04s |
| `v3_validate_stale_weather` | result_validation | hard | 82.6% | stop,stop,stop | uses_fresh_result | 11.06s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | stop,stop |  | 3.18s |
| `v3_validate_timeout_fallback` | result_validation | hard | 21.7% | stop,stop,stop,stop | fallback_after_primary_failure, honest_freshness_limit, check_6:final_answer_present | 6.40s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 100.0% | stop,stop,stop |  | 7.12s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 11.28s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 100.0% | stop |  | 20.86s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 70.8% | stop |  | 69.38s |
| `v3_code_path_traversal` | code_ops | hard | 8.7% | length | structured_answer, correct_vulnerability, canonical_containment_fix, check_6:final_answer_present, check_7:answer_not_truncated | 114.22s |
| `v3_code_tenant_isolation` | code_ops | hard | 75.0% | stop | cross_tenant_impact, cross_tenant_disclosure | 26.64s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 80.8% | stop |  | 31.16s |
