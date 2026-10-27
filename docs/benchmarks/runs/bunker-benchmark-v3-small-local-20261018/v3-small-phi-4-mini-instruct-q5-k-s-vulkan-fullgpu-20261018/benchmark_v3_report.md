# Bunker Benchmark v3

Generated: `2026-10-19T04:52:46`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Phi-4-mini-instruct-Q5_K_S` | 1 | 56.70% | 56.70% | 0.00 | 56.70% | 0 | 30 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `Phi-4-mini-instruct-Q5_K_S` | 1 | 56.70% | 0 | 30 | no | agent_execution 37.8%; code_ops 54.9%; grounded_rag 71.1%; result_validation 56.1%; synthesis 63.7% |

## Case results

### Phi-4-mini-instruct-Q5_K_S / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 83.3% | stop |  | 1.51s |
| `v3_syn_meeting_decisions` | synthesis | hard | 33.3% | stop | structured_answer, accepted_decisions_only | 0.92s |
| `v3_syn_capacity_placement` | synthesis | hard | 84.6% | stop |  | 2.37s |
| `v3_syn_policy_revision` | synthesis | hard | 65.4% | stop |  | 2.31s |
| `v3_syn_noisy_transcript` | synthesis | hard | 52.0% | stop | confirmed_actions_only | 2.15s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 17.9% | stop,stop,stop | complete_tool_selection, uses_returned_facts, check_8:final_answer_present | 5.74s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 56.0% | stop,stop,stop | no_unrequested_mutation | 3.32s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 34.6% | stop,stop,stop | complete_parallel_diagnosis, check_6:final_answer_present | 1.09s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 53.3% | stop,stop,stop,stop,stop | approval_token_forwarded, check_8:final_answer_present | 2.85s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 26.9% | stop,stop | top3_relevant_tools_only, correct_public_local_fusion, check_6:final_answer_present | 5.24s |
| `v3_validate_stale_weather` | result_validation | hard | 43.5% | stop,stop | detect_and_refresh_stale_data, uses_fresh_result | 0.84s |
| `v3_validate_stop_after_success` | result_validation | hard | 87.0% | stop,stop | check_5:final_answer_present | 0.69s |
| `v3_validate_timeout_fallback` | result_validation | hard | 73.9% | stop,stop | check_6:final_answer_present | 2.45s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 20.0% | stop,stop | compare_independent_sources, resolve_conflict, safe_decision, check_6:final_answer_present | 1.04s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 78.3% | stop | exact_evidence | 0.46s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 80.8% | stop |  | 0.64s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 54.2% | stop | correct_effective_limit | 2.52s |
| `v3_code_path_traversal` | code_ops | hard | 43.5% | stop | correct_vulnerability, canonical_containment_fix | 1.17s |
| `v3_code_tenant_isolation` | code_ops | hard | 75.0% | stop | cross_tenant_impact, cross_tenant_disclosure | 1.15s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 46.2% | stop | correct_root_cause, safe_recovery_sequence | 3.25s |
