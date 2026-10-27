#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR="${BUNKER_EVAL_GGUF_DIR:-models/gguf}"
OLLAMA_BLOB_DIR="${OLLAMA_BLOB_DIR:-$HOME/.ollama/models/blobs}"
SOURCE_MODEL_DIR="${BUNKER_EVAL_MODEL_SOURCE_DIR:-$HOME/bunker-data/models}"
mkdir -p "$MODEL_DIR"

# Mapping of Model Names to Ollama Blob Shas
# Values extracted from earlier 'cat' of manifests

# Qwen 3.5 35B MoE
ln -sf "$OLLAMA_BLOB_DIR/sha256-0f135a59159030f4710477abc6f9922d2f13552c85bff736deaaef71023cd770" "$MODEL_DIR/qwen-35b-moe.gguf"

# Qwen 3.5 35B Q3
ln -sf "$OLLAMA_BLOB_DIR/sha256-5607c8fcc8b04ada7d1a1152b9a5b6c1e67e6768232c16f6b03d9719d5ab1b2d" "$MODEL_DIR/qwen-35b-q3.gguf"

# Qwen 3.5 27B Q5
ln -sf "$OLLAMA_BLOB_DIR/sha256-e41a488a3f013dbfb323563d7250105b1e708daf084942f9011344ad1525996f" "$MODEL_DIR/qwen-27b-q5.gguf"

# Qwen 3.5 27B Q3
ln -sf "$OLLAMA_BLOB_DIR/sha256-f08ce37ebe8a7130db0c198262336773976b1e374f2444f898c41117710f0bb3" "$MODEL_DIR/qwen-27b-q3.gguf"

# Qwen 3 8B
ln -sf "$OLLAMA_BLOB_DIR/sha256-0a7127b800d5239d4bc68e013f4ed8b41f269401989d6e45213dfcf5f94f5039" "$MODEL_DIR/qwen3-8b.gguf"

# Qwen 3 4B
ln -sf "$OLLAMA_BLOB_DIR/sha256-37edbd37f5b7a4d4e7a766400c57def1f790e809de03513b86bf11bb06979695" "$MODEL_DIR/qwen3-4b.gguf"

# Ministral 8B (latest)
ln -sf "$OLLAMA_BLOB_DIR/sha256-1ea1f4a720f56dad1cc912512d71dad6fbe59bcf101643c0765f63d0886e80a6" "$MODEL_DIR/ministral-8b.gguf"

# Ministral 14B
ln -sf "$OLLAMA_BLOB_DIR/sha256-dd49ec994c15788d4fbad3740c9fb7ef5835d70edc53a85c6f794164ed391aa1" "$MODEL_DIR/ministral-14b.gguf"

# Nemotron
ln -sf "$OLLAMA_BLOB_DIR/sha256-792230ba50b5975609e96f5bb82ac17afa886da5e6d2b7ad5cd3daf2f5333e6b" "$MODEL_DIR/nemotron-70b.gguf"

# GLM-4
ln -sf "$OLLAMA_BLOB_DIR/sha256-068bae163faa96ad48032daf4e071a6a28fe67d8dcc95367609c2ff165e52738" "$MODEL_DIR/glm4-9b.gguf"

# New Local Models
ln -sf "$SOURCE_MODEL_DIR/Qwen3.5-4B-Q5_K_M.gguf" "$MODEL_DIR/qwen3.5-4b.gguf"
ln -sf "$SOURCE_MODEL_DIR/Qwen3.5-9B-Q5_K_M.gguf" "$MODEL_DIR/qwen3.5-9b.gguf"
ln -sf "$SOURCE_MODEL_DIR/gemma-3-12b-it-heretic-v2-Q4_K_M.gguf" "$MODEL_DIR/gemma-3-12b.gguf"
ln -sf "$SOURCE_MODEL_DIR/GLM-4.7-Flash-REAP-23B-A3B-Q3_K_M.gguf" "$MODEL_DIR/glm-4.7-flash.gguf"
ln -sf "$SOURCE_MODEL_DIR/phi-4-Q4_K.gguf" "$MODEL_DIR/phi-4.gguf"
ln -sf "$SOURCE_MODEL_DIR/Phi-4-mini-instruct.Q5_K_S.gguf" "$MODEL_DIR/phi-4-mini.gguf"

echo "Symlinks created in $MODEL_DIR"
ls -lh "$MODEL_DIR"
