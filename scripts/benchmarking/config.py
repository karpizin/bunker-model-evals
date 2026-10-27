import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# Base URLs
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")

# System Paths
LLAMA_SERVER_BIN = os.getenv("LLAMA_SERVER_BIN", "/opt/homebrew/bin/llama-server")
MODELS_DIR = Path(os.getenv("BUNKER_EVAL_MODELS_DIR", ROOT / "models"))
GGUF_MODEL_PATH = os.getenv("GGUF_MODEL_PATH", str(MODELS_DIR / "gguf" / "qwen-35b-moe.gguf"))
GRAMMAR_PATH = str(ROOT / "scripts" / "benchmarking" / "grammars" / "json_rpc.gbnf")

# GGUF Models for hybrid/llama benchmarks
GGUF_MODELS = [
    (str(MODELS_DIR / "gguf" / "qwen3.5-4b.gguf"), "Qwen3.5-4B"),
    (str(MODELS_DIR / "gguf" / "qwen3.5-9b.gguf"), "Qwen3.5-9B"),
    (str(MODELS_DIR / "gguf" / "qwen3-8b.gguf"), "Qwen3-8B"),
    (str(MODELS_DIR / "gguf" / "qwen-35b-moe.gguf"), "Qwen3.5-35B-MoE"),
    (str(MODELS_DIR / "gguf" / "qwen3-4b.gguf"), "Qwen3-4B"),
    (str(MODELS_DIR / "gguf" / "ministral-8b.gguf"), "Ministral-8B"),
    (str(MODELS_DIR / "gguf" / "gemma-3-12b.gguf"), "Gemma-3-12B"),
    (str(MODELS_DIR / "gguf" / "nemotron-70b.gguf"), "Nemotron-70B")
]

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Models
EMBED_MODEL_NAME = "mlx-community/all-MiniLM-L6-v2-4bit"

# Models for benchmarking

# Models for benchmarking
ALL_MODELS = [
    "qwen3.5:4b",           # 4.2B, Q5_K_M, 256k ctx
    "qwen3.5:9b",           # 9.0B, Q5_K_M, 256k ctx
    "qwen3.5:27b-q3",       # 26.9B, Q3_K_M, 256k ctx
    "qwen3.5:27b-q5",       # 26.9B, Q5_K_M, 256k ctx
    "qwen3.5:35b-q3",       # 34.7B, Q3_K_M, 256k ctx (MoE)
    "qwen3.5:35b-moe",      # 34.7B, Q4_K_M, 256k ctx (MoE)
    "gemma-3-12b",          # 11.8B, Q4_K_M, 128k ctx
    "ministral:latest",     # 3.4B, Q5_K_M, 256k ctx
    "ministral-14b:latest", # 13.5B, Q4_K_M, 256k ctx
    "nemotron:latest",      # 8.2B, Q5_K_M, 40k ctx 
    "glm-4:latest",         # 9.4B, Q6_K, 128k ctx
    "glm-4.7-flash:latest", # 23.0B, Q3_K_M, 200k ctx
    "phi-4:latest",         # 14.7B, Q4_K_M, 16k ctx
    "phi-4-mini:latest",    # 3.8B, Q5_K_S, 128k ctx
    "qwen3:8b",             # 8.2B, Q5_K_M, 40k ctx
    "qwen3:4b"              # 4.0B, Q5_K_M, 40k ctx
]

# Local models under 10B for evaluation (excluding Nemotron/GLM)
CONTESTANT_MODELS = [
    "qwen3.5:4b", 
    "qwen3.5:9b", 
    "qwen3:4b", 
    "qwen3:8b", 
    "phi-4-mini:latest", 
    "ministral:latest"
]

# OpenRouter Judge Models
JUDGE_MODELS = [
    "google/gemini-3-flash-preview",
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o",
    "x-ai/grok-4.1-fast",
    "nvidia/nemotron-3-super-120b-a12b:free"
]

# Default models for specific tasks
REASONING_MODEL = "qwen3.5:9b"

# Default Context Window for Benchmarks
DEFAULT_NUM_CTX = 32768

# Model-specific context limits (architectural)
MODEL_CONTEXT_LIMITS = {
    # Ollama Names
    "phi-4:latest": 16384,
    "nemotron:latest": 40960,
    "qwen3:8b": 40960,
    "qwen3:4b": 40960,
    # GGUF Aliases
    "Nemotron-70B": 131072, # The 70B version has 128k+
    "Phi-4": 16384
}

def get_model_ctx(model_name: str) -> int:
    """Returns the optimal context window for a model, respecting architectural limits."""
    # If the model has a known hardware/architectural limit lower than our default, use it.
    limit = MODEL_CONTEXT_LIMITS.get(model_name)
    if limit:
        return min(limit, DEFAULT_NUM_CTX)
    return DEFAULT_NUM_CTX

# Default Judge
DEFAULT_JUDGE = JUDGE_MODELS[0]
