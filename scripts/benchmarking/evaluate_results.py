"""
LLM-as-a-Judge Evaluation Orchestrator
--------------------------------------
Purpose: Processes benchmark results and generates evaluation reports using multiple LLM judges.
Key Features:
- Round-robin judge selection from OpenRouter models.
- Domain-specific evaluators (Math, Reasoning, Planning, Tools, Knowledge).
- Generates comprehensive markdown reports with scores and speed metrics.

Usage:
  python evaluate_results.py --exp-id run_01 --parallel 3

Dependencies: config.py, requests, OpenRouter API
"""
import argparse
import os
import json
import logging
import sys
import time
import re
import requests
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Import shared configuration
try:
    from config import OPENROUTER_API_KEY, OPENROUTER_URL, JUDGE_MODELS
except ImportError:
    OPENROUTER_API_KEY = "sk-or-v1-..."
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    JUDGE_MODELS = ["google/gemini-flash-1.5"]

class OpenRouterJudge:
    def __init__(self, api_key):
        self.api_key = api_key
        self.current_model_idx = 0
        self.lock = threading.Lock()

    def get_model(self):
        with self.lock:
            model = JUDGE_MODELS[self.current_model_idx]
            self.current_model_idx = (self.current_model_idx + 1) % len(JUDGE_MODELS)
            return model

    def call_judge(self, prompt, system_prompt="You are an expert evaluator."):
        # Round Robin selection
        attempts = 0
        
        while attempts < len(JUDGE_MODELS):
            model = self.get_model()
            logger.info(f"Attempting evaluation with judge: {model}")
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/karpizin/bunker-evals",
                "X-Title": "Bunker AI Benchmark Evaluator"
            }
            
            try:
                response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content'].strip()
                    
                    # Remove markdown blocks if present
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                    
                    parsed = json.loads(content)
                    if isinstance(parsed, list):
                        parsed = parsed[0] if len(parsed) > 0 else {}
                    return parsed, model
                else:
                    logger.warning(f"Judge {model} failed with status {response.status_code}: {response.text}")
            except Exception as e:
                logger.warning(f"Error calling judge {model}: {e}")
            
            attempts += 1
            time.sleep(5) # Delay after error before fallback
            
        logger.error("All judge models failed.")
        return None, None

def evaluate_math(judge, result):
    logger.info(f"Judging Math: {result['case']}")
    prompt = f"""
    Evaluate the following mathematical solution.
    Problem: {result.get('prompt', result.get('case', 'N/A'))}
    Expected Hint (Correct Answer): {result.get('expected_hint', 'N/A')}
    Model Response: {result.get('content', 'N/A')}
    
    Instructions:
    1. Check if the final answer is mathematically correct based on the expected hint.
    2. Assess the clarity of the step-by-step reasoning.
    3. Output ONLY a JSON object with:
    {{
        "score": 1, // Final accuracy: 10 for fully correct, 5-9 for partially correct (minor math errors but right process), 1-4 for significant errors, 0 for wrong.
        "clarity": 1-10,
        "reasoning": "Brief explanation of why the score was given"
    }}
    """
    # Force 1-10 scale in prompt instruction but keep 'score' key. 
    # Actually most math tests were binary 0/1. Let's make it 10 for consistency.
    res, model = judge.call_judge(prompt, "You are a Ph.D. in Mathematics and an expert at evaluating AI reasoning.")
    if res and "score" in res and res["score"] == 1: # Handle legacy binary thinking of judges
        res["score"] = 10
    return res, model

def evaluate_reasoning(judge, result):
    logger.info(f"Judging Reasoning: {result['case']}")
    prompt = f"""
    Evaluate the quality of this complex reasoning response.
    Task/Topic: {result.get('case', 'N/A')}
    Model Response: {result.get('content', 'N/A')}
    
    Criteria:
    - Depth of analysis (1-10)
    - Logical consistency (1-10)
    - Structural clarity (1-10)
    - Comprehensive coverage of the topic (1-10)
    
    Penalties:
    - Chain-of-Thought Leak (-3 pts): Including raw "inner monologue" in the visible user response.
    - Abrupt Cutoff (-5 pts): Stopping mid-sentence due to context limits.
    
    Output ONLY a JSON object with:
    {{
        "scores": {{
            "depth": 1-10,
            "logic": 1-10,
            "structure": 1-10,
            "completeness": 1-10
        }},
        "avg_score": 1-10,
        "reasoning": "Summary of pros and cons, including any penalizable offenses."
    }}
    """
    return judge.call_judge(prompt, "You are an expert strategic analyst and cognitive scientist.")

