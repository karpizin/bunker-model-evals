"""
Hybrid MCP Benchmark (Ollama + llama.cpp)
----------------------------------------
Purpose: Evaluates a two-phase tool-calling approach (Reasoning + GBNF Extraction).
Key Features:
- Phase 1: High-quality reasoning via Ollama (qwen3.5:9b).
- Phase 2: Strict JSON-RPC extraction via llama.cpp and GBNF grammar.
- Uses llama-server for low-latency, constrained generation.

Usage:
  python mcp_bench_hybrid.py

Dependencies: config.py, requests, llama-server, scripts/benchmarking/grammars/json_rpc.gbnf
"""
import requests
import json
import time
import logging
import sys
import subprocess
import os
import re

# Import shared configuration
try:
    from config import OLLAMA_URL, REASONING_MODEL, LLAMA_SERVER_BIN, GGUF_MODELS, GRAMMAR_PATH, DEFAULT_NUM_CTX, get_model_ctx
    OLLAMA_CHAT_URL = f"{OLLAMA_URL}/api/chat"
    OLLAMA_GENERATE_URL = f"{OLLAMA_URL}/api/generate"
except ImportError:
    OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
    OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
    REASONING_MODEL = "qwen3.5:9b"
    LLAMA_SERVER_BIN = "/opt/homebrew/bin/llama-server"
    GRAMMAR_PATH = "scripts/benchmarking/grammars/json_rpc.gbnf"
    GGUF_MODELS = [("models/gguf/qwen3.5-4b.gguf", "Qwen3.5-4B")]
    DEFAULT_NUM_CTX = 4096
    def get_model_ctx(m): return 4096

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

class LlamaServer:
    def __init__(self, model_path, n_gpu_layers=99, n_ctx=DEFAULT_NUM_CTX, port=8080):
        self.model_path = model_path
        self.n_gpu_layers = n_gpu_layers
        self.n_ctx = n_ctx
        self.port = port
        self.process = None

    def start(self):
        logger.info(f"Starting llama-server for model: {self.model_path} on port {self.port}")
        # Clear previous log
        if os.path.exists("hybrid_server.log"):
            os.remove("hybrid_server.log")

        cmd = [
            LLAMA_SERVER_BIN,
            "-m", self.model_path,
            "-ngl", str(self.n_gpu_layers),
            "-c", str(self.n_ctx),
            "--port", str(self.port),
            "--host", "127.0.0.1"
        ]
        # Redirect output to file
        self.log_file = open("hybrid_server.log", "w")
        self.process = subprocess.Popen(cmd, stdout=self.log_file, stderr=self.log_file)
        
        # Wait for server to be ready
        max_retries = 120
        for i in range(max_retries):
            if i % 10 == 0:
                logger.debug(f"Waiting for server... ({i}s)")
            try:
                response = requests.get(f"http://127.0.0.1:{self.port}/health", timeout=2, proxies={"http": None, "https": None})
                if response.status_code == 200:
                    logger.info("llama-server is ready")
                    return True
            except:
                pass
            time.sleep(1)
        
        logger.error(f"llama-server failed to start for {self.model_path}. Check hybrid_server.log")
        return False

    def stop(self):
        if self.process:
            logger.info("Stopping llama-server...")
            self.process.terminate()
            self.process.wait()
            if hasattr(self, 'log_file'):
                self.log_file.close()
            self.process = None

