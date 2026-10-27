# Archived OpenClaw hard-suite re-score

Generated: `2026-10-16T09:58:38`
Evaluation profile: `openrouter-budget-reference-v2-20261016`
Complete 28-case runs: **42**
Incomplete or partial entries: **11**

This is an offline deterministic contract re-score of saved responses. Models were not run again.
Semantic v2 is not inferred where no semantic judge was executed.

## Complete runs

| Rank | Model | Source run | Old | Contract v2 | Delta | Length |
|---:|---|---|---:|---:|---:|---:|
| 1 | `qwen3.5-122b-a10b-q3-k-m / Qwen3.5-122B-A10B-Q3_K_M-00001-of-00003` | `openclaw-hard-qwen35q3-qwen36q6-gpu-reasoning-off-20260520-1024` | 85.34% | 90.44% | +5.10 pp | 4 |
| 2 | `qwen3.5-122b-a10b-mtp-ud-iq4-nl / Qwen3.5-122B-A10B-UD-IQ4_NL-00001-of-00003` | `openclaw-hard-qwen35-122b-a10b-iq4nl-2048tok-main-20260527-153441` | 84.93% | 90.04% | +5.10 pp | 0 |
| 3 | `qwen3.5-122b-a10b-mtp-ud-iq4-nl / Qwen3.5-122B-A10B-UD-IQ4_NL-00001-of-00003` | `openclaw-hard-qwen35-122b-a10b-iq4nl-2048tok-main-temp0-20260527-173707` | 84.93% | 90.04% | +5.10 pp | 0 |
| 4 | `qwen3.6-35b-a3b-mtp / Qwen3.6-35B-A3B-UD-Q6_K` | `openclaw-hard-mtp-enabled-qwen27-qwen35-2048tok-20260525-061538` | 87.14% | 90.02% | +2.88 pp | 0 |
| 5 | `qwen3.5-122b-a10b-q3-k-m / Qwen3.5-122B-A10B-Q3_K_M-00001-of-00003` | `openclaw-hard-qwen35-122b-q3-2048tok-gpu-reasoning-off-20260523-182731` | 83.27% | 88.61% | +5.34 pp | 0 |
| 6 | `minimax-m2.7-q2-k / MiniMax-M2.7-Q2_K-00001-of-00002` | `openclaw-hard-top10-mtp-run-1024tok-gpu-reasoning-off-20260523-153142` | 85.66% | 88.30% | +2.64 pp | 6 |
| 7 | `qwen3.6-27b-mtp / Qwen3.6-27B-UD-IQ3_XXS` | `openclaw-hard-truncation-check-2048tok-gpu-reasoning-off-20260523-174116` | 81.90% | 88.23% | +6.34 pp | 0 |
| 8 | `mlx / Qwen3-4B-Instruct-2507-4bit` | `openclaw-hard-mlx-qwen4b-gemma3n-2048tok-foreground-20260526-105129` | 83.41% | 88.20% | +4.79 pp | 0 |
| 9 | `qwen3.6-27b / Qwen3.6-27B-Q4_K_M` | `openclaw-hard-top10-mtp-run-1024tok-gpu-reasoning-off-20260523-153142` | 82.50% | 88.15% | +5.65 pp | 6 |
| 10 | `minimax-m2.7-q2-k / MiniMax-M2.7-Q2_K-00001-of-00002` | `openclaw-hard-truncation-check-2048tok-gpu-reasoning-off-20260523-174116` | 84.65% | 87.62% | +2.97 pp | 2 |
| 11 | `qwen3.5-122b-a10b-q3-k-m / Qwen3.5-122B-A10B-Q3_K_M-00001-of-00003` | `openclaw-hard-qwen35-122b-q3-20260520` | 80.18% | 87.61% | +7.44 pp | 8 |
| 12 | `qwen3.5-122b-a10b-q3-k-m / Qwen3.5-122B-A10B-Q3_K_M-00001-of-00003` | `openclaw-hard-top10-mtp-run-1024tok-gpu-reasoning-off-20260523-153142` | 80.29% | 87.42% | +7.13 pp | 4 |
| 13 | `qwen3.6-27b / Qwen3.6-27B-Q4_K_M` | `openclaw-hard-truncation-check-2048tok-gpu-reasoning-off-20260523-174116` | 81.40% | 87.06% | +5.65 pp | 0 |
| 14 | `local-imports / gemma-4-31B-it-uncensored-heretic-Q4_K_M` | `openclaw-hard-top10-mtp-run-1024tok-gpu-reasoning-off-20260523-153142` | 83.57% | 86.96% | +3.39 pp | 0 |
| 15 | `gemma-4-26b-a4b / gemma-4-26B-A4B-it-UD-Q4_K_M` | `openclaw-hard-top10-mtp-run-1024tok-gpu-reasoning-off-20260523-153142` | 82.23% | 86.77% | +4.54 pp | 1 |
| 16 | `local-imports / Qwen3.5-9B-Q5_K_M` | `openclaw-hard-top10-mtp-run-1024tok-gpu-reasoning-off-20260523-153142` | 80.93% | 86.68% | +5.75 pp | 2 |
| 17 | `gemma-4-e4b / gemma-4-E4B-it-Q5_K_M` | `openclaw-hard-top10-mtp-run-1024tok-gpu-reasoning-off-20260523-153142` | 81.74% | 86.66% | +4.92 pp | 3 |
| 18 | `local-imports / Qwen3.6-27B-UD-IQ2_M` | `openclaw-hard-top10-mtp-run-1024tok-gpu-reasoning-off-20260523-153142` | 79.28% | 86.33% | +7.05 pp | 5 |
| 19 | `qwen3.6-27b-mtp / Qwen3.6-27B-UD-IQ3_XXS` | `openclaw-hard-mtp-enabled-qwen27-qwen35-2048tok-20260525-061538` | 80.94% | 85.96% | +5.03 pp | 2 |
| 20 | `local-imports / gemma-4-26B-A4B-it-UD-Q3_K_M` | `openclaw-hard-top10-mtp-run-1024tok-gpu-reasoning-off-20260523-153142` | 83.31% | 85.95% | +2.64 pp | 2 |
| 21 | `mistral-medium-3.5-128b-q3-k-m / Mistral-Medium-3.5-128B-Q3_K_M-00001-of-00003` | `openclaw-hard-mistral-medium-2048tok-gpu-reasoning-off-20260525-054438` | 81.32% | 84.55% | +3.24 pp | 1 |
| 22 | `qwen3-coder-next-q4-k-m / Qwen3-Coder-Next-Q4_K_M` | `openclaw-hard-fresh3-2048tok-gpu-reasoning-off-20260524-101708` | 80.20% | 84.46% | +4.26 pp | 0 |
| 23 | `gemma-4-E4B-it-Q4_K_M / gemma-4-E4B-it-Q4_K_M` | `openclaw-hard-m3max-local-six-2048tok-20260526` | 78.35% | 84.17% | +5.82 pp | 0 |
| 24 | `Qwen3.5-9B-Q5_K_M / Qwen3.5-9B-Q5_K_M` | `openclaw-hard-m3max-local-six-2048tok-20260526` | 79.35% | 83.15% | +3.79 pp | 0 |
| 25 | `qwen3-coder-next-q4-k-m / Qwen3-Coder-Next-Q4_K_M` | `openclaw-hard-qwen3-coder-next-q4-2048tok-hard28-20260526-184822` | 79.76% | 82.73% | +2.97 pp | 0 |
| 26 | `glm-4.5-air-q3-k-m / GLM-4.5-Air-Q3_K_M-00001-of-00002` | `openclaw-hard-top10-mtp-run-1024tok-gpu-reasoning-off-20260523-153142` | 78.71% | 81.94% | +3.24 pp | 0 |
| 27 | `llama-3.1-nemotron-ultra-253b-q2-k / Llama-3_1-Nemotron-Ultra-253B-v1-Q2_K-00001-of-00002` | `openclaw-hard-nemotron-ctx32768-2048tok-gpu110-reasoning-off-20260524-232426` | 77.63% | 81.25% | +3.62 pp | 0 |
| 28 | `mimo-v2.5-ud-iq2-m / MiMo-V2.5-UD-IQ2_M-00001-of-00003` | `openclaw-hard-mimo-v25-iq2m-gpu-reasoning-off-20260523-134250` | 76.38% | 80.24% | +3.86 pp | 12 |
| 29 | `gemma-4-E2B-it-Q4_K_M / gemma-4-E2B-it-Q4_K_M` | `openclaw-hard-m3max-after-unload-speedcheck-20260526` | 75.33% | 79.78% | +4.45 pp | 0 |
| 30 | `gemma-4-E2B-it-Q4_K_M / gemma-4-E2B-it-Q4_K_M` | `openclaw-hard-m3max-local-six-2048tok-20260526` | 75.33% | 79.78% | +4.45 pp | 0 |
| 31 | `llama-3.3-70b-instruct-q4-k-m / Llama-3.3-70B-Instruct-Q4_K_M` | `openclaw-hard-llama33q4-llama4scoutq4-2048tok-reasoning-off-20260526-100444` | 76.17% | 79.08% | +2.91 pp | 0 |
| 32 | `qwen3.6-35b-a3b-mtp / Qwen3.6-35B-A3B-UD-Q6_K` | `openclaw-hard-qwen35q3-qwen36q6-gpu-reasoning-off-20260520-1024` | 75.70% | 79.02% | +3.32 pp | 3 |
| 33 | `qwen3.6-27b-mtp / Qwen3.6-27B-UD-IQ3_XXS` | `openclaw-hard-fresh-missing-gpu-reasoning-off-20260522` | 74.21% | 78.72% | +4.51 pp | 14 |
| 34 | `qwen3.6-35b-a3b-mtp / Qwen3.6-35B-A3B-UD-Q6_K` | `openclaw-hard-qwen122-qwen36q6-20260520` | 75.33% | 77.72% | +2.39 pp | 8 |
| 35 | `Qwen3.5-4B-Q5_K_M / Qwen3.5-4B-Q5_K_M` | `openclaw-hard-m3max-local-six-2048tok-20260526` | 72.38% | 76.56% | +4.17 pp | 1 |
| 36 | `huihui-qwen3.6-35b-a3b-abliterated-mtp-q4-k / Huihui-Qwen3.6-35B-A3B-abliterated-ggml-model-Q4_K` | `openclaw-hard-qwen-next-huihui-mtp-2048tok-hard28-20260526-164532-huihui-qwen36-35b-mmproj` | 73.15% | 75.82% | +2.67 pp | 0 |
| 37 | `gemma-4-31b / gemma-4-31B-it-Q6_K` | `openclaw-hard-fresh-missing-gpu-reasoning-off-20260522` | 71.71% | 75.65% | +3.94 pp | 12 |
| 38 | `llama-4-scout-17b-16e-instruct-q4-k-m / Llama-4-Scout-17B-16E-Instruct-Q4_K_M-00001-of-00002` | `openclaw-hard-llama33q4-llama4scoutq4-2048tok-reasoning-off-20260526-100444` | 71.99% | 74.50% | +2.52 pp | 0 |
| 39 | `gemma-3-12b-it-heretic-v2-q4 / gemma-3-12b-it-heretic-v2-Q4_K_M` | `openclaw-hard-m3max-local-six-2048tok-20260526` | 71.22% | 74.33% | +3.11 pp | 0 |
| 40 | `mistral-small-4-119b-2603-ud-q3-k-m / Mistral-Small-4-119B-2603-UD-Q3_K_M-00001-of-00003` | `openclaw-hard-fresh3-2048tok-gpu-reasoning-off-20260524-101708` | 70.77% | 74.33% | +3.56 pp | 0 |
| 41 | `mlx / gemma-3n-E2B-it-lm-4bit` | `openclaw-hard-mlx-gemma3n-direct-2048tok-20260526-110922` | 70.02% | 70.78% | +0.77 pp | 0 |
| 42 | `Phi-4-mini-instruct.Q5_K_S / Phi-4-mini-instruct.Q5_K_S` | `openclaw-hard-m3max-local-six-2048tok-20260526` | 68.40% | 69.24% | +0.84 pp | 0 |

