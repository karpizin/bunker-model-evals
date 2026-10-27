# Bunker Benchmark v3

Generated: `2026-10-19T05:11:23`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Qwopus3.5-9B-Coder-MTP-Q4_K_M` | 1 | 72.80% | 72.80% | 0.00 | 72.80% | 3 | 21 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `Qwopus3.5-9B-Coder-MTP-Q4_K_M` | 1 | 72.80% | 3 | 21 | no | agent_execution 91.8%; code_ops 45.5%; grounded_rag 91.7%; result_validation 76.1%; synthesis 58.9% |

## Case results

### Qwopus3.5-9B-Coder-MTP-Q4_K_M / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 100.0% | stop |  | 17.76s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 11.04s |
| `v3_syn_capacity_placement` | synthesis | hard | 7.7% | length | structured_answer, unique_valid_placement, check_8:final_answer_present, check_9:answer_not_truncated | 102.97s |
| `v3_syn_policy_revision` | synthesis | hard | 26.9% | length | structured_answer, check_7:final_answer_present, check_8:answer_not_truncated | 105.00s |
| `v3_syn_noisy_transcript` | synthesis | hard | 60.0% | stop | confirmed_actions_only | 28.52s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 75.0% | stop,stop | check_8:final_answer_present | 20.09s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 84.0% | stop,stop |  | 13.74s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 100.0% | stop,stop |  | 9.05s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 100.0% | stop,stop,stop,stop |  | 8.04s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 100.0% | stop,stop |  | 31.76s |
| `v3_validate_stale_weather` | result_validation | hard | 82.6% | stop,stop,stop | uses_fresh_result | 9.90s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | stop,stop |  | 3.16s |
| `v3_validate_timeout_fallback` | result_validation | hard | 21.7% | stop,stop,stop,stop | fallback_after_primary_failure, honest_freshness_limit, check_6:final_answer_present | 8.41s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 100.0% | stop,stop,stop |  | 8.43s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 4.23s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 100.0% | stop |  | 13.73s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 75.0% | stop |  | 18.06s |
| `v3_code_path_traversal` | code_ops | hard | 8.7% | length | structured_answer, correct_vulnerability, canonical_containment_fix, check_6:final_answer_present, check_7:answer_not_truncated | 100.10s |
| `v3_code_tenant_isolation` | code_ops | hard | 62.5% | stop | cross_tenant_impact, cross_tenant_disclosure | 15.05s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 65.4% | stop | safe_recovery_sequence | 18.02s |
