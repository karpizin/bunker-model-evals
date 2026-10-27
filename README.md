# Bunker Model Evals

Reproducible, model-focused evaluations for local GGUF and hosted language
models. This repository contains model corpora, runners, scoring logic,
quantization studies, compatibility suites, and selected raw results. It does
not contain Bunker AI product, module, customer, or acceptance-test code.

[![CI](https://github.com/karpizin/bunker-model-evals/actions/workflows/ci.yml/badge.svg)](https://github.com/karpizin/bunker-model-evals/actions/workflows/ci.yml)
[![Security](https://github.com/karpizin/bunker-model-evals/actions/workflows/security.yml/badge.svg)](https://github.com/karpizin/bunker-model-evals/actions/workflows/security.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

## What is here

- **Bunker Benchmark v3/v3.1** — 20 outcome-oriented cases covering synthesis,
  agent execution, result validation, grounded retrieval, and code/operations.
- **Local model matrices** — speed, output integrity, knowledge, reasoning,
  planning, and quantization comparisons on Apple Silicon and AMD/Vulkan.
- **Hosted references** — fixed-model comparisons with deterministic contract
  checks and separately reported semantic judgement.
- **Tool-call compatibility** — normalization and scoring for OpenAI, Hermes,
  Qwen, Mistral, Gemma, DeepSeek, MiMo, and related model-native formats.
- **Published evidence** — sanitized raw results, manifests, hashes, CSV
  summaries, and explicit exclusion records.

Start with the [benchmark catalogue](docs/benchmarks/README.md), the
[v3 methodology](docs/benchmarks/BUNKER_BENCHMARK_V3.md), the
[latest v3.1 ranking](docs/benchmarks/BUNKER_BENCHMARK_V3_1_RESCORE_20261027.md),
and the [October 2026 raw-result bundle](docs/benchmarks/results/bunker-v3-public-results-20261027/README.md).

## Quick start

Requirements: Python 3.12 and Git. Model-backed runs may additionally require
Ollama, llama.cpp, MLX, or a compatible HTTP endpoint.

```bash
git clone https://github.com/karpizin/bunker-model-evals.git
cd bunker-model-evals
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make test
make smoke
```

Validate the v3 corpus without loading a model:

```bash
python scripts/benchmarking/bunker_benchmark_v3.py --validate-only
```

Run a local GGUF matrix:

```bash
python scripts/benchmarking/local_gguf_matrix.py \
  --models-dir "$HOME/bunker-data/models" \
  --direct-host
```

Runners never download model weights implicitly. Credentials, model files,
private corpora, and unredacted machine logs must remain outside the repository.

## Scope boundary

This repository evaluates models and model-serving configurations. Bunker AI
module tests, product acceptance suites, memory-provider integration, EV News,
Protocolist, Geo, and other application-specific evaluations remain in the
private `bunker-evals` repository.

See [SCOPE.md](docs/SCOPE.md) and the
[publication policy](docs/PUBLICATION_POLICY.md) before adding a suite or result.

Licensed under the [Apache License 2.0](LICENSE).
