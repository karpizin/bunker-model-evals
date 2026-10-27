# OpenClaw Model Regression Master Table — 2026-05-03

This document consolidates the model regression results collected on the `mac mini` OpenClaw runtime using the current `assistant_regression_v1` suite.

It is meant to be the canonical reference for:
- hosted model ranking
- local model ranking
- obvious keep / experimental / drop decisions
- special compatibility experiments that are not directly comparable to the full suite

## Scope

- assistant runtime: `OpenClaw`
- benchmark suite: `assistant_regression_v1`
- date range: `2026-05-03` to `2026-05-04`
- environment: `mac mini`

Most of the comparable runs below use the current semantic-router / live-context policy path. Some older exploratory runs still matter historically, but the tables below favor the latest comparable full-suite result per model.

Scores in this document now use the taxonomy-aware rescoring pass:
- blocked tool attempts caused purely by policy are not treated the same as successful bad tool detours
- summaries distinguish `policy_friction`, `tool_env_fail`, and `model_fail`
- this makes the table a better reflection of model behavior inside the stack, rather than a harsher reading of every blocked attempt

## Post-Orchestration Reruns (Selected Mid-Tier Models)

After the `execution_mode` routing refactor and taxonomy-aware scorer update, we re-ran a focused set of previously middling hosted models to see which gains were real and which were mostly benchmark interpretation changes.

| Model | Old score | Old pass | Old latency | New score | New pass | New latency | Delta score | Delta pass | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `qwen/qwen3.6-plus` | `0.934` | `8/10` | `74.1s` | `0.970` | `9/10` | `62.1s` | `+0.036` | `+1` | Biggest win was cleaner routing on web/news plus less punitive scoring of blocked detours. |
| `xiaomi/mimo-v2.5-pro` | `0.932` | `7/10` | `58.8s` | `1.000` | `10/10` | `54.1s` | `+0.068` | `+3` | The clearest example that orchestration, not raw model weakness, was suppressing results. |
| `nvidia/nemotron-3-super-120b-a12b:free` | `0.912` | `7/10` | `160.8s` | `0.909` | `7/10` | `169.9s` | `-0.003` | `+0` | Quality stayed roughly flat; latency remains the main reason not to promote it. |
| `minimax/minimax-m2.7` | `0.883` | `7/10` | `56.2s` | `0.920` | `8/10` | `61.2s` | `+0.037` | `+1` | Improved materially once weather/search misroutes were reduced. |
| `openai/gpt-oss-120b:free` | `0.826` | `5/10` | `53.0s` | `0.929` | `7/10` | `63.4s` | `+0.103` | `+2` | Strongest uplift among free hosted models; orchestration matters a lot more than we first thought. |

Rerun sources:
- [Qwen 3.6 Plus rerun](runs/openclaw_regression_v1_qwen36plus_rerun_20260503/assistant_regression_suite_summary.md)
- [Mimo v2.5 Pro rerun](runs/openclaw_regression_v1_mimov25pro_rerun_20260503/assistant_regression_suite_summary.md)
- [Nemotron free rerun](runs/openclaw_regression_v1_nemotron_rerun_20260503/assistant_regression_suite_summary.md)
- [MiniMax m2.7 rerun](runs/openclaw_regression_v1_minimaxm27_rerun_20260503/assistant_regression_suite_summary.md)
- [GPT-OSS 120B free rerun](runs/openclaw_regression_v1_gptoss_rerun_20260503/assistant_regression_suite_summary.md)

## Full-Suite Ranking

