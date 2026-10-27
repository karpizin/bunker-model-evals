# Bunker Benchmark v3

Generated: `2026-10-19T05:02:05`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-E4B-it-Q5_K_M` | 1 | 83.67% | 83.67% | 0.00 | 83.67% | 0 | 9 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `gemma-4-E4B-it-Q5_K_M` | 1 | 83.67% | 0 | 9 | no | agent_execution 84.1%; code_ops 79.8%; grounded_rag 90.3%; result_validation 75.3%; synthesis 88.8% |

## Case results

### gemma-4-E4B-it-Q5_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 2.70s |
| `v3_syn_meeting_decisions` | synthesis | hard | 83.3% | stop |  | 2.53s |
| `v3_syn_capacity_placement` | synthesis | hard | 84.6% | stop |  | 4.37s |
| `v3_syn_policy_revision` | synthesis | hard | 92.3% | stop |  | 5.74s |
| `v3_syn_noisy_transcript` | synthesis | hard | 84.0% | stop |  | 2.97s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 85.7% | stop,stop |  | 6.18s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 60.0% | stop,stop,stop | reconcile_both_sources | 4.08s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 100.0% | stop,stop |  | 6.39s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 90.0% | stop,stop,stop |  | 2.28s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 84.6% | stop,stop | correct_public_local_fusion | 5.96s |
| `v3_validate_stale_weather` | result_validation | hard | 43.5% | stop,stop | detect_and_refresh_stale_data, uses_fresh_result | 2.31s |
| `v3_validate_stop_after_success` | result_validation | hard | 87.0% | stop,stop |  | 1.13s |
| `v3_validate_timeout_fallback` | result_validation | hard | 87.0% | stop,stop,stop | honest_freshness_limit | 3.13s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 84.0% | stop,stop,stop,stop | compare_independent_sources | 3.41s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 1.36s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 100.0% | stop |  | 1.48s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 70.8% | stop |  | 3.68s |
| `v3_code_path_traversal` | code_ops | hard | 91.3% | stop |  | 2.39s |
| `v3_code_tenant_isolation` | code_ops | hard | 75.0% | stop | cross_tenant_impact, cross_tenant_disclosure | 2.02s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 73.1% | stop | safe_recovery_sequence | 7.15s |