def get_reasoning(goal, retries=3):
    """Phase 1: Get reasoning from Ollama with retries."""
    prompt = f"Goal: {goal}\n\nThink about how to solve this using our bunker tools. Provide a concise step-by-step plan."
    payload = {
        "model": REASONING_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_ctx": get_model_ctx(REASONING_MODEL)
        }
    }
    
    for attempt in range(retries):
        try:
            start_time = time.time()
            response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=600, proxies={"http": None, "https": None})
            duration = time.time() - start_time
            if response.status_code == 200:
                content = response.json().get("message", {}).get("content", "")
                return content, duration
            logger.warning(f"Reasoning attempt {attempt+1} failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"Reasoning attempt {attempt+1} exception: {e}")
        time.sleep(2)
    return None, 0

def get_tool_call(reasoning, goal, grammar_content, port=8080):
    """Phase 2: Use llama.cpp + GBNF to generate the JSON-RPC."""
    # Define available tools for the model
    tools_info = """
Available Tools:
1. retrieve_blueprint(level: int, system: str) - Search for bunker blueprints.
2. set_valve_state(sector: int, valve_type: str, state: str) - Control vents and valves.
3. get_sensor_history(sensor: str, location: str, duration_hours: int) - Get historical data.
"""
    
    system_prompt = f"You are a precise tool-calling agent. Below is a reasoning process and a user goal. Your mission is to pick the CORRECT tool from the list and generate a valid JSON-RPC 2.0 call.\n\n{tools_info}\n- YOU MUST STOP GENERATING IMMEDIATELY after closing the JSON-RPC object.\n- DO NOT simulate the next conversational turn."
    
    prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
    prompt += f"<|im_start|>user\nReasoning: {reasoning}\nGoal: {goal}<|im_end|>\n"
    prompt += "<|im_start|>assistant\n"

    payload = {
        "prompt": prompt,
        "temperature": 0.0,
        "grammar": grammar_content,
        "n_predict": 256,
        "stop": ["<|im_end|>", "Goal:", "User:", "\nUser:", "\nGoal:"]
    }

    start_time = time.time()
    response = requests.post(f"http://127.0.0.1:{port}/completion", json=payload, timeout=60, proxies={"http": None, "https": None})
    duration = time.time() - start_time

    if response.status_code == 200:
        content = response.json().get("content", "").strip()
        return content, duration
    return None, 0

def validate_call(content, case):
    try:
        if not content: return False
        parsed = json.loads(content)
        params = parsed.get("params", {})
        actual_tool = params.get("name")
        actual_args = params.get("arguments", {})
        
        tool_match = actual_tool == case["expected_tool"]
        
        # Normalize args (handle server_room vs server room)
        def normalize(v):
            if isinstance(v, str):
                return v.lower().replace("_", " ").strip()
            return v
        
        args_match = True
        if not isinstance(actual_args, dict):
            args_match = False
        else:
            for k, v in case["expected_args"].items():
                actual_v = actual_args.get(k)
                if normalize(actual_v) != normalize(v):
                    args_match = False
                    break
        
        return tool_match and args_match
    except:
        return False

def main():
    models_to_test = GGUF_MODELS

    with open(GRAMMAR_PATH, "r") as f:
        grammar_content = f.read()

    results = []

    for model_path, model_name in models_to_test:
        if not os.path.exists(model_path):
            logger.warning(f"Model {model_path} not found, skipping...")
            continue
            
        logger.info(f"=== Testing Hybrid: Ollama({REASONING_MODEL}) + llama.cpp({model_name}) ===")
        server = LlamaServer(model_path, n_ctx=get_model_ctx(model_name))
        if not server.start():
            continue

        try:
            model_results = []
            for case in MCP_CASES:
                try:
                    logger.info(f"--- Case: {case['name']} ---")
                    
                    # Reasoning
                    logger.info(f"Phase 1: Requesting reasoning from Ollama ({REASONING_MODEL})...")
                    reasoning, r_time = get_reasoning(case['goal'])
                    if not reasoning:
                        logger.error("Reasoning failed")
                        model_results.append({"case": case['name'], "passed": False, "r_time": 0, "t_time": 0, "total_time": 0})
                        continue
                    logger.info(f"Reasoning received in {r_time:.1f}s")
                    
                    # Tool Call
                    logger.info(f"Phase 2: Extracting tool call via llama.cpp (GBNF)...")
                    tool_call, t_time = get_tool_call(reasoning, case['goal'], grammar_content)
                    if not tool_call:
                        logger.error("Tool call extraction failed")
                        model_results.append({"case": case['name'], "passed": False, "r_time": r_time, "t_time": 0, "total_time": r_time})
                        continue
                    logger.info(f"Tool call extracted in {t_time:.1f}s")
                    
                    passed = validate_call(tool_call, case)
                    
                    model_results.append({
                        "case": case['name'],
                        "passed": passed,
                        "r_time": r_time,
                        "t_time": t_time,
                        "total_time": r_time + t_time
                    })
                    
                    status = "✅" if passed else "❌"
                    logger.info(f"{status} R:{r_time:.1f}s T:{t_time:.1f}s | Result: {tool_call}")
                except Exception as e:
                    logger.error(f"Execution failed for case {case['name']}: {e}")
                    model_results.append({"case": case['name'], "passed": False, "r_time": 0, "t_time": 0, "total_time": 0})

            results.append({"model": model_name, "stats": model_results})

        finally:
            server.stop()

    # Summary Table
    print("\n\n=== FINAL HYBRID BENCHMARK SUMMARY ===")
    print(f"{'Model':<20} | {'Score':<5} | {'Avg R-Time':<12} | {'Avg T-Time':<12}")
    print("-" * 60)
    for res in results:
        passed = sum(1 for s in res['stats'] if s['passed'])
        avg_r = sum(s['r_time'] for s in res['stats']) / len(res['stats'])
        avg_t = sum(s['t_time'] for s in res['stats']) / len(res['stats'])
        print(f"{res['model']:<20} | {passed}/3  | {avg_r:<12.2f} | {avg_t:<12.2f}")

if __name__ == "__main__":
    main()
