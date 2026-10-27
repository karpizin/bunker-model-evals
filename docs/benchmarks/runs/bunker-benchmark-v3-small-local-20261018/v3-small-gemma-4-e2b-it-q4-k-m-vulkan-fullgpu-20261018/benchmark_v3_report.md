# Bunker Benchmark v3

Generated: `2026-10-19T04:56:57`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-E2B-it-Q4_K_M` | 1 | 71.70% | 71.70% | 0.00 | 71.70% | 0 | 21 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `gemma-4-E2B-it-Q4_K_M` | 1 | 71.70% | 0 | 21 | no | agent_execution 55.6%; code_ops 66.1%; grounded_rag 87.7%; result_validation 74.2%; synthesis 74.8% |

## Case results

### gemma-4-E2B-it-Q4_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 1.61s |
| `v3_syn_meeting_decisions` | synthesis | hard | 83.3% | stop |  | 1.16s |
| `v3_syn_capacity_placement` | synthesis | hard | 30.8% | stop | structured_answer, unique_valid_placement | 6.45s |
| `v3_syn_policy_revision` | synthesis | hard | 100.0% | stop |  | 2.36s |
| `v3_syn_noisy_transcript` | synthesis | hard | 60.0% | stop | confirmed_actions_only | 1.38s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 82.1% | stop,stop | check_8:final_answer_present | 2.99s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 72.0% | stop,stop | check_6:final_answer_present | 1.76s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 53.8% | stop | complete_parallel_diagnosis | 1.21s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 43.3% | stop,stop | safe_mutation_sequence, approval_token_forwarded | 0.85s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 26.9% | stop | top3_relevant_tools_only, correct_public_local_fusion, check_6:final_answer_present | 1.85s |
| `v3_validate_stale_weather` | result_validation | hard | 56.5% | stop,stop | detect_and_refresh_stale_data, check_6:final_answer_present | 0.95s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | stop,stop |  | 0.63s |
| `v3_validate_timeout_fallback` | result_validation | hard | 52.2% | stop,stop | fallback_after_primary_failure, honest_freshness_limit | 1.29s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 88.0% | stop,stop,stop | safe_decision | 1.60s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 0.53s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 92.3% | stop |  | 0.82s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 70.8% | stop |  | 2.02s |
| `v3_code_path_traversal` | code_ops | hard | 69.6% | stop | canonical_containment_fix | 1.99s |
| `v3_code_tenant_isolation` | code_ops | hard | 75.0% | stop | cross_tenant_impact, cross_tenant_disclosure | 1.72s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 53.8% | stop | correct_root_cause, safe_recovery_sequence | 3.17s |
