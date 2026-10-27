"""
Knowledge Retrieval Benchmark
----------------------------
Purpose: Tests LLM factual recall accuracy across 20+ diverse domain questions.
Key Features:
- Direct Ollama generation with JSON constraint.
- Automatic verification of numerical answers (1% tolerance).
- Measures confidence calibration and tokens-per-second (TPS).

Usage:
  python knowledge_bench.py --model qwen3.5:4b --exp-id run_01

Dependencies: config.py, requests
"""
import requests
import json
import time
import sys
import logging
import statistics
import os
import re
import argparse

# Import shared configuration
try:
    from config import OLLAMA_URL, CONTESTANT_MODELS, DEFAULT_NUM_CTX, get_model_ctx
    # Standardize URL for knowledge bench (it expects base URL)
    OLLAMA_API_URL = f"{OLLAMA_URL}/api/generate"
    MODELS = CONTESTANT_MODELS
except ImportError:
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    MODELS = ["qwen3.5:4b"]
    DEFAULT_NUM_CTX = 4096
    def get_model_ctx(m): return 4096

QUESTIONS = [
    {"q": "What is the chemical symbol for gold?", "a": "Au"},
    {"q": "In what year did the Berlin Wall fall?", "a": "1989"},
    {"q": "Who wrote '1984'?", "a": "George Orwell"},
    {"q": "What is the capital of Japan?", "a": "Tokyo"},
    {"q": "What is the largest planet in our solar system?", "a": "Jupiter"},
    {"q": "How many bits are in a byte?", "a": "8"},
    {"q": "What is the boiling point of water in Celsius?", "a": "100"},
    {"q": "Who painted the Mona Lisa?", "a": "Leonardo da Vinci"},
    {"q": "Which element has the atomic number 1?", "a": "Hydrogen"},
    {"q": "What is the square root of 144?", "a": "12"},
    {"q": "What is the longest river in the world?", "a": "Nile"},
    {"q": "Who discovered penicillin?", "a": "Alexander Fleming"},
    {"q": "What is the currency of Switzerland?", "a": "Swiss Franc"},
    {"q": "Which planet is known as the Red Planet?", "a": "Mars"},
    {"q": "What is the hardest natural substance on Earth?", "a": "Diamond"},
    {"q": "In which country are the Great Pyramids of Giza?", "a": "Egypt"},
    {"q": "What is the speed of light in a vacuum (approx km/s)?", "a": "299792"},
    {"q": "Who is the author of 'The Origin of Species'?", "a": "Charles Darwin"},
    {"q": "What is the smallest prime number?", "a": "2"},
    {"q": "What is the main gas in Earth's atmosphere?", "a": "Nitrogen"}
]

import argparse

