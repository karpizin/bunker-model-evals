# OpenClaw Model Regression — All Checked Models (Snapshot 2026-05-04)

This file is a flat snapshot of every model we have checked so far against the `assistant_regression_v1` suite on the `mac mini` OpenClaw runtime.

Rules for this table:
- use the latest comparable full-suite result per model when we have reruns
- keep clearly non-comparable local packaging experiments marked as such
- include latency, because some models are usable in quality terms but not in product terms

## All Models

| Rank | Model | Type | Provider | Avg score | Pass | Avg latency | Comparable | Notes |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 1 | `google/gemini-3-flash-preview` | hosted | `openrouter` | `1.000` | `10/10` | `10.6s` | yes | Current primary |
| 2 | `qwen/qwen3.5-122b-a10b` | hosted | `openrouter` | `1.000` | `10/10` | `30.8s` | yes | Strongest practical new hosted fallback |
| 3 | `qwen/qwen3.5-397b-a17b` | hosted | `openrouter` | `1.000` | `10/10` | `44.2s` | yes | Excellent quality, slower than `122b` |
| 4 | `xiaomi/mimo-v2.5-pro` | hosted | `openrouter` | `1.000` | `10/10` | `54.1s` | yes | Major gain after orchestration rerun |
| 5 | `qwen/qwen3.6-max-preview` | hosted | `openrouter` | `1.000` | `10/10` | `71.4s` | yes | Excellent quality, heavy latency |
| 6 | `openai/gpt-5.4-nano` | hosted | `openrouter` | `0.970` | `9/10` | `27.8s` | yes | Strongest low-latency fallback candidate |
| 7 | `qwen/qwen3.6-plus` | hosted | `openrouter` | `0.970` | `9/10` | `62.1s` | yes | Strongly improved after rerun |
| 8 | `google/gemma-4-31b-it` | hosted | `openrouter` | `0.970` | `9/10` | `30.2s` | yes | Best Gemma result so far |
| 9 | `z-ai/glm-5.1` | hosted | `openrouter` | `0.963` | `9/10` | `66.8s` | yes | Strong quality fallback |
| 10 | `deepseek/deepseek-v4-flash` | hosted | `openrouter` | `0.963` | `9/10` | `56.5s` | yes | Strong quality fallback |
| 11 | `openai/gpt-oss-120b:free` | hosted | `openrouter` | `0.929` | `7/10` | `63.4s` | yes | Best free hosted result after rerun |
| 12 | `minimax/minimax-m2.7` | hosted | `openrouter` | `0.920` | `8/10` | `61.2s` | yes | Solid mid-tier hosted model |
| 13 | `nvidia/nemotron-3-super-120b-a12b:free` | hosted | `openrouter` | `0.909` | `7/10` | `169.9s` | yes | Quality acceptable, latency poor |
| 14 | `bunker-gemma26:latest` | local | `ollama` | `0.896` | `7/10` | `154.1s` | yes | Best local model tested so far |
| 15 | `google/gemma-4-26b-a4b-it` | hosted | `openrouter` | `0.874` | `5/10` | `22.6s` | yes | Mid-tier Gemma result |
| 16 | `minimax/minimax-m2.5:free` | hosted | `openrouter` | `0.859` | `6/10` | `76.0s` | yes | Lower free tier |
| 17 | `tencent/hy3-preview:free` | hosted | `openrouter` | `0.858` | `6/10` | `72.7s` | yes | Lower free tier; expiring |
| 18 | `google/gemma-3-27b-it` | hosted | `openrouter` | `0.823` | `6/10` | `17.5s` | yes | Fast but clearly below top hosted tier |
| 19 | `bunker-qwen36-35b-a3b-ud-iq2xxs-qwen35rt:latest` | local | `ollama` | `0.782` | `4/10` | `236.9s` | mostly | Tool-capable, but too slow to be practical |
| 20 | `bunker-qwen35-9b:latest` | local | `ollama` | `0.738` | `4/10` | `14.6s` | no | Current packaging does not support tools cleanly |
| 21 | `bunker-qwen36-temp:latest` | local | `ollama` | `0.538` | `1/10` | `14.2s` | no | Tool-incompatible packaging |
| 22 | `nousresearch/hermes-3-llama-3.1-405b:free` | hosted | `openrouter` | `0.535` | `0/10` | `7.5s` | yes | Drop |
| 23 | `meta-llama/llama-3.3-70b-instruct:free` | hosted | `openrouter` | `0.510` | `0/10` | `28.6s` | yes | Drop |
| 24 | `qwen/qwen3-next-80b-a3b-instruct:free` | hosted | `openrouter` | `0.510` | `0/10` | `27.5s` | yes | Drop |

## Practical Takeaways

- Best current overall model: `google/gemini-3-flash-preview`
- Best current practical hosted fallback: `qwen/qwen3.5-122b-a10b`
- Strong fallback tier after that: `openai/gpt-5.4-nano`, `google/gemma-4-31b-it`, `z-ai/glm-5.1`, `deepseek/deepseek-v4-flash`
- Best free hosted result so far: `openai/gpt-oss-120b:free`
- Best local result so far: `bunker-gemma26:latest`
- Most misleading family without packaging fixes: local `Qwen`
- Best reminder from the reruns: orchestration quality materially changes leaderboard shape
- Biggest surprise from the new sweep: large hosted `Qwen` variants are currently among the strongest models in this stack

## Related

- [Master regression table](OPENCLAW_MODEL_REGRESSION_MASTER_TABLE_20260503.md)
- [Router comparison](runs/openclaw_regression_model_comparison_router_20260503.md)
