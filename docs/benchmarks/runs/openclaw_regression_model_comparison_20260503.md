# OpenClaw Regression Model Comparison — 2026-05-03

This note compares the current `assistant_regression_v1` baseline across three model configurations on the `mac mini` OpenClaw runtime.

## Targets

| Label | Model | Provider | Source run |
| --- | --- | --- | --- |
| `gemma26` | `bunker-gemma26:latest` | `ollama` | `openclaw_regression_v1_gemma26_nomem_20260503` |
| `gemini_flash` | `google/gemini-3-flash-preview` | `openrouter` | `openclaw_regression_v1_geminiflash_nomem_20260503` |
| `nemotron_free` | `nvidia/nemotron-3-super-120b-a12b:free` | `openrouter` | per-case runs `openclaw_regression_nemotron_case_*_20260503` |

`mem0` auto-recall and auto-capture were disabled for these baselines to reduce cross-case contamination.

## Headline Summary

| Model | Avg score | Pass | Fail | Avg latency |
| --- | ---: | ---: | ---: | ---: |
| `gemma26` | `0.676` | `3` | `7` | `96.3s` |
| `gemini_flash` | `0.902` | `6` | `4` | `10.5s` |
| `nemotron_free` | `0.847` | `5` | `5` | `56.4s` |

## Case Matrix

| Case | `gemma26` | `gemini_flash` | `nemotron_free` |
| --- | --- | --- | --- |
| `identity_role_baseline` | pass `1.000` | pass `1.000` | pass `1.000` |
| `current_datetime_live_source` | fail `0.625` | fail `0.625` | fail `0.625` |
| `weather_followup_city_carryover` | fail `0.800` | fail `0.700` | fail `0.700` |
| `news_today_default_date` | fail `0.800` | pass `1.000` | pass `1.000` |
| `news_partial_date_defaults_current_year` | fail `0.300` | pass `1.000` | fail `0.700` |
| `sparse_search_retry_partial_answer` | fail `0.250` | fail `0.875` | fail `0.875` |
| `planning_uses_recent_location_context` | pass `1.000` | pass `1.000` | fail `0.571` |
| `explicit_web_sources_and_addresses` | fail `0.364` | fail `0.818` | pass `1.000` |
| `country_aware_broad_news` | fail `0.625` | pass `1.000` | pass `1.000` |
| `memory_preference_reuse` | pass `1.000` | pass `1.000` | pass `1.000` |

## Main Takeaways

- `gemini_flash` is the best current overall default for OpenClaw on the `mac mini`.
- `nemotron_free` is materially stronger than the local `gemma26` on web-grounded news and venue lookup, but much slower than `gemini_flash` and less stable on planning and partial-date defaults.
- `gemma26` remains viable as a local fallback, but it is currently too slow and too weak on web-routing-heavy cases to be the primary OpenClaw model.

## Shared Failure Modes

These regressions still affect all three profiles and should be fixed at the policy / routing layer rather than by model selection alone:

- `current_datetime_live_source`: none of the three baselines used the required live clock-style tool.
- `weather_followup_city_carryover`: all three baselines still failed the suite's strict live-weather expectations.
- `sparse_search_retry_partial_answer`: stronger web models got close, but still failed to frame incomplete retrieval as explicitly partial.

## Model-Specific Notes

### `gemini_flash`

- Best blend of speed and quality.
- Strongest broad-news routing and date defaulting behavior.
- Still detours on some weather and explicit-address cases.

### `nemotron_free`

- Good identity behavior.
- Strong on explicit web-grounded lookup and country-aware news.
- Weaker on planning carry-over and partial-date news routing.
- High latency on search-heavy turns (`~98s` to `~138s`).

### `gemma26`

- Best local-only option tested so far.
- Acceptable on identity, planning carry-over, and memory preference reuse.
- Significantly behind hosted models on search, current-events, and explicit venue lookup.

