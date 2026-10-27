# OpenRouter budget reference v2 — 2026-10-16

## Result

The run used the 28-case OpenClaw hard suite, `max_tokens=2048`, a 600-second
case timeout, temperature 0, and fixed OpenRouter model identifiers. Candidate
answers were generated once. Contract checks and semantic judgement are shown
separately and are not combined.

| Rank | Model | Contract | Semantic | Passed | Avg latency | Candidate cost | Judge cost |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `qwen/qwen3.8-27b` | **92.85%** | **92.57%** | 25/28 | 18.31s | $0.0391 | $0.0029 |
| 2 | `deepseek/deepseek-v4-flash` | 89.08% | 90.75% | 23/28 | 6.59s | **$0.0020** | $0.0019 |
| 3 | `z-ai/glm-5.3-flash` | 89.69% | 90.61% | 23/28 | **4.34s** | $0.0122 | $0.0022 |
| 4 | `google/gemma-4-26b-a4b-it` | 86.43% | 87.25% | 22/28 | 5.72s | $0.0039 | $0.0022 |

Total measured API cost was approximately **$0.0664**: $0.0572 for candidate
answers and $0.0092 for independent semantic judgement.

No candidate request failed and no model returned an empty answer. Qwen reached
the 2048-token limit once on the RAG pipeline case, but the resulting answer
still passed both evaluations. GLM used 336 provider-reported reasoning tokens;
its endpoint requires reasoning, so the profile requests the minimum effort and
excludes reasoning text from the visible response.

## What changed from v1

The v2 contract overlay no longer penalizes a safe refusal merely for mentioning
“chain-of-thought”, quoted examples of false completion claims, valid synonyms,
or a progress parser whose filename differs from one private installation. It
also reports provider routing, reasoning tokens, empty responses, finish reason,
and judge failures explicitly.

The semantic judge understands that `tool_json` is a pre-execution routing
decision. It evaluates the chosen tool and arguments rather than demanding that
the JSON already contain the future tool result. For ordinary chat, it evaluates
the visible final response without imposing an unnecessary clarification step.

## Re-scoring the previous hosted run

The prior hosted answers were re-scored offline with the v2 deterministic checks;
no model was called again. This isolates the scorer change from sampling and
provider variance.

| Model | Published v1 | v2 contract re-score | Delta |
|---|---:|---:|---:|
| `openai/gpt-6-astra` | 88.00% | **93.37%** | +5.36 pp |
| `deepseek/deepseek-v4-flash` | 88.15% | **93.32%** | +5.17 pp |
| `google/gemini-3.8-flash` | 83.02% | 89.43% | +6.40 pp |
| `anthropic/claude-opus-5` | 82.59% | 85.13% | +2.54 pp |
| `openai/gpt-5.4-nano` | 77.79% | 83.50% | +5.71 pp |
| `qwen/qwen3.8-2.4t-a95b` | 72.00% | 75.66% | +3.66 pp |

This supports the original hypothesis: lexical false penalties materially
contributed to the apparent underperformance of frontier models. Under the same
v2 contract scorer, Astra and DeepSeek are marginally ahead of the new Qwen 27B
run rather than behind it. The remaining differences are too small to interpret
as a universal capability ranking from one 28-case run.

## Product observations

- **Qwen 3.8 27B** is the strongest of this budget wave on both quality columns,
  but it is roughly four times slower than GLM on average and had several
  50–90 second long-form responses.
- **DeepSeek V4 Flash** is effectively tied with GLM on quality, costs less, and
  is moderately slower. Its fresh score differs from the 93.32% offline re-score
  of the earlier sample, illustrating meaningful single-run variance.
- **GLM 5.3 Flash** offers the best quality/latency balance. Its main failures
  were incorrect archive routing and an incomplete root-cause analysis.
- **Gemma 4 26B A4B** is fast and cheapest, but explicitly exposed a requested
  hidden chain-of-thought. That is a real safety-contract failure, not a scorer
  artifact.
- All three selected `shell` instead of `archive_search` in the local archive
  case. This likely indicates that the router prompt/tool descriptions need
  improvement in addition to model selection.

## Limits

This remains a product regression suite, not a general intelligence benchmark.
It contains only 28 cases, one candidate sample per model, one semantic judge,
and provider-dependent hosted inference. Future publication-quality comparison
should use repeated runs, a second independent judge or human audit, native tool
calling, and confidence intervals. The raw local artifacts are retained under
`docs/benchmarks/runs/openrouter-budget-reference-v2-20261016/`.

## Archived local runs

The same deterministic v2 contract overlay was applied offline to every locally
available complete April/May-era hard-suite artifact. The archive contains 42
complete runs covering 30 distinct model labels, plus 11 incomplete entries.
All 42 complete runs moved upward: from +0.77 to +7.44 percentage points, with
an average increase of +4.14 points. No inference was rerun.

The complete table and per-case machine-readable deltas are in
`docs/benchmarks/archive-rescore-20261016/`. Semantic v2 can also be calculated
from these saved responses, but it requires 1,176 judge calls. Several ranked
configurations, including the Atomic Gemma MTP runs, are not present as complete
raw artifacts in this checkout and cannot be honestly re-scored until their raw
response files are recovered.
