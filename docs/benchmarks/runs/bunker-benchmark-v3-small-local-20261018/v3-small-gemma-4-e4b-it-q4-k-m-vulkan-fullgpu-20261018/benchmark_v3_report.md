# Bunker Benchmark v3

Generated: `2026-10-19T04:58:18`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-E4B-it-Q4_K_M` | 1 | 86.76% | 86.76% | 0.00 | 86.76% | 0 | 8 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `gemma-4-E4B-it-Q4_K_M` | 1 | 86.76% | 0 | 8 | no | agent_execution 85.5%; code_ops 69.2%; grounded_rag 94.4%; result_validation 92.7%; synthesis 91.9% |

## Case results

### gemma-4-E4B-it-Q4_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 2.48s |
| `v3_syn_meeting_decisions` | synthesis | hard | 83.3% | stop |  | 2.27s |
| `v3_syn_capacity_placement` | synthesis | hard | 92.3% | stop |  | 5.13s |
| `v3_syn_policy_revision` | synthesis | hard | 100.0% | stop |  | 6.01s |
| `v3_syn_noisy_transcript` | synthesis | hard | 84.0% | stop |  | 2.65s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 92.9% | stop,stop |  | 6.00s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 60.0% | stop,stop,stop | reconcile_both_sources | 3.97s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 100.0% | stop,stop |  | 6.39s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 90.0% | stop,stop,stop,stop |  | 2.31s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 84.6% | stop,stop | correct_public_local_fusion | 7.59s |
| `v3_validate_stale_weather` | result_validation | hard | 100.0% | stop,stop,stop |  | 1.96s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | stop,stop |  | 1.06s |
| `v3_validate_timeout_fallback` | result_validation | hard | 87.0% | stop,stop,stop | honest_freshness_limit | 2.87s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 84.0% | stop,stop,stop,stop | compare_independent_sources | 3.08s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 1.34s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 100.0% | stop |  | 1.40s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 83.3% | stop |  | 2.69s |
| `v3_code_path_traversal` | code_ops | hard | 91.3% | stop |  | 3.34s |
| `v3_code_tenant_isolation` | code_ops | hard | 62.5% | stop | cross_tenant_impact, cross_tenant_disclosure | 1.71s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 53.8% | stop | correct_root_cause, safe_recovery_sequence | 5.86s |
