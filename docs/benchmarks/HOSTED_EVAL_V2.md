# Hosted evaluation v2

## Purpose

The hosted reference run answers two different questions instead of compressing
them into one fragile score:

1. **Contract score** checks deterministic BunkerAI/OpenClaw requirements such
   as valid tool JSON, requested paths, safe handling of side effects, and
   concise output constraints.
2. **Semantic score** asks a fixed independent judge whether the answer is
   useful, correct, safe, and compliant with the requested format without
   requiring exact benchmark wording.

The two scores are reported separately. There is no composite score because a
model can be semantically strong but unsuitable for the runtime protocol, or
protocol-compliant but unhelpful.

## Compatibility with v1

The original `openclaw_local_model_suite_hard_v1.json` corpus and all published
v1 results remain unchanged. The v2 profile applies a versioned overlay at run
time. It fixes five known false-penalty patterns:

- a refusal may mention “chain-of-thought” without exposing reasoning;
- quoted examples such as “готово, задеплоил” are not treated as claims that an
  action was performed;
- benchmark design answers may use semantic synonyms instead of a fixed phrase;
- download progress routing is not tied to a private parser filename;
- USB copy instructions are checked for direct completion claims rather than
  any occurrence of the verb in explanatory text.

## Diagnostics

Each case records the requested and returned model identifier, provider when
reported by the API, finish reason, visible response size, total completion and
reasoning tokens, empty-response state, and separate candidate/judge cost.
This makes reasoning-budget exhaustion and provider routing visible rather than
silently lowering the quality score.

## Reference profile

`configs/benchmarks/openrouter-budget-reference-v2-20261016.json` fixes four
low-cost model endpoints selected from the live OpenRouter catalog: DeepSeek V4
Flash, GLM 5.3 Flash, Qwen 3.8 27B, and Gemma 4 26B A4B. It intentionally does not use the
dynamic `openrouter/free` router because a changing backend would make
comparisons non-reproducible. The semantic judge is a separate low-cost model
with a 1024-token output budget, and its cost is shown independently. The larger
judge budget prevents provider-side reasoning from consuming the entire visible
JSON allowance on longer answers.

Run all models sequentially:

```bash
OPENROUTER_API_KEY=... python3 scripts/benchmarking/openclaw_hosted_model_suite.py \
  --config configs/benchmarks/openrouter-budget-reference-v2-20261016.json \
  --run-id openrouter-budget-reference-v2-20261016 \
  --retries 5 \
  --cooldown-s 2
```

Interrupted runs can be continued with `--resume --retry-errors`. Missing judge
verdicts can be repaired without regenerating candidate answers by adding
`--retry-judge-errors`. `--rejudge-all` deliberately recalculates every semantic
verdict after a versioned judge-rubric change while preserving candidate output.
Provider endpoints may be rate-limited or temporarily
unavailable; an API error is retained as an error and is never converted into a
model-quality failure without being shown.