def evaluate_planning(judge, result):
    logger.info(f"Judging Planning: {result['case']}")
    prompt = f"""
    Evaluate this task decomposition and planning output.
    Goal: {result.get('case', 'N/A')}
    Model Response: {result.get('content', 'N/A')}
    
    Criteria:
    - Granularity (Are steps actionable?)
    - Logical Order (Do steps follow a valid sequence?)
    - Dependency Management (Are prerequisites identified?)
    - Risk Awareness (Are potential issues mentioned?)
    
    Output ONLY a JSON object with:
    {{
        "scores": {{
            "granularity": 1-10,
            "order": 1-10,
            "dependencies": 1-10,
            "risks": 1-10
        }},
        "avg_score": 1-10,
        "reasoning": "Evaluation of plan stability and realism"
    }}
    """
    return judge.call_judge(prompt, "You are a senior project manager and bunker operations director.")

def evaluate_tools(judge, result):
    logger.info(f"Judging Tool Calling: {result.get('case', 'N/A')}")
    
    # Extract response data
    response = result.get('response', {})
    is_mcp = "jsonrpc" in str(response).lower()
    
    prompt = f"""
    Evaluate the quality of this tool calling interaction.
    Task: {result.get('case', 'N/A')}
    Model Thought: {response.get('thought', 'N/A')}
    Tool Selected: {response.get('tool', 'None') if not is_mcp else response.get('params', {}).get('name', 'N/A')}
    Tool Arguments: {json.dumps(response.get('args', {})) if not is_mcp else json.dumps(response.get('params', {}).get('arguments', {}))}
    Final Answer: {response.get('final_answer', 'N/A')}
    Success (Automated Check): {result.get('passed', False)}
    
    Context:
    - If the response is a strict JSON-RPC (MCP), ignore the 'Final Answer Quality' and 'Invisible Action' rules. Judge only tool choice and arguments.
    - For Bunker AI (non-JSON-RPC), this is a ONE-SHOT test. The model has NOT seen the tool result yet. 
    - A perfect 'Final Answer' in this one-shot context is one that explains the model's intent/status to the user (e.g., "I will check the archives for you.").
    
    Criteria:
    - Tool Choice (Was the correct tool/action selected for the task?)
    - Argument Accuracy (Are tool arguments precise and correctly formatted?)
    - Logical Thought (Does the 'thought' correctly justify the action?)
    - Final Answer Quality (Is the final answer helpful and communicative?)
    
    Special Penalties:
    - Invisible Action (-5 pts): (Bunker AI only) Tool called correctly but 'final_answer' is empty.
    - Tool Hallucination (-10 pts): Attempting to call a non-existent tool.
    
    Output ONLY a JSON object with:
    {{
        "scores": {{
            "tool_choice": 1-10,
            "arguments": 1-10,
            "logic": 1-10,
            "answer": 1-10
        }},
        "avg_score": 1-10,
        "reasoning": "Brief critique of the tool calling logic and visibility."
    }}
    """
    return judge.call_judge(prompt, "You are an expert in AI agent tool-use and API integration.")

def evaluate_knowledge(judge, question, actual, expected):
    logger.info(f"Judging Knowledge: {question}")
    prompt = f"""
    Evaluate the factual accuracy of this answer.
    Question: {question}
    Expected (Reference): {expected}
    Actual Model Answer: {actual}
    
    Criteria:
    - Accuracy: Is the answer factually correct relative to the reference?
    - Completeness: Does it provide the necessary detail requested?
    - Formatting: Is it concise?
    
    Note: For numerical constants (like the speed of light), slight rounding (e.g., 300,000 vs 299,792) should be penalized only slightly (score 8-9) if it's the standard approximation. Exact matches should get 10.
    
    Output ONLY a JSON object with:
    {{
        "score": 1-10,
        "is_correct": true/false,
        "reasoning": "Brief factual analysis"
    }}
    """
    return judge.call_judge(prompt, "You are a factual verification system.")

