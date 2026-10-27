import requests
import json
import time
import logging
import sys
import subprocess
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
LLAMA_SERVER_BIN = "/opt/homebrew/bin/llama-server"
OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"
GRAMMAR_PATH = "scripts/benchmarking/grammars/tool_calling.gbnf"
REASONING_MODEL = "qwen3.5:9b"

# Test cases from tool_bench.py
TEST_CASES = [
    {"name": "Wiki: Simple Geography", "goal": "What is the largest desert in the world?", "expected_tool": "search_wikipedia"},
    {"name": "IoT: Lighting Control", "goal": "Turn on the lights in the laboratory.", "expected_tool": "toggle_light"},
    {"name": "Archive: Maintenance", "goal": "Find the manual for the air filtration system model V4.", "expected_tool": "search_internal_archive"},
    {"name": "Chat: Greeting", "goal": "Good morning Bunker AI, identify yourself.", "expected_tool": ""}
]

TOOLS_INFO = """
Available tools:
1. search_wikipedia: General knowledge, history, geography.
2. search_internal_archive: Private bunker manuals, security, inventory.
3. toggle_light: Lighting control. Args: {"state": "on/off", "room": "room name"}
"""

class LlamaServer:
    def __init__(self, model_path, port=8080):
        self.model_path = model_path
        self.port = port
        self.process = None

    def start(self):
        logger.info(f"Starting llama-server for model: {self.model_path}")
        cmd = [
            LLAMA_SERVER_BIN,
            "-m", self.model_path,
            "-ngl", "99",
            "-c", "4096",
            "--port", str(self.port),
            "--host", "127.0.0.1"
        ]
        self.log_file = open("hybrid_tool_server.log", "w")
        self.process = subprocess.Popen(cmd, stdout=self.log_file, stderr=self.log_file)
        
        for i in range(60):
            try:
                response = requests.get(f"http://127.0.0.1:{self.port}/health", timeout=2, proxies={"http": None, "https": None})
                if response.status_code == 200:
                    logger.info("llama-server is ready")
                    return True
            except:
                pass
            time.sleep(1)
        return False

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.log_file.close()

def get_reasoning(goal, retries=3):
    prompt = f"Goal: {goal}\n\nThink about how to solve this using our bunker tools. Provide a plan."
    payload = {
        "model": REASONING_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.0}
    }
    
    for attempt in range(retries):
        try:
            start = time.time()
            response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=600, proxies={"http": None, "https": None})
            duration = time.time() - start
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", ""), duration
            logger.warning(f"Reasoning attempt {attempt+1} failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"Reasoning attempt {attempt+1} exception: {e}")
        time.sleep(2)
    return None, 0

def get_tool_call(reasoning, goal, grammar_content, port=8080):
    system_p = f"""You are Bunker AI. Use the reasoning provided to generate a tool call JSON.
{TOOLS_INFO}

CRITICAL RULES:
- 'final_answer' MUST NEVER BE EMPTY.
- If you ARE calling a tool: Use 'final_answer' to explain your intent to the user (e.g., "I am searching the archives for Sector 7 protocols.").
- If you are NOT calling a tool: Provide the complete answer in 'final_answer'."""
    prompt = f"<|im_start|>system\n{system_p}<|im_end|>\n"
    prompt += f"<|im_start|>user\nReasoning: {reasoning}\nGoal: {goal}<|im_end|>\n"
    prompt += "<|im_start|>assistant\n"

    payload = {
        "prompt": prompt,
        "temperature": 0.0,
        "grammar": grammar_content,
        "n_predict": 512,
        "stop": ["<|im_end|>"]
    }
    start = time.time()
    response = requests.post(f"http://127.0.0.1:{port}/completion", json=payload, timeout=60, proxies={"http": None, "https": None})
    duration = time.time() - start
    if response.status_code == 200:
        return response.json().get("content", "").strip(), duration
    return None, 0

def main():
    models_to_test = [
        ("models/gguf/qwen3.5-4b.gguf", "Qwen3.5-4B"),
        ("models/gguf/qwen3.5-9b.gguf", "Qwen3.5-9B"),
        ("models/gguf/gemma-3-12b.gguf", "Gemma-3-12B")
    ]

    if not os.path.exists(GRAMMAR_PATH):
        logger.error(f"Grammar {GRAMMAR_PATH} not found")
        return

    with open(GRAMMAR_PATH, "r") as f:
        grammar = f.read()

    overall_results = []

    for model_path, model_name in models_to_test:
        if not os.path.exists(model_path):
            logger.warning(f"Model {model_path} not found, skipping...")
            continue

        logger.info(f"=== Testing Hybrid: Ollama({REASONING_MODEL}) + llama.cpp({model_name}) ===")
        server = LlamaServer(model_path)
        if not server.start(): continue

        try:
            model_results = []
            for case in TEST_CASES:
                try:
                    logger.info(f"--- Case: {case['name']} ---")
                    
                    logger.info("Phase 1: Reasoning...")
                    reasoning, r_time = get_reasoning(case['goal'])
                    if not reasoning:
                        logger.error(f"Failed to get reasoning for {case['name']}")
                        model_results.append({"name": case['name'], "passed": False, "r_time": 0, "t_time": 0})
                        continue

                    logger.info("Phase 2: Action...")
                    tool_call, t_time = get_tool_call(reasoning, case['goal'], grammar)
                    if not tool_call:
                        logger.error(f"Failed to get tool call for {case['name']}")
                        model_results.append({"name": case['name'], "passed": False, "r_time": r_time, "t_time": 0})
                        continue

                    try:
                        parsed = json.loads(tool_call)
                        actual_tool = parsed.get("tool", "")
                        passed = actual_tool == case["expected_tool"]
                    except:
                        passed = False
                    
                    status = "✅" if passed else "❌"
                    logger.info(f"{status} R:{r_time:.1f}s T:{t_time:.1f}s | Result: {tool_call}")
                    model_results.append({"name": case['name'], "passed": passed, "r_time": r_time, "t_time": t_time})
                except Exception as e:
                    logger.error(f"Error in test case {case['name']}: {e}")
                    model_results.append({"name": case['name'], "passed": False, "r_time": 0, "t_time": 0})
            
            overall_results.append({"model": model_name, "results": model_results})
        
        finally:
            server.stop()

    print("\n\n=== FINAL HYBRID TOOL BENCHMARK SUMMARY ===")
    print(f"{'Model':<20} | {'Score':<5} | {'Avg R-Time':<12} | {'Avg T-Time':<12}")
    print("-" * 60)
    for res in overall_results:
        passed = sum(1 for r in res['results'] if r['passed'])
        avg_r = sum(r['r_time'] for r in res['results']) / len(res['results'])
        avg_t = sum(r['t_time'] for r in res['results']) / len(res['results'])
        print(f"{res['model']:<20} | {passed}/4  | {avg_r:<12.2f} | {avg_t:<12.2f}")

if __name__ == "__main__":
    main()
