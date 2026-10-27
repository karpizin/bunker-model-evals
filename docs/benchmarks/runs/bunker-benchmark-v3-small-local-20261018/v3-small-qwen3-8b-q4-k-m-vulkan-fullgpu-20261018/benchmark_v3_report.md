# Bunker Benchmark v3

Generated: `2026-10-19T05:00:43`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Qwen3-8B-Q4_K_M` | 1 | 81.43% | 81.43% | 0.00 | 81.43% | 0 | 11 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `Qwen3-8B-Q4_K_M` | 1 | 81.43% | 0 | 11 | no | agent_execution 77.3%; code_ops 70.5%; grounded_rag 90.6%; result_validation 81.5%; synthesis 87.3% |

## Case results

### Qwen3-8B-Q4_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 91.7% | stop |  | 3.53s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 3.13s |
| `v3_syn_capacity_placement` | synthesis | hard | 84.6% | stop |  | 3.16s |
| `v3_syn_policy_revision` | synthesis | hard | 100.0% | stop |  | 8.20s |
| `v3_syn_noisy_transcript` | synthesis | hard | 60.0% | stop | confirmed_actions_only | 3.12s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 85.7% | stop,stop |  | 5.41s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 76.0% | stop,stop |  | 3.69s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 42.3% | stop | complete_parallel_diagnosis, check_6:final_answer_present | 1.54s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 90.0% | stop,stop,stop |  | 2.20s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 92.3% | stop,stop |  | 4.55s |
| `v3_validate_stale_weather` | result_validation | hard | 52.2% | stop,stop | detect_and_refresh_stale_data, uses_fresh_result | 1.85s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | stop,stop |  | 0.94s |
| `v3_validate_timeout_fallback` | result_validation | hard | 73.9% | stop,stop,stop | honest_freshness_limit | 3.84s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 100.0% | stop,stop,stop |  | 3.70s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 0.98s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 88.5% | stop |  | 1.51s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 83.3% | stop |  | 5.53s |
| `v3_code_path_traversal` | code_ops | hard | 82.6% | stop | correct_vulnerability | 3.15s |
| `v3_code_tenant_isolation` | code_ops | hard | 75.0% | stop | cross_tenant_impact, cross_tenant_disclosure | 1.81s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 53.8% | stop | correct_root_cause, safe_recovery_sequence | 7.77s |
