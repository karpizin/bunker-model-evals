# Bunker Benchmark v3

Generated: `2026-10-18T19:27:17`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `deepseek/deepseek-v4-flash` | 1 | 89.51% | 89.51% | 0.00 | 89.51% | 0 | 5 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `deepseek/deepseek-v4-flash` | 1 | 89.51% | 0 | 5 | no | agent_execution 79.5%; code_ops 82.8%; grounded_rag 94.4%; result_validation 92.4%; synthesis 98.5% |

## Case results

### deepseek/deepseek-v4-flash / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 13.11s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 12.59s |
| `v3_syn_capacity_placement` | synthesis | hard | 92.3% | stop |  | 15.04s |
| `v3_syn_policy_revision` | synthesis | hard | 100.0% | stop |  | 3.74s |
| `v3_syn_noisy_transcript` | synthesis | hard | 100.0% | stop |  | 2.06s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 75.0% | stop,stop | complete_tool_selection | 5.02s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 84.0% | stop,stop |  | 25.72s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 100.0% | stop,stop |  | 26.80s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 100.0% | stop,stop,stop,stop |  | 29.54s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 38.5% | stop,stop | top3_relevant_tools_only, correct_public_local_fusion | 25.19s |
| `v3_validate_stale_weather` | result_validation | hard | 82.6% | stop,stop,stop | uses_fresh_result | 27.25s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | stop,stop |  | 24.67s |
| `v3_validate_timeout_fallback` | result_validation | hard | 87.0% | stop,stop,stop |  | 3.88s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 100.0% | stop,stop,stop |  | 27.91s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 14.14s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 100.0% | stop |  | 14.50s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 83.3% | stop |  | 12.85s |
| `v3_code_path_traversal` | code_ops | hard | 91.3% | stop |  | 12.76s |
| `v3_code_tenant_isolation` | code_ops | hard | 91.7% | stop |  | 4.76s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 65.4% | stop | safe_recovery_sequence | 8.35s |
