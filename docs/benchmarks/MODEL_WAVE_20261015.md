# Model benchmark wave: 2026-10-15

This wave refreshes the Ubuntu AMD benchmark pool after increasing the firmware GPU allocation to 96 GiB. Together with the Linux GTT pool, the host exposes about 111.5 GiB of GPU-addressable memory.

## Download matrix

| Family | Publisher / conversion | Quant | Acceleration companion | Purpose |
| --- | --- | --- | --- | --- |
| Qwen 3.8 27B | ggml-org | Q4_K_M | MTP Q4_0 and DFlash Q4_0 | Reference conversion and acceleration baseline |
| Qwen 3.8 27B | Unsloth | UD-Q4_K_M, UD-Q6_K_M | MTP Q4_0 | Publisher and quantization comparison |
| Nemotron 3.5 Lightning 30B-A3B | ggml-org | Q4_0 | MTP Q4_0 | Reference conversion and MTP baseline |
| Nemotron 3.5 Lightning 30B-A3B | Unsloth | UD-Q4_K_M, UD-Q6_K_XL | None | Publisher and quantization comparison |
| LFM 2.5 24B-A2B | ggml-org | Q4_K_M | None | Compact MoE reference |
| LFM 2.5 24B-A2B | Unsloth | UD-Q6_K_XL | None | Higher-quality quantization comparison |
| Qwen 3.8 Flash Next | ggml-org | Q2_K | MTP Q4_0 | Largest model expected to fit the host |
| Qwen 3.8 Flash Next | Unsloth | UD-IQ3_XXS | MTP Q4_K_M | Higher-quality alternate conversion near the memory limit |
| Nemotron 3.5 Super VL 120B-A12B | ggml-org | Q4_0 | MTP Q4_0, Q8 mmproj | New 120B multimodal reference conversion |
| Nemotron 3.5 Super VL 120B-A12B | Unsloth | UD-Q4_K_XL | BF16 mmproj | Higher-quality alternate conversion |

The download list is stored in `configs/downloads/benchmark-wave-20261015.urls`. Expected payload is approximately 478 GiB.

## Runtime

The benchmark runtime is built separately from the production runtime at `<benchmark-home>/llama.cpp-upstream-20261015`. The initial pinned revision is `b76b13379d3b7d67ab0bc424516bb6fd2522bd8e` (`llama.cpp 0.7.0-dev`) with Vulkan enabled. Production services must not be switched to this binary until the smoke tests pass.

Current builds use the `--spec-draft-*` option family for speculative decoding. Legacy `--draft-max` and `--draft-min` options are removed and must not be copied from older benchmark commands.

## Benchmark controls

- Pin the exact `llama.cpp` commit and model file SHA-256 in every run result.
- Run the existing 28-case suite with `max_tokens=2048`, `case_timeout=600`, thinking disabled, and the same context size.
- Warm up each local model before measurement and run each configuration once. Repeat only a failed or clearly anomalous run, and keep the rerun marked separately instead of silently replacing the first result.
- Measure quality, prompt processing, generation throughput, first-token latency, peak RAM/VRAM, and MTP acceptance separately.
- Compare MTP on/off against the same base file. Do not compare an MTP run to a different quantization.
- Keep unsupported formats, load failures, and truncated responses out of the normal quality ranking and report them separately.

## Hosted reference

Run each hosted model exactly once with the same 28-case, `2048/600` profile
used for the local candidates. The first group is a low-cost cross-provider
baseline; the second group establishes a stronger ceiling with models that
cannot be deployed on the target host.

### Budget baseline

| Model | OpenRouter price per 1M input / output tokens | Previous suite signal | Purpose |
| --- | ---: | ---: | --- |
| `deepseek/deepseek-v4-flash` | `$0.0679 / $0.168` | `96.3%` | Very low-cost strong reasoning reference |
| `google/gemini-3.8-flash` | `$0.75 / $3.75` | New reference | Current high-quality Flash reference with tool support |
| `openai/gpt-5.4-nano` | `$0.20 / $1.25` | `97.0%` | Independent commercial small-model reference with tool support |