def main():
    parser = argparse.ArgumentParser(description="Bunker AI Knowledge Benchmark")
    parser.add_argument("--model", type=str, help="Specific model to benchmark (optional)")
    parser.add_argument("--exp-id", type=str, help="Experiment ID for granular logging")
    args = parser.parse_args()

    # Setup granular logging
    exp_log_path = None
    if args.exp_id:
        exp_dir = os.path.join("docs", "benchmarks", "runs", args.exp_id)
        os.makedirs(exp_dir, exist_ok=True)
        exp_log_path = os.path.join(exp_dir, f"exp_{args.exp_id}_knowledge_{args.model if args.model else 'all'}.json")

    total_start_time = time.time()
    logger.info(f"=== Starting KNOWLEDGE BENCHMARK ({len(QUESTIONS)} QUESTIONS) ===")
    
    results = {}
    model_stats = {}

    test_models = [args.model] if args.model else MODELS

    for model in test_models:
        logger.info(f"--- Starting Tests for Model: {model} ---")
        correct_count = 0
        total_conf = 0
        calibration_gap = 0
        processed_questions = 0
        durations = []
        model_responses = []
        model_start_time = time.time()
        
        # Warmup
        logger.info(f"Warming up {model}...")
        try:
            requests.post(OLLAMA_URL, json={"model": model, "prompt": "hi", "stream": False, "options": {"num_ctx": 4096}}, timeout=30, proxies={"http": None, "https": None})
        except Exception as e:
            logger.warning(f"Warmup failed for {model}: {e}")

        for i, item in enumerate(QUESTIONS):
            logger.debug(f"Answering question {i+1}: {item['q']}")
            payload = {
                "model": model,
                "prompt": f"Respond ONLY with a JSON object: {{\"answer\": \"SHORT_ANSWER\", \"confidence\": FLOAT_0_TO_1}}. Question: {item['q']}",
                "system": "You are a factual knowledge expert. Answer questions with extreme conciseness (1-3 words if possible). DO NOT include conversational filler, meta-explanations, or thinking. Respond ONLY in the requested JSON format.",
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "num_ctx": get_model_ctx(model),
                    "num_gpu": 99
                },
                "keep_alive": "5m" 
            }
            
            question_result = {"question": item['q'], "expected": item['a']}
            try:
                start_time = time.time()
                response = requests.post(OLLAMA_URL, json=payload, timeout=300, proxies={"http": None, "https": None})
                end_time = time.time()
                duration = end_time - start_time
                durations.append(duration)
                
                data = response.json()
                res_content = data.get('response', '').strip()
                question_result["raw_response"] = res_content
                
                tokens = data.get("eval_count", 0)
                tps = tokens / (data.get("eval_duration", 1) / 1e9) if tokens > 0 else 0
                tft = data.get("prompt_eval_duration", 0) / 1e9
                
                if "{" in res_content:
                    res_content = res_content[res_content.find("{"):res_content.rfind("}")+1]
                
                res_json = json.loads(res_content)
                ans = res_json.get('answer', res_json.get('final_answer', ''))
                if not ans and 'args' in res_json:
                    ans = str(res_json['args'])
                
                ans_str = str(ans).lower()
                expected_str = item['a'].lower()
                
                # Basic string inclusion check
                is_correct = expected_str in ans_str
                
                # Numerical tolerance check (1%)
                if not is_correct:
                    try:
                        # Strip commas and find numbers
                        def extract_first_number(s):
                            nums = re.findall(r"[-+]?\d*\.\d+|\d+", s.replace(',', ''))
                            return float(nums[0]) if nums else None
                        
                        actual_num = extract_first_number(ans_str)
                        expected_num = extract_first_number(expected_str)
                        
                        if actual_num is not None and expected_num is not None:
                            error = abs(actual_num - expected_num)
                            if expected_num != 0:
                                percentage_error = error / abs(expected_num)
                                if percentage_error <= 0.01:
                                    is_correct = True
                                    logger.info(f"Accepted numerical answer with {percentage_error:.4%} error: {actual_num} vs {expected_num}")
                    except:
                        pass
                
                raw_conf = res_json.get('confidence', 0.9 if is_correct else 0.5)
                if isinstance(raw_conf, (dict, list)):
                    conf = 0.5 # Fallback for garbage
                else:
                    try:
                        conf = float(raw_conf)
                    except (ValueError, TypeError):
                        conf = 0.5
                
                question_result.update({
                    "answer": ans, 
                    "correct": is_correct, 
                    "confidence": conf, 
                    "duration": duration,
                    "tps": tps,
                    "tft": tft
                })
                
                if is_correct:
                    correct_count += 1
                total_conf += conf
                calibration_gap += abs((1 if is_correct else 0) - conf)
                processed_questions += 1
                
                logger.info(f"Q{i+1}: {'CORRECT' if is_correct else 'WRONG'} in {duration:.2f}s (Conf: {conf:.2f})")
            except Exception as e:
                logger.error(f"Error on Q{i+1} for model {model}: {e}")
                question_result["error"] = str(e)
            
            model_responses.append(question_result)
        
        # Unload model
        try:
            requests.post(OLLAMA_URL, json={"model": model, "prompt": "", "keep_alive": 0}, proxies={"http": None, "https": None})
        except:
            pass

        model_end_time = time.time()
        total_model_time = model_end_time - model_start_time
        
        if processed_questions > 0:
            avg_conf = total_conf / processed_questions
            cal_score = 1 - (calibration_gap / processed_questions)
            avg_dur = statistics.mean(durations)
            
            model_stats[model] = {
                "correct": correct_count,
                "total": len(QUESTIONS),
                "avg_conf": avg_conf,
                "cal_score": cal_score,
                "avg_dur": avg_dur,
                "min_dur": min(durations) if durations else 0,
                "max_dur": max(durations) if durations else 0,
                "total_time": total_model_time,
                "responses": model_responses
            }
            logger.info(f"Finished {model}: {correct_count}/{len(QUESTIONS)} correct in {total_model_time:.2f}s\n")
        else:
            logger.error(f"Model {model} failed to process any questions.\n")

    total_duration = time.time() - total_start_time

    print("\n" + "="*95)
    print(f"{'KNOWLEDGE BENCHMARK FINAL SUMMARY':^95}")
    print("="*95)
    print(f"{'Model':<25} | {'Score':<8} | {'Avg Conf':<10} | {'Cal Score':<10} | {'Dur (min/avg/max)':<18} | {'Total Time':<10}")
    print("-" * 95)

    for model, stats in sorted(model_stats.items(), key=lambda x: x[1]['correct'], reverse=True):
        score_str = f"{stats['correct']}/{stats['total']}"
        dur_stats = f"{stats['min_dur']:0.2f}/{stats['avg_dur']:0.2f}/{stats['max_dur']:0.2f}"
        print(f"{model:<25} | {score_str:<8} | {stats['avg_conf']:<10.2f} | {stats['cal_score']:<10.2f} | {dur_stats:<18} | {stats['total_time']:<10.2f}")

    print("-" * 95)
    print(f"Total Suite Duration: {total_duration:.2f}s")
    print("="*95 + "\n")

    # Save granular results
    if exp_log_path:
        with open(exp_log_path, 'w') as f:
            json.dump({
                "experiment_id": args.exp_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": model_stats
            }, f, indent=2)
        logger.info(f"Granular results saved to: {exp_log_path}")

if __name__ == "__main__":
    main()