| Rank | Model | Type | Provider | Avg score | Pass | Avg latency | Main strengths | Main weaknesses | Status | Source |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | `google/gemini-3-flash-preview` | hosted | `openrouter` | `1.000` | `10/10` | `10.6s` | Best overall balance; passes the whole suite; strong on live context, planning, web grounding, memory | No suite failures in current routed stack | `Primary` | [summary](runs/openclaw_regression_v1_geminiflash_router4way_20260503/assistant_regression_suite_summary.md) |
| 2 | `qwen/qwen3.5-122b-a10b` | hosted | `openrouter` | `1.000` | `10/10` | `30.8s` | Perfect sweep with strong practical latency; excellent grounded search, planning, locale news, memory | No current suite failures | `Keep / Strong fallback` | [summary](runs/openclaw_regression_v1_qwen35_122b_20260504/assistant_regression_suite_summary.md) |
| 3 | `qwen/qwen3.5-397b-a17b` | hosted | `openrouter` | `1.000` | `10/10` | `44.2s` | Perfect sweep; very strong on grounded search and follow-up context | Slower than `qwen3.5-122b-a10b` without clear quality gain in this suite | `Keep / Strong fallback` | [summary](runs/openclaw_regression_v1_qwen35_397b_20260504/assistant_regression_suite_summary.md) |
| 4 | `xiaomi/mimo-v2.5-pro` | hosted | `openrouter` | `1.000` | `10/10` | `54.1s` | Major orchestration winner; now clears the whole suite | Still slower than the top tier | `Keep / Strong fallback` | [summary](runs/openclaw_regression_v1_mimov25pro_rerun_20260503/assistant_regression_suite_summary.md) |
| 5 | `qwen/qwen3.6-max-preview` | hosted | `openrouter` | `1.000` | `10/10` | `71.4s` | Perfect sweep; strong across all current categories | Heavy latency | `Keep / Strong fallback` | [summary](runs/openclaw_regression_v1_qwen36maxpreview_20260504/assistant_regression_suite_summary.md) |
| 6 | `openai/gpt-5.4-nano` | hosted | `openrouter` | `0.970` | `9/10` | `27.8s` | Very strong overall; surprisingly good on sparse search, planning, web grounding, memory | `weather_followup_city_carryover` | `Keep / Strong fallback` | [summary](runs/openclaw_regression_v1_gpt54nano_20260503/assistant_regression_suite_summary.md) |
| 7 | `qwen/qwen3.6-plus` | hosted | `openrouter` | `0.970` | `9/10` | `62.1s` | Strongly improved after rerun; now in the upper tier | Still slower and slightly rougher than the top `Qwen 3.5` variants | `Experimental / near-top` | [summary](runs/openclaw_regression_v1_qwen36plus_rerun_20260503/assistant_regression_suite_summary.md) |
| 8 | `google/gemma-4-31b-it` | hosted | `openrouter` | `0.970` | `9/10` | `30.2s` | Best `Gemma` result so far; good balance of quality and speed | `weather_followup_city_carryover` | `Keep / Strong fallback` | [summary](runs/openclaw_regression_v1_gemma431bit_20260504/assistant_regression_suite_summary.md) |
| 9 | `z-ai/glm-5.1` | hosted | `openrouter` | `0.963` | `9/10` | `66.8s` | Strong on live context, weather, news, planning, web grounding, memory | `sparse_search_retry_partial_answer` | `Keep / Strong fallback` | [summary](runs/openclaw_regression_v1_glm51_20260503/assistant_regression_suite_summary.md) |
| 10 | `deepseek/deepseek-v4-flash` | hosted | `openrouter` | `0.963` | `9/10` | `56.5s` | Strong overall; good news/date handling; good planning and web grounding | `sparse_search_retry_partial_answer` | `Keep / Strong fallback` | [summary](runs/openclaw_regression_v1_deepseekv4flash_20260503/assistant_regression_suite_summary.md) |
| 11 | `openai/gpt-oss-120b:free` | hosted | `openrouter` | `0.929` | `7/10` | `63.4s` | Strong orchestration uplift; best free hosted result so far | Weather carry-over and sparse-search framing still weaker than top tier | `Keep / Free fallback` | [summary](runs/openclaw_regression_v1_gptoss_rerun_20260503/assistant_regression_suite_summary.md) |
| 12 | `minimax/minimax-m2.7` | hosted | `openrouter` | `0.920` | `8/10` | `61.2s` | Better after rerun; decent mid-tier hosted option | Search quality and planning still weaker than upper tier | `Experimental` | [summary](runs/openclaw_regression_v1_minimaxm27_rerun_20260503/assistant_regression_suite_summary.md) |
| 13 | `nvidia/nemotron-3-super-120b-a12b:free` | hosted | `openrouter` | `0.909` | `7/10` | `169.9s` | Better than first impression after rescoring; decent quality | Very heavy latency; not practical as a default fallback | `Experimental / heavy only` | [summary](runs/openclaw_regression_v1_nemotron_rerun_20260503/assistant_regression_suite_summary.md) |
| 14 | `bunker-gemma26:latest` | local | `ollama` | `0.896` | `7/10` | `154.1s` | Best local model tested so far; materially improved under new orchestration | Still very slow; web-heavy cases remain rough | `Keep / Emergency local fallback` | [summary](runs/openclaw_regression_v1_gemma26_execmode_20260504/assistant_regression_suite_summary.md) |
| 15 | `google/gemma-4-26b-a4b-it` | hosted | `openrouter` | `0.874` | `5/10` | `22.6s` | Fast enough and decent on basics | Frequent output-hygiene issues and weaker grounded behavior | `Experimental / low priority` | [summary](runs/openclaw_regression_v1_gemma426a4b_20260504/assistant_regression_suite_summary.md) |
| 16 | `minimax/minimax-m2.5:free` | hosted | `openrouter` | `0.859` | `6/10` | `76.0s` | Acceptable on identity, date defaults, planning, locale news, memory | Weak live context, sparse search, explicit grounding; high latency on several turns | `Experimental / low priority` | [summary](runs/openclaw_regression_v1_minimaxm25free_20260503/assistant_regression_suite_summary.md) |
| 17 | `tencent/hy3-preview:free` | hosted | `openrouter` | `0.858` | `6/10` | `72.7s` | Acceptable on identity, search quality, planning, locale news, memory | Weak live context, partial-date news, explicit grounding | `Experimental / expiring` | [summary](runs/openclaw_regression_v1_hy3previewfree_20260503/assistant_regression_suite_summary.md) |
| 18 | `google/gemma-3-27b-it` | hosted | `openrouter` | `0.823` | `6/10` | `17.5s` | Quite fast; does fine on basics and date defaults | Falls apart on sparse search, web grounding, and memory reuse | `Experimental / low priority` | [summary](runs/openclaw_regression_v1_gemma327bit_20260504/assistant_regression_suite_summary.md) |
| 19 | `bunker-qwen36-35b-a3b-ud-iq2xxs-qwen35rt:latest` | local | `ollama` | `0.782` | `4/10` | `236.9s` | Tool-capable local Qwen experiment | Too slow to be practical; many timeouts/aborts | `Experimental / not practical` | [summary](runs/openclaw_regression_v1_qwen36_35b_qwen35rt_execmode_20260504/assistant_regression_suite_summary.md) |
| 20 | `bunker-qwen35-9b:latest` | local | `ollama` | `0.738` | `4/10` | `14.6s` | Fast | Current packaging does not support tools cleanly; score is misleading | `Drop until repackaged` | [summary](runs/openclaw_regression_v1_qwen35_9b_execmode_20260504/assistant_regression_suite_summary.md) |
| 21 | `bunker-qwen36-temp:latest` | local | `ollama` | `0.538` | `1/10` | `14.2s` | None in current stack beyond identity | Tool-incompatible in current packaging; most cases fail before useful work | `Drop` | [summary](runs/openclaw_regression_v1_qwen36temp_20260503/assistant_regression_suite_summary.md) |
| 22 | `nousresearch/hermes-3-llama-3.1-405b:free` | hosted | `openrouter` | `0.535` | `0/10` | `7.5s` | Fast responses | Poor fit for current tool-capable stack | `Drop` | [summary](runs/openclaw_regression_v1_hermes3free_20260503/assistant_regression_suite_summary.md) |
| 23 | `meta-llama/llama-3.3-70b-instruct:free` | hosted | `openrouter` | `0.510` | `0/10` | `28.6s` | None in this stack | Does not survive the suite in practice | `Drop` | [summary](runs/openclaw_regression_v1_llama33free_20260503/assistant_regression_suite_summary.md) |
| 24 | `qwen/qwen3-next-80b-a3b-instruct:free` | hosted | `openrouter` | `0.510` | `0/10` | `27.5s` | None in this stack | Does not survive the suite in practice | `Drop` | [summary](runs/openclaw_regression_v1_qwen3nextfree_20260503/assistant_regression_suite_summary.md) |

