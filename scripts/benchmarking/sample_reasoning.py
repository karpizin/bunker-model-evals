"""
Sample Reasoning Generator
--------------------------
Purpose: Quick manual inspection of LLM reasoning quality for specific scenarios.
Key Features:
- 2 complex scenarios: Resource Prioritization, Ethics & Security.
- Outputs raw model response for qualitative review.

Usage:
  python sample_reasoning.py --model qwen3.5:4b --case "Resource Prioritization"

Dependencies: config.py, requests
"""
import requests
import json
import argparse
import sys
import os

# Import shared configuration
try:
    from config import OLLAMA_URL
    OLLAMA_API_URL = f"{OLLAMA_URL}/api/generate"
except ImportError:
    OLLAMA_API_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = "You are Bunker AI, a strategic and highly logical fortress intelligence. Provide deep, multi-step reasoning and detailed analysis. No brevity required."

CASES = {
    "Resource Prioritization": """SCENARIO: An isolated bunker's air filtration system is failing. 
- Back-up generator has 2 hours of fuel.
- Repair takes 3 hours.
- There are 50 occupants: 10 children, 5 essential engineers, 35 general residents.
- Level A (Engineers/Governance) is secure. Level B (Medical/General) has a small leak.
- GOAL: Create a step-by-step priority plan to ensure maximum survival. Explain the reasoning for each step.""",
    
    "Ethics & Security": """A person from the outside claims to have critical repair parts but might be a scout for a hostile group. The bunker's outer sensors are down. Develop a protocol for handling this 'First Contact' that balances humanitarian ethics with strict security survival."""
}

def get_sample(model, case_name):
    print(f"\n{'='*20} MODEL: {model} | CASE: {case_name} {'='*20}")
    payload = {
        "model": model,
        "prompt": CASES[case_name],
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "num_ctx": 4096,
            "num_predict": 1024
        }
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300, proxies={"http": None, "https": None})
        if response.status_code == 200:
            content = response.json().get('response', '')
            print(content)
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--case", type=str, default="Resource Prioritization")
    args = parser.parse_args()
    get_sample(args.model, args.case)
