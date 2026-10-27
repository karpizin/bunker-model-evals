# Bunker Benchmark v3

Generated: `2026-10-19T04:56:08`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Qwen3-4B-Q5_K_M` | 1 | 74.65% | 74.65% | 0.00 | 74.65% | 1 | 17 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `Qwen3-4B-Q5_K_M` | 1 | 74.65% | 1 | 17 | no | agent_execution 65.9%; code_ops 60.7%; grounded_rag 86.4%; result_validation 81.5%; synthesis 78.7% |

## Case results

### Qwen3-4B-Q5_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 1.88s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 1.43s |
| `v3_syn_capacity_placement` | synthesis | hard | 84.6% | stop |  | 4.23s |
| `v3_syn_policy_revision` | synthesis | hard | 76.9% | stop |  | 5.64s |
| `v3_syn_noisy_transcript` | synthesis | hard | 32.0% | length | structured_answer, confirmed_actions_only, check_7:answer_not_truncated | 148.55s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 75.0% | stop,stop | check_8:final_answer_present | 4.07s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 76.0% | stop,stop |  | 3.54s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 61.5% | stop,stop | check_6:final_answer_present | 4.12s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 90.0% | stop,stop,stop,stop |  | 1.58s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 26.9% | stop | top3_relevant_tools_only, correct_public_local_fusion, check_6:final_answer_present | 1.17s |
| `v3_validate_stale_weather` | result_validation | hard | 52.2% | stop,stop | detect_and_refresh_stale_data, uses_fresh_result | 1.00s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | stop,stop |  | 0.81s |
| `v3_validate_timeout_fallback` | result_validation | hard | 73.9% | stop,stop,stop | honest_freshness_limit | 2.10s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 100.0% | stop,stop |  | 2.41s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 0.63s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 88.5% | stop |  | 0.97s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 70.8% | stop |  | 2.42s |
| `v3_code_path_traversal` | code_ops | hard | 60.9% | stop | correct_vulnerability, canonical_containment_fix | 2.88s |
| `v3_code_tenant_isolation` | code_ops | hard | 75.0% | stop | cross_tenant_impact, cross_tenant_disclosure | 1.08s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 46.2% | stop | correct_root_cause, safe_recovery_sequence | 1.59s |
