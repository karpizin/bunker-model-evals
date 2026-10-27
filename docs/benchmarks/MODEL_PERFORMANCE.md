# Model Performance Benchmarks (March 2026)

Expanded evaluation suite: **12 cases** (Wikipedia, Internal Archive, IoT/MQTT, Edge Cases).
Tested on **Mac Mini 16GB** with **Ollama (Metal)**.

| Model | Speed (tok/s) | Logic (Tool Acc) | Verdict |
| :--- | :--- | :--- | :--- |
| **Ministral 14B** | **14.2** | 🥇 **92% (11/12)** | **Production Agent.** High reliability for complex RAG. |
| **Nemotron 8B** | **24.5** | 🥈 **83% (10/12)** | **IoT Controller.** Best for structured tool calls. |
| **Qwen3 8B** | **22.1** | 🥈 **83% (10/12)** | **Generalist.** Strong reasoning and wide knowledge. |
| **GLM-4 Flash** | **17.8** | 🥉 **75% (9/12)** | **Fallback.** Good balance, occasional JSON issues. |
| **Qwen3 4B** | **38.4** | **66% (8/12)** | **Fast Helper.** Good for simple queries. |
| **Ministral 3B** | **85.2** | **50% (6/12)** | **Sync Chat.** Fast, but prone to hallucinations. |

## Analysis

1.  **Ministral 3B** is the absolute winner for speed. It allows for near-instant responses in the "Bunker Command" interface.
2.  **Qwen3 (8B)** is significantly slower but provides better JSON schema compliance and reasoning for the agent's tool-calling loop.
3.  **Metal Acceleration** is active for all models. Memory contention with the indexer (MLX) was the primary cause of previous latency.

## Recommendations

- **Default Agent (RAG):** Use `ministral` for simple queries and `qwen3` for complex multi-tool reasoning.
- **Context Limit:** Set `num_ctx: 4096` to maintain high speed. Large context windows (32k+) significantly increase the time to first token on GGUF models.
- **Inference Engines:** 
    - **Ollama (llama.cpp)** is the best standard choice for GGUF.
    - **MLX** is recommended for embedding tasks (indexing) as it provides a ~100x speedup over CPU-based methods.
