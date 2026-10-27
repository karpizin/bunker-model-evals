# Bunker Benchmark v3: October model wave

Status: complete; public evidence bundle published 2026-10-27
Started: 2026-10-26  
Hardware: AMD Ryzen AI Max+ 395 / Vulkan full GPU offload  
Runtime: `llama.cpp` `fd8f8451a2c0`  
Protocol: 20 v3 cases, one measured run, temperature `0.05`, maximum
`8192` output tokens, `600` second per-case timeout

The authoritative publication is the
[`2026-10-27 public result bundle`](results/bunker-v3-public-results-20261027/README.md):
42 included result files, 142 complete runs, sanitized raw outputs, hashes, and
an explicit excluded-results ledger. The same answers were independently
re-evaluated with the versioned semantic rubric in the
[`v3.1 report`](BUNKER_BENCHMARK_V3_1_RESCORE_20261027.md).

Capability and protocol compliance are reported separately. A model is
production eligible only when it has zero critical failures.

## Queue

| Model | Quantization | Source | Status |
|---|---|---|---|
| Spark-X2.6-4B | Q5_K_M | [bartowski/Spark-X2.6-4B-GGUF](https://huggingface.co/bartowski/Spark-X2.6-4B-GGUF) | Complete |
| Flint | Q4_K_M | [ggml-org/Flint-GGUF](https://huggingface.co/ggml-org/Flint-GGUF) | Complete |
| Nanbeige4.3-33B | Q4_K_M | [bartowski/Nanbeige_Nanbeige4.3-33B-GGUF](https://huggingface.co/bartowski/Nanbeige_Nanbeige4.3-33B-GGUF) | Complete |
| Qwen3.6-27B | Q4_K_M, plain | Local artifact | Complete: 5 runs |
| Qwen3.6-27B | Q4_K_M, internal MTP | Local artifact | Complete: 5 runs |
| Qwen3.6-27B | UD-IQ3_XXS, internal MTP | Local artifact | Complete: 5 runs |
| Qwen3.6-27B | UD-IQ2_M, plain | Local artifact | Complete: 5 runs |
| Qwen3.8-27B | UD-Q6_K_M, external MTP | Local artifact | Complete: 5 runs |
| Qwen3.6-35B-A3B | UD-Q4_K_M, plain | Local artifact | Complete |
| Qwen3.6-35B-A3B | UD-Q5_K_M, internal MTP | Local artifact | Complete |
| Qwen3.6-35B-A3B | UD-Q6_K, internal MTP | Local artifact | Complete |
| Huihui-Qwen3.6-35B-A3B abliterated | Q4_K, internal MTP | Local artifact | Complete |
| Qwen3.6-35B-A3B Uncensored | Q3_K_P, plain | Local artifact | Complete: 5 runs |

All models in this wave use the same isolated runtime build. This avoids mixing
the older benchmark runtime with the new build required for Flint support.

The Qwen artifacts completed the original 2026-10-19 wave, but those results
predate the final tool-call normalizer. They are therefore rerun rather than
copied into the current ranking. The eight main configurations run first; the
abliterated and uncensored variants form a separate experimental tail.

## Results

| Model | Capability | Critical failures | Truncated | Protocol errors | Total latency | Eligible |
|---|---:|---:|---:|---:|---:|---|
| Spark-X2.6-4B-Q5_K_M | 75.38% | 15 | 0 | 2 | 74.82 s | No |

### Spark-X2.6-4B track scores

| Track | Score |
|---|---:|
| Grounded RAG | 83.87% |
| Synthesis | 82.45% |
| Code / operations | 75.20% |
| Agent execution | 71.71% |
| Result validation | 63.65% |

Spark is 0.73 percentage points ahead of Qwen3-4B-Q5_K_M and 2.83 points
behind Qwen3.5-4B-Q5_K_M in the current unified ranking. Its main failures are
top-3 tool fusion and fallback/result-validation behavior. The absence of
truncation is positive, but 15 critical failures make it unsuitable for the
production allowlist without guards.

The original diagnostic run on the previous runtime scored 74.29%. It is not
used in the ranking; the 75.38% run above is the comparable result.

## Reproducibility

- Download manifest:
  `scripts/benchmarking/manifests/bunker_benchmark_v3_october_wave.urls`
- Benchmark runner: `scripts/benchmarking/run_v3_medium_large_remote.sh`
- Download-aware queue worker:
  `scripts/benchmarking/run_v3_october_wave_remote.sh`

The worker verifies completed files and exact byte sizes before starting each
downloaded model. Qwen artifacts are benchmarked while Flint and Nanbeige are
downloading; the user accepted the negligible storage-I/O effect on LLM
throughput. Flint and Nanbeige start automatically as soon as both files are
complete.

## Stability phase

After the single-run wave, the ten highest-scoring standard local models are
selected automatically. Hosted API models and abliterated, uncensored or
heretic variants are excluded from this selection. Before selection, four
strong candidates from earlier local waves are refreshed on the current
runtime: Qwen3.8 27B Q4, Gemma 4 E4B Q4, Qwen3 14B Q4 and Qwen3.5 9B Q5. The
top ten standard local models are each resumed to five complete runs using the
same runtime and protocol. The repeated-run report publishes mean, median, standard
deviation, worst score, truncations and eligible-run count; individual critical
failure counts remain available in the per-run table.

## Gemma 4 regression audit

The initial medium/large wave understated the larger Gemma 4 models because
the pre-normalizer runner did not recognize their native/agent tool-call and
final-answer formats. Corrected control runs changed the representative Q4
results as follows:

| Model | Pre-normalizer | Corrected | Critical failures |
|---|---:|---:|---:|
| Gemma 4 26B-A4B Q4 | 75.63% | 87.19% | 18 -> 6 |
| Gemma 4 31B Q4 | 84.15% | 91.76% | 13 -> 2 |

The largest recovered scores are in agent execution and result validation,
where valid Gemma final answers had previously been counted as missing. A full
quantization sweep is queued on the current `fd8f8451a2c0` runtime before
leader selection: 26B-A4B Q3/Q4/Q5 and 31B Q4/Q5/Q6. All six artifacts are
already present locally, so no additional model download is required. The
stability phase can include any Gemma variant that finishes in the top ten.

## Modified-leader comparison

Modified models are kept outside automatic leader selection and compared
directly with their parent checkpoints. The queued group contains:

| Modified model | Parent comparison | Quant/profile | Source |
|---|---|---|---|
| Qwen3.8-27B Uncensored | Qwen3.8-27B | Q6_K, internal MTP | [JonathanColetti/Qwen3.8-27B-Uncensored-GGUF](https://huggingface.co/JonathanColetti/Qwen3.8-27B-Uncensored-GGUF) |
| Qwen3.6-27B Abliterated | Qwen3.6-27B | Q4_K_M, internal MTP | [gaston-parravicini/Qwen3.6-27B-Abliterated-MTP-GGUF](https://huggingface.co/gaston-parravicini/Qwen3.6-27B-Abliterated-MTP-GGUF) |
| Gemma 4 31B Heretic | Gemma 4 31B | Q4_K_M, plain | Local artifact |

The Qwen3.8 and Qwen3.6 files preserve MTP and match the parent quantization
class closely enough to separate modification effects from quantization and
runtime effects. The two remote artifacts total about 39.2 GB; the Gemma
Heretic artifact is already local.

### Q6/Q8 sweep for existing modified 35B models

The earlier Q3/Q4 modified models are followed by four higher-precision runs:

- HauhauCS Qwen3.6 35B Uncensored Q6_K_P and Q8_K_P;
- Huihui Qwen3.6 35B Abliterated MTP Q6_K and Q8_0.

The four GGUF files total 141.3 GB. After the storage cleanup below, enough
space is available to download them sequentially alongside the existing queue
and retain them after each complete 20-case run. Benchmark JSON, reports and
logs are retained as well.

## Model storage cleanup

On 2026-10-26, 301,204,881,600 bytes of reproducible GGUF artifacts were
removed after their complete benchmark results had been preserved. Only model
weights were deleted; result JSON, reports, logs and model directories remain.

| Removed model family | Best V3 capability | Removed bytes |
|---|---:|---:|
| NVIDIA Nemotron 3.5 Super-VL 120B Q4 + MTP/mmproj | 72.72% | 75,040,780,288 |
| NVIDIA Nemotron 3 Super 120B Q3 | 72.77% | 61,712,289,792 |
| MiniMax M2.7 Q2 | 77.29% | 83,302,711,296 |
| Sakura MiMo V2.6 Flash IQ2 | 79.88% | 57,761,339,136 |
| Flint Q4 | 76.24% | 23,387,911,136 |

None of these artifacts was active, used by production, or selected by the
queued stability and modified-model phases. They can be downloaded again from
their original sources if a future rerun is required.

## Heavy MiMo control

The exact Sakura P160 release only publishes its mixed IQ2_XS artifact; a
ready-made P160 Q3 or Q4 does not exist. To test whether the 79.88% result was
primarily caused by aggressive quantization and expert pruning, the queue adds
the full 256-expert MiMo-V2.6-Flash-MOPD 3.61 bpw Q3_K artifact from
`ddh0/MiMo-V2.6-Flash-MOPD-GGUF` (139,630,709,088 bytes).

This is a diagnostic parent-model control, not a clean quant-only comparison:
both precision and expert count change relative to Sakura P160. It uses mmap,
lazy expert reads, CPU-MoE placement and a 32 GiB Vulkan MoE cache so the
139.6 GB model can run despite exceeding currently free VRAM. A Q4 run is
deferred until Q3 demonstrates sufficient quality uplift and acceptable SSD
streaming speed.
