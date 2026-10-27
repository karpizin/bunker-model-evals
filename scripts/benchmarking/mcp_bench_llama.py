"""
Llama-Server MCP Adherence Benchmark
------------------------------------
Purpose: Tests LLM ability to follow JSON-RPC 2.0 protocol using llama-server (GBNF).
Key Features:
- Uses llama-server with GBNF grammar for constrained tool-call generation.
- Validates the 3 standard MCP test cases (Blueprint, Valve, Sensors).
- Specifically tests the 35B MoE model (or other GGUF models).

Usage:
  python mcp_bench_llama.py

Dependencies: config.py, requests, llama-server, scripts/benchmarking/grammars/json_rpc.gbnf
"""
import requests
import json
import time
import logging
import sys
import subprocess
import os
import signal
import re

# Import shared configuration
try:
    from config import OLLAMA_URL # For health checks or other if needed
except ImportError:
    OLLAMA_URL = "http://127.0.0.1:11434"

# Import shared configuration
try:
    from config import OLLAMA_URL, LLAMA_SERVER_BIN, GGUF_MODEL_PATH, GRAMMAR_PATH, DEFAULT_NUM_CTX, get_model_ctx
except ImportError:
    OLLAMA_URL = "http://127.0.0.1:11434"
    LLAMA_SERVER_BIN = "/opt/homebrew/bin/llama-server"
    GGUF_MODEL_PATH = "models/gguf/qwen-35b-moe.gguf"
    GRAMMAR_PATH = "scripts/benchmarking/grammars/json_rpc.gbnf"
    DEFAULT_NUM_CTX = 4096
    def get_model_ctx(m): return 4096

# Constants
MODEL_PATH = GGUF_MODEL_PATH
SERVER_URL = "http://127.0.0.1:8080/completion"

MCP_CASES = [
    {
        "name": "MCP: Knowledge Retrieval",
        "description": "Call a tool to search for specific bunker blueprints.",
        "goal": "I need the blueprints for the Level 4 air filtration system.",
        "expected_tool": "retrieve_blueprint",
        "expected_args": {"level": 4, "system": "air_filtration"}
    },
    {
        "name": "MCP: IoT Action",
        "description": "Call a tool to change environment state.",
        "goal": "The pressure in Sector 7 is rising. Open the emergency vent.",
        "expected_tool": "set_valve_state",
        "expected_args": {"sector": 7, "valve_type": "emergency_vent", "state": "open"}
    },
    {
        "name": "MCP: Data Synthesis",
        "description": "Retrieve logs and analyze them.",
        "goal": "Get the temperature logs for the last 24 hours for the server room.",
        "expected_tool": "get_sensor_history",
        "expected_args": {"sensor": "temperature", "location": "server_room", "duration_hours": 24}
    }
]

# We use the same system prompt but we'll adapt the format for llama-server
MCP_SYSTEM_PROMPT = """[HUB_IDENT: L1_PROXY]
[MODE: STRICT_JSON_RPC_2.0]

You are a terminal interface for bunker systems. 
You must output ONLY one valid JSON-RPC 2.0 request object.

### MANDATORY SCHEMA:
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "EXACT_TOOL_NAME",
    "arguments": { ... }
  },
  "id": 1
}

### TOOL REGISTRY:
1. retrieve_blueprint: {"level": int, "system": str}
2. set_valve_state: {"sector": int, "valve_type": str, "state": "open" | "closed"}
3. get_sensor_history: {"sensor": str, "location": str, "duration_hours": int}
"""

class LlamaServer:
    def __init__(self, model_path, n_gpu_layers=99, n_ctx=DEFAULT_NUM_CTX):
        self.model_path = model_path
        self.n_gpu_layers = n_gpu_layers
        self.n_ctx = n_ctx
        self.process = None

    def start(self):
        logger.info(f"Starting llama-server for model: {self.model_path}")
        # Clear previous log
        if os.path.exists("llama_server.log"):
            os.remove("llama_server.log")
            
        cmd = [
            LLAMA_SERVER_BIN,
            "-m", self.model_path,
            "-ngl", str(self.n_gpu_layers),
            "-c", str(self.n_ctx),
            "--port", "8080",
            "--host", "127.0.0.1"
        ]
        # Redirect stderr to file for debugging
        self.log_file = open("llama_server.log", "w")
        self.process = subprocess.Popen(cmd, stdout=self.log_file, stderr=self.log_file)
        
        # Wait for server to be ready
        max_retries = 120  # Give it 2 minutes for 35B model
        for i in range(max_retries):
            if i % 10 == 0:
                logger.info(f"Waiting for server... ({i}s)")
            try:
                response = requests.get("http://127.0.0.1:8080/health", timeout=2, proxies={"http": None, "https": None})
                if response.status_code == 200:
                    logger.info("llama-server is ready")
                    return True
            except:
                pass
            time.sleep(1)
        
        logger.error("llama-server failed to start. Check llama_server.log")
        return False

    def stop(self):
        if self.process:
            logger.info("Stopping llama-server...")
            self.process.terminate()
            self.process.wait()
            if hasattr(self, 'log_file'):
                self.log_file.close()
            self.process = None