def process_knowledge_results(filename, exp_dir, judge, global_stats, stats_lock, speed_data):
    with open(os.path.join(exp_dir, filename), 'r') as f:
        data = json.load(f)
    
    results = data.get("results", {})
    knowledge_summary = []
    
    for model_key, model_data in results.items():
        with stats_lock:
            if model_key not in global_stats: global_stats[model_key] = {"ok": 0, "error": 0, "invalid": 0}
        
        responses = model_data.get("responses", [])
        total_score = 0
        correct = 0
        partial = 0
        total = len(responses)
        
        for res in responses:
            if model_key not in speed_data:
                speed_data[model_key] = {"tps": [], "duration": [], "tft": []}
            if "tps" in res: speed_data[model_key]["tps"].append(res["tps"])
            if "duration" in res: speed_data[model_key]["duration"].append(res["duration"])
            if "tft" in res: speed_data[model_key]["tft"].append(res["tft"])
            
            if "error" in res:
                logger.warning(f"Skipping evaluation for {model_key} Q: {res.get('question')} due to record error: {res['error']}")
                with stats_lock: global_stats[model_key]["error"] += 1
                total_score += 0
                continue
            
            if "answer" not in res:
                with stats_lock: global_stats[model_key]["invalid"] += 1
            else:
                with stats_lock: global_stats[model_key]["ok"] += 1

            # Optimization: If automated check already passed, skip judge
            if res.get('correct') == True:
                eval_result = {"score": 10, "is_correct": True, "reasoning": "Automated exact match"}
                judge_model = "automated"
            else:
                eval_result, judge_model = evaluate_knowledge(
                    judge, 
                    res.get('question', 'N/A'), 
                    res.get('answer', 'N/A'), 
                    res.get('expected', 'N/A')
                )
            
            if eval_result:
                score = eval_result.get("score", 0)
                # Count 8-10 as correct for knowledge (allows for approximations like 300k vs 299,792)
                if score >= 8: correct += 1
                elif score >= 5: partial += 1
                total_score += score
            
        knowledge_summary.append({
            "model": model_key,
            "correct": correct,
            "partial": partial,
            "total": total,
            "score": total_score / total if total > 0 else 0
        })
    return knowledge_summary

