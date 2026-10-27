# Bunker Benchmark v3

Generated: `2026-10-18T19:28:22`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `openai/gpt-5.4-nano` | 1 | 83.35% | 83.35% | 0.00 | 83.35% | 0 | 9 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `openai/gpt-5.4-nano` | 1 | 83.35% | 0 | 9 | no | agent_execution 91.8%; code_ops 75.1%; grounded_rag 94.4%; result_validation 69.8%; synthesis 85.6% |

## Case results

### openai/gpt-5.4-nano / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 83.3% | stop |  | 1.88s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 1.78s |
| `v3_syn_capacity_placement` | synthesis | hard | 84.6% | stop |  | 1.86s |
| `v3_syn_policy_revision` | synthesis | hard | 100.0% | stop |  | 3.24s |
| `v3_syn_noisy_transcript` | synthesis | hard | 60.0% | stop | confirmed_actions_only | 1.85s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 75.0% | stop,stop | complete_tool_selection | 3.67s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 84.0% | stop,stop |  | 3.21s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 100.0% | stop,stop |  | 4.78s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 100.0% | stop,stop,stop |  | 4.04s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 100.0% | stop,stop |  | 5.95s |
| `v3_validate_stale_weather` | result_validation | hard | 69.6% | stop,stop | detect_and_refresh_stale_data | 3.41s |
| `v3_validate_stop_after_success` | result_validation | hard | 30.4% | stop | stop_after_valid_result, check_5:final_answer_present | 1.30s |
| `v3_validate_timeout_fallback` | result_validation | hard | 91.3% | stop,stop,stop |  | 4.06s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 88.0% | stop,stop,stop | safe_decision | 3.36s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 1.50s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 100.0% | stop |  | 1.63s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 83.3% | stop |  | 1.93s |
| `v3_code_path_traversal` | code_ops | hard | 52.2% | stop | correct_vulnerability, canonical_containment_fix | 2.94s |
| `v3_code_tenant_isolation` | code_ops | hard | 100.0% | stop |  | 2.14s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 73.1% | stop | safe_recovery_sequence | 4.80s |
