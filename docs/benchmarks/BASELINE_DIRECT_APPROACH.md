# Archival Baseline: Direct Approach (Pre-Qwen 3.5)

These results represent the initial state of the Bunker AI benchmarking suite, using the **Direct Approach** (Ollama standard API) on **Mac Mini 16GB (Metal)**.

## 1. Tool Call Accuracy (12 Cases)
*Testing ability to select and format internal tools correctly.*

| Model | Speed (tok/s) | Logic (Tool Acc) | Verdict |
| :--- | :--- | :--- | :--- |
| **Ministral 14B** | 14.2 | **92% (11/12)** | 🥇 Best logic |
| **Nemotron 8B** | **24.5** | **83% (10/12)** | 🥈 Best balance |
| **Qwen3 8B** (Legacy) | 22.1 | **83% (10/12)** | 🥈 Strong generalist |
| **GLM-4 Flash** | 17.8 | 75% (9/12) | 🥉 Occasional errors |
| **Qwen3 4B** | **38.4** | 66% (8/12) | Fast but inaccurate |
| **Ministral 3B** | **85.2** | 50% (6/12) | High hallucination |

---

## 2. MCP Protocol Adherence (Direct Approach)
*Testing raw adherence to JSON-RPC 2.0 without GBNF or Hybrid optimizations.*

| Model | Latency (Phase 1) | Adherence | Root Cause of Failure |
| :--- | :--- | :--- | :--- |
| **Ministral 8B** | ~45s | 1/3 Passed | Conversational noise ("Here is your JSON...") |
| **Qwen 3.5 35B-MoE** | **155.0s** | 2/3 Passed | Value hallucinations (`server room` vs `server_room`) |

---

## 3. Historical Limitations
- **No GBNF**: Structural integrity relied entirely on system prompt and regex/brace-counting extractors.
- **Conversational Noise**: All models in direct mode tended to wrap JSON in conversational prose, making parsing unreliable.
- **High Latency**: Significant Ollama launch overhead and model loading contention.

---
*Report archived on: March 16, 2026*
