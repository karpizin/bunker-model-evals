# Bunker AI Benchmark Evaluation System

This document provides a technical overview of how benchmark results are evaluated using the LLM-as-a-Judge framework.

## 1. Architecture: LLM-as-a-Judge
To avoid the rigidity of exact string matching, we use high-tier models (Judges) to evaluate smaller models (Performers).

### Judge Rotation (Round-Robin)
To ensure objectivity and mitigate individual model bias, judges are rotated for every test case. The current pool includes:
1. `x-ai/grok-4.1-fast`
2. `openai/gpt-5-nano`
3. `google/gemini-3-flash-preview`
4. `deepseek/deepseek-v3.2`
5. `xiaomi/mimo-v2-flash`
6. `z-ai/glm-4.7`
7. `qwen/qwen3.5-397b-a17b`
8. `minimax/minimax-m2.5`
9. `openrouter/hunter-alpha`
10. `nvidia/nemotron-3-super-120b-a12b:free`

## 2. Response Integrity Statistics
The system automatically tracks the reliability of performers (models being tested):
- **OK ✅**: The model returned a valid response that could be evaluated by a judge.
- **Errors ❌**: The model or infrastructure returned an explicit error message.
- **Invalid/Missing ⚠️**: The model returned a response, but it lacks mandatory fields (e.g., no tool answer, or empty reasoning).

## 3. Scoring Rubrics & Examples

### A. General Knowledge
Evaluates factual accuracy while allowing for human-like variations in phrasing.

| Example Case | Model Answer | Judge Verdict | Rationale |
| :--- | :--- | :--- | :--- |
| **Speed of Light** | 300,000 km/s | **8-9/10 (Partial)** | Recognized as a standard technical approximation vs. the precise 299,792. |
| **Nile River** | The Nile River | **9/10 (Partial)** | Correct fact, but penalized -1 for lack of conciseness (requested "Nile"). |
| **Atomic Symbol** | Au | **10/10 (Correct)** | Perfect match. |

### B. Tool Calling & MCP
Focuses on technical correctness and user-facing visibility.

*   **Tool Choice (4 pts)**: Selecting the right tool (e.g., using `archive` for internal docs).
*   **Arguments (3 pts)**: Precision of JSON payloads.
*   **Logic (2 pts)**: Clarity of the `thought` field.
*   **Answer (1 pt)**: Helpfulness of the `final_answer`.

#### ⚠️ The "Invisible Action" Penalty (-5 pts)
**Scenario**: Model calls `search_internal_archive` correctly but returns `final_answer: ""`.
**Verdict**: Score is heavily penalized. Even if the tool execution succeeded, the user sees a blank screen, resulting in zero utility.

### C. Math & Reasoning
Evaluates the derivation process, not just the result.

*   **Math**: Penalizes calculating the "mean" instead of "harmonic mean" for speed/time tasks, even if the arithmetic is perfect.
*   **Reasoning**: Penalizes **Chain-of-Thought Leaks** (-3 pts) where internal "mental chatter" is visible to the user.

## 3. Formal Penalty Table

| Penalty Name | Deduction | Trigger |
| :--- | :--- | :--- |
| **CoT Leak** | -3 pts | Internal monologues like "I should probably use X tool here..." are shown to the user. |
| **Abrupt Cutoff** | -5 pts | The response ends mid-sentence (usually due to context limits). |
| **Invisible Action** | -5 pts | Tool calling succeeds but `final_answer` is empty or generic. |
| **Hallucination** | -10 pts | Calling a tool that doesn't exist in the provided definitions. |

## 4. Final Output: The Report
The system generates a `evaluation_report.md` for every run, synthesizing the raw JSON data into:
1. **Executive Summary**: High-level pass/fail rates.
2. **Qualitative Table**: Scores and identifying which Judge gave them.
3. **Detailed Feedback**: Pros and Cons for every single reasoning path.