### Frontier and non-local reference

| Model | OpenRouter price per 1M input / output tokens | Why it is non-local | Purpose |
| --- | ---: | --- | --- |
| `openai/gpt-6-astra` | `$10 / $50` | Proprietary frontier model | High-end OpenAI quality ceiling |
| `anthropic/claude-opus-5` | `$5 / $25` | Proprietary frontier model | Independent high-end Anthropic reference |
| `qwen/qwen3.8-2.4t-a95b` | `$2 / $6` | Open 2.4T-parameter MoE, 95B active | Very large open-model reference that exceeds the local deployment envelope |

Reasoning is disabled where the provider permits it. The current Gemini 3.8
Flash endpoint rejects `reasoning=none`; for that model the runner requests the
minimum supported effort and excludes reasoning text from the response. Reports
must retain this caveat instead of presenting Gemini as a strict reasoning-off
comparison. The same provider restriction applies to GPT-6 Astra and Qwen3.8
2.4T-A95B. Claude Opus 5 accepts the strict reasoning-off profile.

At the hard output ceiling of 57,344 tokens per model, the three budget runs
together cost about `$0.30` in output tokens. The three frontier/non-local runs
have a worst-case output cost of about `$4.65`, although normal completed runs
should be materially cheaper. Input-token charges are additional. Prices were
checked on 2026-10-16 and must be refreshed before a later wave.
The machine-readable execution contract is stored in
`configs/benchmarks/openrouter-budget-reference-20261015.json`.

### Hosted results: 2026-10-16

| Rank | Model | Reasoning | Score | Passed | Average latency | Estimated cost |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | `deepseek/deepseek-v4-flash` | disabled | `88.15%` | `22/28` | `7.11s` | `$0.0020` |
| 2 | `openai/gpt-6-astra` | minimal, mandatory | `88.00%` | `22/28` | `11.02s` | `$0.6598` |
| 3 | `google/gemini-3.8-flash` | minimal, mandatory | `83.02%` | `19/28` | `7.18s` | `$0.0558` |
| 4 | `anthropic/claude-opus-5` | disabled | `82.59%` | `19/28` | `14.16s` | `$0.5861` |
| 5 | `openai/gpt-5.4-nano` | disabled | `77.79%` | `18/28` | `5.37s` | `$0.0214` |
| 6 | `qwen/qwen3.8-2.4t-a95b` | minimal, mandatory | `72.00%` | `16/28` | `9.32s` | `$0.1756` |

All six runs completed without final API errors. Qwen reached the 2,048-token
completion limit in six cases. Five of those responses contained no visible
answer because mandatory provider-side reasoning consumed the completion budget
before final text was emitted. Its `72.00%` is therefore a valid score for this
fixed production profile, but not a reasoning-budget-independent estimate of
the base model's knowledge. The detailed case matrix is generated under
`docs/benchmarks/runs/openrouter-budget-reference-20261016/`.

## Removed weights

Historical results remain in `model-comparison-20260518`. The following weights were removed from the Ubuntu host to recover about 642 GiB:

- ERNIE 4.5 300B Q2: did not fit the previous memory configuration.
- DeepSeek V4 Flash IQ2: invalid decoding on the available runtime.
- Qwen3 Next 80B Thinking Q4: 59.03% best observed score.
- GPT-OSS 120B MXFP4: 69.35% best observed score.
- Mistral Small 4 119B Q3: 70.77% best observed score.
- Llama 4 Scout Q4: 71.99% best observed score.
- MiMo V2.5 IQ2: 76.38% at about 90 GiB.
- Llama 3.1 Nemotron Ultra 253B Q2: 77.63% at about 87 GiB.
- DeepSeek R1 Distill Qwen 32B Q4: 58.35% best observed score.
- Llama 3.3 70B Q2: 71.18%; the separate Q4 copy remains available.
- Gemma 4 31B Q6 file: 71.71%; the Q4 file in the same directory remains available.
