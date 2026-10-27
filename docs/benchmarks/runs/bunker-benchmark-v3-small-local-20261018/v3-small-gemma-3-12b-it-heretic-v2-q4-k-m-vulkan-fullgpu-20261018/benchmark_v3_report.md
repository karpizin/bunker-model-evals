# Bunker Benchmark v3

Generated: `2026-10-19T05:24:33`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-3-12b-it-heretic-v2-Q4_K_M` | 1 | 65.72% | 65.72% | 0.00 | 65.72% | 0 | 21 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `gemma-3-12b-it-heretic-v2-Q4_K_M` | 1 | 65.72% | 0 | 21 | no | agent_execution 55.6%; code_ops 63.3%; grounded_rag 80.0%; result_validation 69.1%; synthesis 60.5% |

## Case results

### gemma-3-12b-it-heretic-v2-Q4_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 83.3% | stop |  | 5.22s |
| `v3_syn_meeting_decisions` | synthesis | hard | 75.0% | stop | accepted_decisions_only | 5.60s |
| `v3_syn_capacity_placement` | synthesis | hard | 46.2% | stop | unique_valid_placement | 3.83s |
| `v3_syn_policy_revision` | synthesis | hard | 46.2% | stop | correct_policy_decision | 7.56s |
| `v3_syn_noisy_transcript` | synthesis | hard | 52.0% | stop | confirmed_actions_only | 5.97s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 78.6% | stop,stop,stop |  | 7.33s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 48.0% | stop | reconcile_both_sources, check_6:final_answer_present | 1.73s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 34.6% | stop,stop,stop | complete_parallel_diagnosis, check_6:final_answer_present | 3.81s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 90.0% | stop,stop,stop,stop |  | 5.15s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 26.9% | stop | top3_relevant_tools_only, correct_public_local_fusion, check_6:final_answer_present | 2.94s |
| `v3_validate_stale_weather` | result_validation | hard | 43.5% | stop,stop | detect_and_refresh_stale_data, uses_fresh_result | 2.77s |
| `v3_validate_stop_after_success` | result_validation | hard | 87.0% | stop,stop |  | 2.75s |
| `v3_validate_timeout_fallback` | result_validation | hard | 73.9% | stop,stop,stop | honest_freshness_limit | 4.21s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 72.0% | stop,stop,stop,stop | compare_independent_sources, safe_decision | 6.51s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 2.21s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 69.2% | stop | correct_abstention | 3.27s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 70.8% | stop |  | 3.88s |
| `v3_code_path_traversal` | code_ops | hard | 52.2% | stop | correct_vulnerability, canonical_containment_fix | 6.87s |
| `v3_code_tenant_isolation` | code_ops | hard | 91.7% | stop |  | 4.29s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 46.2% | stop | correct_root_cause, safe_recovery_sequence | 9.09s |
