# Bunker Benchmark v3

Generated: `2026-10-19T04:51:56`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Llama-3.2-3B-Instruct-Q5_K_M` | 1 | 56.79% | 56.79% | 0.00 | 56.79% | 0 | 29 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `Llama-3.2-3B-Instruct-Q5_K_M` | 1 | 56.79% | 0 | 29 | no | agent_execution 36.6%; code_ops 56.2%; grounded_rag 68.8%; result_validation 63.1%; synthesis 59.3% |

## Case results

### Llama-3.2-3B-Instruct-Q5_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 62.5% | stop | correct_root_cause | 1.17s |
| `v3_syn_meeting_decisions` | synthesis | hard | 66.7% | stop | accepted_decisions_only | 2.10s |
| `v3_syn_capacity_placement` | synthesis | hard | 53.8% | stop | unique_valid_placement | 1.95s |
| `v3_syn_policy_revision` | synthesis | hard | 61.5% | stop | correct_policy_decision | 3.80s |
| `v3_syn_noisy_transcript` | synthesis | hard | 52.0% | stop | confirmed_actions_only | 2.49s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 35.7% | stop,stop | complete_tool_selection, uses_returned_facts | 1.26s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 60.0% | stop,stop | reconcile_both_sources | 1.07s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 34.6% | stop,stop,stop | complete_parallel_diagnosis, check_6:final_answer_present | 0.80s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 33.3% | stop,stop,stop | safe_mutation_sequence, approval_token_forwarded | 1.23s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 19.2% | stop,stop,stop | top3_relevant_tools_only, correct_public_local_fusion, check_6:final_answer_present | 1.84s |
| `v3_validate_stale_weather` | result_validation | hard | 43.5% | stop,stop | detect_and_refresh_stale_data, uses_fresh_result | 0.70s |
| `v3_validate_stop_after_success` | result_validation | hard | 87.0% | stop,stop |  | 0.45s |
| `v3_validate_timeout_fallback` | result_validation | hard | 73.9% | stop,stop,stop | honest_freshness_limit | 1.17s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 48.0% | stop,stop | compare_independent_sources, safe_decision | 0.67s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 0.44s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 73.1% | stop | correct_abstention | 0.76s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 33.3% | stop | structured_answer, correct_effective_limit | 1.41s |
| `v3_code_path_traversal` | code_ops | hard | 52.2% | stop | correct_vulnerability, canonical_containment_fix | 2.20s |
| `v3_code_tenant_isolation` | code_ops | hard | 62.5% | stop | cross_tenant_impact, cross_tenant_disclosure | 1.40s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 53.8% | stop | correct_root_cause, safe_recovery_sequence | 1.52s |
