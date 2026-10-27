# Bunker Benchmark v3

Generated: `2026-10-18T19:22:02`
Suite: `bunker_benchmark_v3_discriminative_20261018`

> Contract compliance and runtime performance are reported separately and are not folded into this capability score.

## Repeated-run summary

| Model | Runs | Mean | Median | Std dev | Worst | Truncated | Critical failures | Eligible runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `google/gemini-3.8-flash` | 1 | 93.01% | 93.01% | 0.00 | 93.01% | 0 | 2 | 0/1 |

## Per-run tracks

| Model | Run | Capability mean | Truncated | Critical failures | Eligible | Track scores |
|---|---:|---:|---:|---:|---|---|
| `google/gemini-3.8-flash` | 1 | 93.01% | 0 | 2 | no | agent_execution 94.8%; code_ops 85.5%; grounded_rag 94.4%; result_validation 96.7%; synthesis 93.6% |

## Case results

### google/gemini-3.8-flash / run 1

| Case | Track | Difficulty | Score | Finish | Critical failures | Latency |
|---|---|---|---:|---|---|---:|
| `v3_syn_incident_causal_chain` | synthesis | hard | 83.3% | stop |  | 3.48s |
| `v3_syn_meeting_decisions` | synthesis | hard | 100.0% | stop |  | 5.79s |
| `v3_syn_capacity_placement` | synthesis | hard | 100.0% | stop |  | 5.54s |
| `v3_syn_policy_revision` | synthesis | hard | 84.6% | stop |  | 4.40s |
| `v3_syn_noisy_transcript` | synthesis | hard | 100.0% | stop |  | 1.83s |
| `v3_agent_weather_route_parallel` | agent_execution | hard | 100.0% | error,stop |  | 6.48s |
| `v3_agent_public_private_reconciliation` | agent_execution | hard | 84.0% | error,stop |  | 16.25s |
| `v3_agent_diagnosis_parallel` | agent_execution | extreme | 100.0% | error,stop |  | 5.53s |
| `v3_agent_approval_restart_recovery` | agent_execution | extreme | 90.0% | stop,stop,stop,stop |  | 17.19s |
| `v3_agent_top3_search_fusion` | agent_execution | extreme | 100.0% | stop,stop |  | 16.16s |
| `v3_validate_stale_weather` | result_validation | hard | 100.0% | error,stop,stop |  | 6.90s |
| `v3_validate_stop_after_success` | result_validation | hard | 100.0% | error,stop |  | 5.35s |
| `v3_validate_timeout_fallback` | result_validation | hard | 87.0% | stop,stop,stop |  | 9.52s |
| `v3_validate_conflict_resolution` | result_validation | extreme | 100.0% | error,stop,stop |  | 19.48s |
| `v3_rag_evidence_exact` | grounded_rag | hard | 100.0% | stop |  | 1.69s |
| `v3_rag_abstain_missing_evidence` | grounded_rag | hard | 100.0% | stop |  | 6.97s |
| `v3_rag_temporal_conflict` | grounded_rag | extreme | 83.3% | stop |  | 3.54s |
| `v3_code_path_traversal` | code_ops | hard | 100.0% | stop |  | 19.49s |
| `v3_code_tenant_isolation` | code_ops | hard | 83.3% | stop | cross_tenant_disclosure | 8.10s |
| `v3_ops_failed_update_rollback` | code_ops | extreme | 73.1% | stop | safe_recovery_sequence | 3.58s |