## Hosted-Only View

| Rank | Model | Avg score | Pass | Avg latency | Recommendation |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | `google/gemini-3-flash-preview` | `1.000` | `10/10` | `10.6s` | `Primary` |
| 2 | `qwen/qwen3.5-122b-a10b` | `1.000` | `10/10` | `30.8s` | `Fallback 1 candidate` |
| 3 | `qwen/qwen3.5-397b-a17b` | `1.000` | `10/10` | `44.2s` | `Fallback 1/2 candidate` |
| 4 | `xiaomi/mimo-v2.5-pro` | `1.000` | `10/10` | `54.1s` | `Fallback 2 candidate` |
| 5 | `qwen/qwen3.6-max-preview` | `1.000` | `10/10` | `71.4s` | `Quality-first fallback` |
| 6 | `openai/gpt-5.4-nano` | `0.970` | `9/10` | `27.8s` | `Strong latency-conscious fallback` |
| 7 | `qwen/qwen3.6-plus` | `0.970` | `9/10` | `62.1s` | `Upper-tier experimental` |
| 8 | `google/gemma-4-31b-it` | `0.970` | `9/10` | `30.2s` | `Best Gemma fallback candidate` |
| 9 | `z-ai/glm-5.1` | `0.963` | `9/10` | `66.8s` | `Strong fallback` |
| 10 | `deepseek/deepseek-v4-flash` | `0.963` | `9/10` | `56.5s` | `Strong fallback` |
| 11 | `openai/gpt-oss-120b:free` | `0.929` | `7/10` | `63.4s` | `Best free hosted fallback` |
| 12 | `minimax/minimax-m2.7` | `0.920` | `8/10` | `61.2s` | `Experimental` |
| 13 | `nvidia/nemotron-3-super-120b-a12b:free` | `0.909` | `7/10` | `169.9s` | `Selective heavy fallback only` |
| 14 | `google/gemma-4-26b-a4b-it` | `0.874` | `5/10` | `22.6s` | `Experimental / low priority` |
| 15 | `minimax/minimax-m2.5:free` | `0.859` | `6/10` | `76.0s` | `Experimental / low priority` |
| 16 | `tencent/hy3-preview:free` | `0.858` | `6/10` | `72.7s` | `Experimental / expiring` |
| 17 | `google/gemma-3-27b-it` | `0.823` | `6/10` | `17.5s` | `Experimental / low priority` |
| 18 | `nousresearch/hermes-3-llama-3.1-405b:free` | `0.535` | `0/10` | `7.5s` | `Drop` |
| 19 | `meta-llama/llama-3.3-70b-instruct:free` | `0.510` | `0/10` | `28.6s` | `Drop` |
| 20 | `qwen/qwen3-next-80b-a3b-instruct:free` | `0.510` | `0/10` | `27.5s` | `Drop` |