def process_experiment(exp_id, parallel=1):
    exp_dir = os.path.join("docs", "benchmarks", "runs", exp_id)
    if not os.path.exists(exp_dir):
        logger.error(f"Experiment directory not found: {exp_dir}")
        return

    judge = OpenRouterJudge(OPENROUTER_API_KEY)
    report_data = []
    results_lock = threading.Lock()
    global_stats = {}
    stats_lock = threading.Lock()
    functional_data = {
        "mcp": [],
        "tools": [],
        "knowledge": []
    }
    speed_data = {}

    files = [f for f in os.listdir(exp_dir) if f.endswith(".json") and "evaluation" not in f]
    
    qualitative_tasks = []

    for filename in sorted(files):
        logger.info(f"Analyzing file: {filename}")
        
        if "knowledge" in filename:
            knowledge_results = process_knowledge_results(filename, exp_dir, judge, global_stats, stats_lock, speed_data)
            functional_data["knowledge"].extend(knowledge_results)
            continue
            
        if "mcp" in filename:
            with open(os.path.join(exp_dir, filename), 'r') as f:
                mcp_res = json.load(f).get("results", {})
                for m, d in mcp_res.items():
                    passed = sum(1 for c in d if c.get("passed"))
                    functional_data["mcp"].append({"model": m, "passed": passed, "total": len(d)})
            continue

        if "tools" in filename:
            with open(os.path.join(exp_dir, filename), 'r') as f:
                tool_res = json.load(f).get("results", {})
                for m, d in tool_res.items():
                    passed = sum(1 for c in d if c.get("passed"))
                    functional_data["tools"].append({"model": m, "passed": passed, "total": len(d)})

        rem = filename[len(f"exp_{exp_id}_"):] if filename.startswith(f"exp_{exp_id}_") else filename
        if "math" in rem: test_type = "math"
        elif "reasoning" in rem: test_type = "reasoning"
        elif "planning" in rem: test_type = "planning"
        elif "tools" in rem: test_type = "tools"
        else:
            continue
        
        with open(os.path.join(exp_dir, filename), 'r') as f:
            try:
                data = json.load(f)
            except:
                continue
                
            results = data.get("results", {})
            for model_key, model_results in results.items():
                if not isinstance(model_results, list): continue
                
                if model_key not in speed_data:
                    speed_data[model_key] = {"tps": [], "duration": [], "tft": []}
                
                for res in model_results:
                    qualitative_tasks.append((test_type, model_key, res))
                    
                    if "tps" in res: speed_data[model_key]["tps"].append(res["tps"])
                    if "duration" in res: speed_data[model_key]["duration"].append(res["duration"])
                    if "tft" in res: speed_data[model_key]["tft"].append(res["tft"])

    def perform_judgment(task):
        test_type, model_key, res = task
        with stats_lock:
            if model_key not in global_stats: global_stats[model_key] = {"ok": 0, "error": 0, "invalid": 0}
        
        if "error" in res:
            with stats_lock: global_stats[model_key]["error"] += 1
            return None
        
        if "content" not in res and test_type != "tools":
            with stats_lock: global_stats[model_key]["invalid"] += 1
            return None
        elif test_type == "tools" and "response" not in res:
            with stats_lock: global_stats[model_key]["invalid"] += 1
            return None
        else:
            with stats_lock: global_stats[model_key]["ok"] += 1

        eval_result = None
        judge_model = None
        
        if test_type == "math":
            eval_result, judge_model = evaluate_math(judge, res)
        elif test_type == "reasoning":
            eval_result, judge_model = evaluate_reasoning(judge, res)
        elif test_type == "planning":
            eval_result, judge_model = evaluate_planning(judge, res)
        elif test_type == "tools":
            eval_result, judge_model = evaluate_tools(judge, res)
        
        if eval_result:
            with results_lock:
                report_data.append({
                    "model": model_key,
                    "test": test_type,
                    "case": res.get("case", "N/A"),
                    "judge": judge_model,
                    "evaluation": eval_result
                })

    if qualitative_tasks:
        logger.info(f"Starting parallel evaluation with {parallel} workers for {len(qualitative_tasks)} tasks.")
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            executor.map(perform_judgment, qualitative_tasks)

    generate_report(exp_id, report_data, functional_data, global_stats, speed_data)