## Incomplete entries

| Model | Source run | Cases | Responses |
|---|---|---:|---:|
| `llama-3.1-nemotron-ultra-253b-q2-k / Llama-3_1-Nemotron-Ultra-253B-v1-Q2_K-00001-of-00002` | `openclaw-hard-fresh3-2048tok-gpu-reasoning-off-20260524-101708` | 0 | 0 |
| `gpt-oss-120b-mxfp4 / gpt-oss-120b-mxfp4-00001-of-00003` | `openclaw-hard-gpt-oss-120b-mxfp4-2048tok-rerun-20260526-1048` | 28 | 23 |
| `gpt-oss-120b-mxfp4 / gpt-oss-120b-mxfp4-00001-of-00003` | `openclaw-hard-gpt-oss-120b-mxfp4-gpu-reasoning-off-20260520` | 28 | 22 |
| `mlx / Qwen3-4B-Instruct-2507-4bit` | `openclaw-hard-mlx-debug-onecase-20260526-105049` | 1 | 1 |
| `mlx / gemma-3n-E2B-it-lm-4bit` | `openclaw-hard-mlx-gemma3n-direct-debug-onecase-20260526-110904` | 1 | 1 |
| `mlx / Qwen3.5-9B-mlx-8bit-mtp` | `openclaw-hard-mlx-qwen35-9b-mtp-8bit-direct-smoke1-20260526-163102` | 1 | 1 |
| `mlx / Qwen3.5-9B-mlx-8bit-mtp` | `openclaw-hard-mlx-qwen35-9b-mtp-8bit-direct-smoke1-2048-20260526-163138` | 1 | 1 |
| `qwen3-next-80b-a3b-thinking-q4-k-m / Qwen_Qwen3-Next-80B-A3B-Thinking-Q4_K_M` | `openclaw-hard-qwen-next-huihui-mtp-2048tok-hard28-20260526-164532-qwen3-next` | 28 | 20 |
| `qwen3.5-122b-a10b-q3-k-m / Qwen3.5-122B-A10B-Q3_K_M-00003-of-00003` | `openclaw-hard-qwen122-qwen36q6-20260520` | 0 | 0 |
| `qwen3.5-122b-a10b-q3-k-m / Qwen3.5-122B-A10B-Q3_K_M-00002-of-00003` | `openclaw-hard-qwen122-qwen36q6-20260520` | 0 | 0 |
| `qwen3-next-80b-a3b-thinking-q4-k-m / Qwen_Qwen3-Next-80B-A3B-Thinking-Q4_K_M` | `openclaw-hard-qwen3-next-80b-thinking-q4-2048tok-hard28-rerun-20260526-193516` | 28 | 19 |