## Local-Only View

| Rank | Model | Avg score | Pass | Avg latency | Recommendation |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | `bunker-gemma26:latest` | `0.896` | `7/10` | `154.1s` | `Emergency local fallback` |
| 2 | `bunker-qwen36-35b-a3b-ud-iq2xxs-qwen35rt:latest` | `0.782` | `4/10` | `236.9s` | `Interesting experiment; not practical` |
| 3 | `bunker-qwen35-9b:latest` | `0.738` | `4/10` | `14.6s` | `Repackage before trusting` |
| 4 | `bunker-qwen36-temp:latest` | `0.538` | `1/10` | `14.2s` | `Drop / incompatible in current stack` |

## Special Compatibility Experiments

These runs are useful, but they are **not directly comparable** to the full 10-case suite results above.

| Model | Runtime | Result | Notes | Source |
| --- | --- | --- | --- | --- |
| `bunker-qwen36-35b-a3b-ud-iq2xxs-qwen35rt:latest` | `ollama` | `0.114`, `0/3 pass`, `7 not run` | Important proof that `RENDERER qwen3.5 + PARSER qwen3.5` enabled `tools`, but the model remained too slow / timeout-prone on the `mac mini` | [summary](runs/openclaw_regression_qwen36_35b_qwen35rt_smoke_20260503/assistant_regression_suite_summary.md) |

## Main Takeaways

- `Gemini 3 Flash` is still the best overall model in the current OpenClaw stack.
- `Qwen 3.5 122B`, `Qwen 3.5 397B`, `Mimo v2.5 Pro`, and `Qwen 3.6 Max Preview` all now clear the suite completely and join the very top hosted tier.
- `Qwen 3.5 122B` currently looks like the strongest practical new hosted fallback because it combines a perfect sweep with materially better latency than the other newly-tested `Qwen` variants.
- `Gemma 4 31B` is the first `Gemma` candidate that clearly belongs in the strong fallback conversation; the smaller `Gemma` variants trail behind.
- `GPT-OSS 120B free` remains the best free hosted fallback tested so far.
- `Gemma26` is still the best local model tested so far, but it should be treated as a narrower emergency fallback rather than a universal assistant model.
- The weakest recurring failure mode across many otherwise good models is still `sparse_search_retry_partial_answer`.

## Recommended Fallback Chain

1. `Primary`: `google/gemini-3-flash-preview`
2. `Fallback 1`: `qwen/qwen3.5-122b-a10b`
3. `Fallback 2`: `openai/gpt-5.4-nano`
4. `Fallback 3`: `z-ai/glm-5.1`
5. `Fallback 4`: `deepseek/deepseek-v4-flash`
6. `Free hosted fallback`: `openai/gpt-oss-120b:free`
7. `Emergency local fallback`: `bunker-gemma26:latest`

## Related Documents

- [OpenClaw Regression Model Comparison — 2026-05-03](runs/openclaw_regression_model_comparison_20260503.md)
- [OpenClaw Regression Model Comparison — Router Sweep — 2026-05-03](runs/openclaw_regression_model_comparison_router_20260503.md)
