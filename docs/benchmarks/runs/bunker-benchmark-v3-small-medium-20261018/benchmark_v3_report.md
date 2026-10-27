# Bunker Benchmark v3

Generated: `2026-10-19T03:04:52`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Phi-4-mini-instruct-Q5_K_M` | 1 | 67.22% | 67.22% | 0.00 | 67.22% | 0 | 16 | 0/1 |
| `Qwen3.5-4B-Q5_K_M` | 1 | 78.21% | 78.21% | 0.00 | 78.21% | 0 | 12 | 0/1 |
| `Qwen3.5-9B-Q5_K_M` | 1 | 85.57% | 85.57% | 0.00 | 85.57% | 0 | 7 | 0/1 |
| `Qwen3-14B-Q4_K_M` | 1 | 85.86% | 85.86% | 0.00 | 85.86% | 0 | 7 | 0/1 |
| `Qwen3.8-27B-Q4_K_M` | 1 | 90.49% | 90.49% | 0.00 | 90.49% | 0 | 4 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `Phi-4-mini-instruct-Q5_K_M` | 1 | 67.22% | 0 | 16 | no | agent_execution 77.3%; code_ops 54.2%; grounded_rag 80.8%; result_validation 63.1%; synthesis 60.7% |
| `Qwen3.5-4B-Q5_K_M` | 1 | 78.21% | 0 | 12 | no | agent_execution 77.2%; code_ops 66.1%; grounded_rag 91.9%; result_validation 68.5%; synthesis 87.3% |
| `Qwen3.5-9B-Q5_K_M` | 1 | 85.57% | 0 | 7 | no | agent_execution 93.1%; code_ops 66.1%; grounded_rag 90.3%; result_validation 87.0%; synthesis 91.4% |
| `Qwen3-14B-Q4_K_M` | 1 | 85.86% | 0 | 7 | no | agent_execution 81.9%; code_ops 73.4%; grounded_rag 94.4%; result_validation 85.9%; synthesis 93.7% |
| `Qwen3.8-27B-Q4_K_M` | 1 | 90.49% | 0 | 4 | no | agent_execution 93.4%; code_ops 81.8%; grounded_rag 94.4%; result_validation 85.9%; synthesis 96.9% |

## Case results

### Phi-4-mini-instruct-Q5_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 83.3% | stop |  | 1.68s |
| `v3_syn_meeting_decisions` | synthesis | hard | 33.3% | stop | structured_answer, accepted_decisions_only | 0.95s |
| `v3_syn_capacity_placement` | synthesis | hard | 69.2% | stop |  | 1.59s |
| `v3_syn_policy_revision` | synthesis | hard | 65.4% | stop |  | 2.84s |
| `v3_syn_noisy_transcript` | synthesis | hard | 52.0% | stop | confirmed_actions_only | 1.91s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 92.9% | stop,stop |  | 3.52s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 76.0% | stop,stop |  | 2.25s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 73.1% | stop,stop |  | 2.86s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 60.0% | stop,stop,stop | safe_mutation_sequence | 1.14s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 84.6% | stop,stop | correct_public_local_fusion | 4.42s |
| `v3_validate_stale_weather` | result_validation | hard | 43.5% | stop,stop | detect_and_refresh_stale_data, uses_fresh_result | 0.81s |
| `v3_validate_stop_after_success` | result_validation | hard | 87.0% | stop,stop |  | 0.70s |
| `v3_validate_timeout_fallback` | result_validation | hard | 73.9% | stop,stop | honest_freshness_limit | 1.86s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 48.0% | stop,stop | resolve_conflict, safe_decision | 1.48s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 78.3% | stop | exact_evidence | 0.48s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 80.8% | stop |  | 0.49s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 83.3% | stop |  | 1.47s |
| `v3_code_path_traversal` | code_ops | hard | 43.5% | stop | correct_vulnerability, canonical_containment_fix | 1.61s |
| `v3_code_tenant_isolation` | code_ops | hard | 50.0% | stop | cross_tenant_disclosure, tenant_scoped_query | 2.72s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 69.2% | stop | correct_root_cause | 3.83s |

### Qwen3.5-4B-Q5_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 2.56s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 1.67s |
| `v3_syn_capacity_placement` | synthesis | hard | 84.6% | stop |  | 6.27s |
| `v3_syn_policy_revision` | synthesis | hard | 100.0% | stop |  | 6.02s |
| `v3_syn_noisy_transcript` | synthesis | hard | 52.0% | stop | confirmed_actions_only | 2.92s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 92.9% | stop,stop |  | 3.37s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 84.0% | stop,stop |  | 3.13s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 80.8% | stop,stop |  | 3.43s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 90.0% | stop,stop,stop |  | 2.27s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 38.5% | stop,stop | top3_relevant_tools_only, correct_public_local_fusion | 7.66s |
| `v3_validate_stale_weather` | result_validation | hard | 43.5% | stop,stop | detect_and_refresh_stale_data, uses_fresh_result | 1.52s |
| `v3_validate_stop_after_success` | result_validation | hard | 87.0% | stop,stop |  | 1.01s |
| `v3_validate_timeout_fallback` | result_validation | hard | 43.5% | stop,stop,stop | fallback_after_primary_failure, honest_freshness_limit | 3.29s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 100.0% | stop,stop,stop |  | 2.99s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 1.33s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 92.3% | stop |  | 1.41s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 83.3% | stop |  | 2.68s |
| `v3_code_path_traversal` | code_ops | hard | 69.6% | stop | canonical_containment_fix | 3.63s |
| `v3_code_tenant_isolation` | code_ops | hard | 75.0% | stop | cross_tenant_impact, cross_tenant_disclosure | 1.45s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 53.8% | stop | correct_root_cause, safe_recovery_sequence | 6.90s |

### Qwen3.5-9B-Q5_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 4.55s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 2.89s |
| `v3_syn_capacity_placement` | synthesis | hard | 84.6% | stop |  | 3.23s |
| `v3_syn_policy_revision` | synthesis | hard | 88.5% | stop |  | 7.37s |
| `v3_syn_noisy_transcript` | synthesis | hard | 84.0% | stop |  | 4.25s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 92.9% | stop,stop |  | 5.18s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 84.0% | stop,stop |  | 7.94s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 100.0% | stop,stop |  | 6.13s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 100.0% | stop,stop,stop,stop |  | 4.35s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 88.5% | stop,stop | check_6:final_answer_present | 12.64s |
| `v3_validate_stale_weather` | result_validation | hard | 69.6% | stop,stop,stop,stop | check_6:final_answer_present | 7.63s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | stop,stop |  | 1.65s |
| `v3_validate_timeout_fallback` | result_validation | hard | 78.3% | stop,stop,stop,stop |  | 6.16s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 100.0% | stop,stop,stop |  | 5.28s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 1.53s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 100.0% | stop |  | 4.12s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 70.8% | stop |  | 6.30s |
| `v3_code_path_traversal` | code_ops | hard | 69.6% | stop | canonical_containment_fix | 6.07s |
| `v3_code_tenant_isolation` | code_ops | hard | 75.0% | stop | cross_tenant_impact, cross_tenant_disclosure | 1.70s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 53.8% | stop | correct_root_cause, safe_recovery_sequence | 5.44s |

### Qwen3-14B-Q4_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 6.68s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 5.33s |
| `v3_syn_capacity_placement` | synthesis | hard | 92.3% | stop |  | 4.46s |
| `v3_syn_policy_revision` | synthesis | hard | 92.3% | stop |  | 16.35s |
| `v3_syn_noisy_transcript` | synthesis | hard | 84.0% | stop |  | 5.27s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 85.7% | stop,stop |  | 7.47s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 76.0% | stop,stop |  | 9.07s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 73.1% | stop,stop |  | 6.99s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 90.0% | stop,stop,stop,stop |  | 4.39s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 84.6% | stop,stop | correct_public_local_fusion | 10.27s |
| `v3_validate_stale_weather` | result_validation | hard | 69.6% | stop,stop | detect_and_refresh_stale_data | 3.10s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | stop,stop |  | 2.38s |
| `v3_validate_timeout_fallback` | result_validation | hard | 73.9% | stop,stop,stop | honest_freshness_limit | 8.63s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 100.0% | stop,stop |  | 7.46s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 2.19s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 100.0% | stop |  | 3.33s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 83.3% | stop |  | 7.23s |
| `v3_code_path_traversal` | code_ops | hard | 91.3% | stop |  | 6.55s |
| `v3_code_tenant_isolation` | code_ops | hard | 75.0% | stop | cross_tenant_impact, cross_tenant_disclosure | 5.08s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 53.8% | stop | correct_root_cause, safe_recovery_sequence | 13.42s |

### Qwen3.8-27B-Q4_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 15.05s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 14.15s |
| `v3_syn_capacity_placement` | synthesis | hard | 84.6% | stop |  | 15.52s |
| `v3_syn_policy_revision` | synthesis | hard | 100.0% | stop |  | 29.66s |
| `v3_syn_noisy_transcript` | synthesis | hard | 100.0% | stop |  | 12.68s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 92.9% | stop,stop |  | 20.15s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 84.0% | stop,stop |  | 19.09s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 100.0% | stop,stop |  | 18.11s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 90.0% | stop,stop,stop,stop |  | 14.04s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 100.0% | stop,stop |  | 21.09s |
| `v3_validate_stale_weather` | result_validation | hard | 52.2% | stop,stop | detect_and_refresh_stale_data, uses_fresh_result | 9.07s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | stop,stop |  | 5.79s |
| `v3_validate_timeout_fallback` | result_validation | hard | 91.3% | stop,stop,stop,stop |  | 19.05s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 100.0% | stop,stop,stop |  | 16.45s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 6.21s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 100.0% | stop |  | 10.68s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 83.3% | stop |  | 25.35s |
| `v3_code_path_traversal` | code_ops | hard | 100.0% | stop |  | 20.75s |
| `v3_code_tenant_isolation` | code_ops | hard | 91.7% | stop |  | 12.93s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 53.8% | stop | correct_root_cause, safe_recovery_sequence | 38.22s |