def run_test(case, grammar_content):
    prompt = f"<|im_start|>system\n{MCP_SYSTEM_PROMPT}<|im_end|>\n"
    prompt += f"<|im_start|>user\nGoal: {case['goal']}<|im_end|>\n"
    prompt += "<|im_start|>assistant\n"

    payload = {
        "prompt": prompt,
        "temperature": 0.0,
        "grammar": grammar_content,
        "n_predict": 256,
        "stop": ["<|im_end|>", "User:", "Goal:"]
    }

    try:
        start_time = time.time()
        response = requests.post(SERVER_URL, json=payload, timeout=300, proxies={"http": None, "https": None})
        end_time = time.time()
        duration = end_time - start_time

        if response.status_code != 200:
            return {"passed": False, "error": f"Server error: {response.text}", "duration": duration}

        result = response.json()
        raw_text = result.get("content", "").strip()
        logger.debug(f"RAW CONTENT: {raw_text}")

        # Robust JSON extraction (same as in mcp_bench.py)
        clean_text = raw_text
        if "<think>" in clean_text:
            clean_text = re.sub(r'<think>.*?</think>', '', clean_text, flags=re.DOTALL).strip()
            
        if "{" in clean_text:
            start = clean_text.find("{")
            count = 0
            end = -1
            for i in range(start, len(clean_text)):
                if clean_text[i] == "{": count += 1
                elif clean_text[i] == "}": count -= 1
                if count == 0:
                    end = i
                    break
            if end != -1:
                clean_text = clean_text[start:end+1]

        try:
            parsed = json.loads(clean_text)
        except json.JSONDecodeError:
            return {"passed": False, "error": f"Invalid JSON: {clean_text}", "duration": duration}
        
        actual_tool = parsed.get("params", {}).get("name")
        actual_args = parsed.get("params", {}).get("arguments")
        
        tool_match = actual_tool == case["expected_tool"]
        args_match = all(actual_args.get(k) == v for k, v in case["expected_args"].items()) if isinstance(actual_args, dict) else False
        
        passed = tool_match and args_match
        
        return {
            "passed": passed,
            "duration": duration,
            "response": parsed,
            "checks": {"tool": tool_match, "args": args_match}
        }
    except Exception as e:
        return {"passed": False, "error": str(e), "duration": 0}

def main():
    if not os.path.exists(MODEL_PATH):
        logger.error(f"Model not found at {MODEL_PATH}")
        return

    with open(GRAMMAR_PATH, "r") as f:
        grammar_content = f.read()

    server = LlamaServer(MODEL_PATH, n_ctx=get_model_ctx("Qwen3.5-35B-MoE"))
    if not server.start():
        return

    try:
        results = []
        for case in MCP_CASES:
            logger.info(f"Running test: {case['name']}")
            res = run_test(case, grammar_content)
            results.append(res)
            status = "✅ PASSED" if res["passed"] else "❌ FAILED"
            logger.info(f"{status} in {res['duration']:.2f}s")
            if not res["passed"]:
                logger.debug(f"Expected: {case['expected_tool']} with {case['expected_args']}")
                logger.debug(f"Got: {res.get('response')}")

        total_passed = sum(1 for r in results if r["passed"])
        avg_time = sum(r["duration"] for r in results) / len(results)
        logger.info(f"--- Final Result: {total_passed}/{len(MCP_CASES)} passed ---")
        logger.info(f"--- Average Time: {avg_time:.2f}s ---")

    finally:
        server.stop()

if __name__ == "__main__":
    main()