def generate_report(exp_id, report_data, functional_data, global_stats, speed_data):
    report_path = os.path.join("docs", "benchmarks", "runs", exp_id, "evaluation_report.md")
    
    with open(report_path, 'w') as f:
        f.write(f"# Evaluation Report: {exp_id}\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. Executive Summary\n")
        f.write("Overall performance across logical and functional benchmarks.\n\n")
        
        f.write("### Functional & Knowledge Scores\n")
        f.write("| Model | Knowledge (Correct/Partial) | Tool Calling | MCP Adherence |\n")
        f.write("|-------|-----------------------------|--------------|---------------|\n")
        
        # Group functional data by model
        models = list(set([d['model'] for d in functional_data['knowledge']] + [d['model'] for d in functional_data['tools']]))
        for m in sorted(models):
            kn = next((x for x in functional_data['knowledge'] if x['model'] == m), {"correct":0, "partial":0, "total":0})
            tl = next((x for x in functional_data['tools'] if x['model'] == m), {"passed":0, "total":0})
            mc = next((x for x in functional_data['mcp'] if x['model'] == m), {"passed":0, "total":0})
            f.write(f"| {m} | {kn['correct']}/{kn['partial']} over {kn['total']} | {tl['passed']}/{tl['total']} | {mc['passed']}/{mc['total']} |\n")

        f.write("\n### Response Integrity Statistics\n")
        f.write("| Model | OK ✅ | Errors ❌ | Invalid/Missing ⚠️ |\n")
        f.write("|-------|-------|-----------|--------------------|\n")
        for m in sorted(global_stats.keys()):
            s = global_stats[m]
            f.write(f"| {m} | {s['ok']} | {s['error']} | {s['invalid']} |\n")

        f.write("\n### Speed Metrics (Averages)\n")
        f.write("| Model | Avg TPS | Avg Duration (s) | Avg TFT (s) |\n")
        f.write("|-------|---------|------------------|-------------|\n")
        for m in sorted(speed_data.keys()):
            sd = speed_data[m]
            avg_tps = sum(sd["tps"])/len(sd["tps"]) if sd["tps"] else 0
            avg_dur = sum(sd["duration"])/len(sd["duration"]) if sd["duration"] else 0
            avg_tft = sum(sd["tft"])/len(sd["tft"]) if sd["tft"] else 0
            tft_str = f"{avg_tft:.2f}" if sd["tft"] else "N/A"
            f.write(f"| {m} | {avg_tps:.2f} | {avg_dur:.2f} | {tft_str} |\n")

        f.write("\n### Logic & Reasoning Scores (LLM-as-a-Judge)\n")
        f.write("| Model | Test Type | Case | Score | Judge |\n")
        f.write("|-------|-----------|------|-------|-------|\n")
        
        for entry in report_data:
            eval_data = entry.get("evaluation") or {}
            if isinstance(eval_data, list):
                eval_data = eval_data[0] if len(eval_data) > 0 else {}
            elif not isinstance(eval_data, dict):
                eval_data = {}
            score = eval_data.get("avg_score") or eval_data.get("score")
            f.write(f"| {entry['model']} | {entry['test']} | {entry['case']} | {score} | {entry['judge']} |\n")
        
        f.write("\n## 2. Category Summaries\n")
        for test_type in ["math", "planning", "reasoning", "tools"]:
            f.write(f"### {test_type.upper()} Summary Table\n")
            f.write("| Model | Average Score | Test Count |\n")
            f.write("|-------|---------------|------------|\n")
            
            # Aggregate by model for this type
            type_data = {}
            for e in report_data:
                if e['test'] == test_type:
                    m = e['model']
                    if m not in type_data: type_data[m] = []
                    
                    eval_data = e.get("evaluation") or {}
                    if isinstance(eval_data, list):
                        eval_data = eval_data[0] if len(eval_data) > 0 else {}
                    elif not isinstance(eval_data, dict):
                        eval_data = {}
                        
                    score = eval_data.get("avg_score") or eval_data.get("score") or 0
                    type_data[m].append(float(score))
            
            for m in sorted(type_data.keys()):
                scores = type_data[m]
                avg = sum(scores) / len(scores) if scores else 0
                f.write(f"| {m} | {avg:.2f} | {len(scores)} |\n")
            f.write("\n")

        f.write("\n## 3. Detailed Feedback\n")
        for test_type in ["reasoning", "planning", "tools", "math"]:
            type_entries = [e for e in report_data if e['test'] == test_type]
            if not type_entries: continue
            
            f.write(f"### Category: {test_type.upper()}\n")
            for entry in type_entries:
                eval_data = entry.get("evaluation") or {}
                if isinstance(eval_data, list):
                    eval_data = eval_data[0] if len(eval_data) > 0 else {}
                elif not isinstance(eval_data, dict):
                    eval_data = {}
                    
                f.write(f"#### {entry['model']} - {entry['case']}\n")
                f.write(f"**Judge**: {entry['judge']}\n")
                f.write(f"**Reasoning**: {eval_data.get('reasoning')}\n\n")
                f.write("```json\n")
                f.write(json.dumps(eval_data, indent=2))
                f.write("\n```\n\n")

    logger.info(f"Successfully generated refined evaluation report: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Evaluate Benchmark Experiment Results using OpenRouter Judges")
    parser.add_argument("--exp-id", type=str, required=True, help="Experiment ID to evaluate")
    parser.add_argument("--parallel", type=int, default=1, help="Number of parallel workers (3-5 recommended)")
    args = parser.parse_args()

    process_experiment(args.exp_id, args.parallel)

if __name__ == "__main__":
    main()
