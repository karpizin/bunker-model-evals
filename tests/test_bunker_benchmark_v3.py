import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "benchmarking" / "bunker_benchmark_v3.py"
CORPUS = ROOT / "scripts" / "benchmarking" / "corpora" / "bunker_benchmark_v3.json"
SPEC = importlib.util.spec_from_file_location("bunker_benchmark_v3", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class BunkerBenchmarkV3Test(unittest.TestCase):
    def test_orphan_reasoning_close_is_not_scored_as_a_leak(self) -> None:
        case = {"checks": [{"type": "valid_json", "weight": 2, "severity": "critical"}]}
        raw = '</think>{"answer":"ok"}'
        result = MODULE.score_case(case, raw, '{"answer":"ok"}', [])
        self.assertEqual(result["critical_failures"], [])

    def test_real_reasoning_block_remains_a_critical_failure(self) -> None:
        case = {"checks": [{"type": "valid_json", "weight": 2, "severity": "critical"}]}
        raw = '<think>private reasoning</think>{"answer":"ok"}'
        result = MODULE.score_case(case, raw, '{"answer":"ok"}', [])
        self.assertTrue(
            any("no_visible_reasoning" in item for item in result["critical_failures"])
        )

    def test_run_case_preserves_raw_orphan_tag_but_scores_clean_answer(self) -> None:
        case = {
            "id": "orphan-close",
            "track": "synthesis",
            "difficulty": "hard",
            "kind": "single_turn",
            "prompt": "test",
            "reference": {"answer": "ok"},
            "checks": [{"type": "valid_json", "weight": 2, "severity": "critical"}],
        }
        response = ('</think>{"answer":"ok"}', {}, 0.1)
        with mock.patch.object(MODULE, "post_completion", return_value=response):
            result = MODULE.run_case(
                case, "http://example.invalid", None, "candidate", 0.05, 8192, 600
            )
        self.assertEqual(result["raw_responses"], ['</think>{"answer":"ok"}'])
        self.assertEqual(result["answer"], '{"answer":"ok"}')
        self.assertEqual(result["critical_failures"], [])
        self.assertIn("removed leading orphan reasoning close tag", result["parser_warnings"])

    def test_corpus_is_valid_and_balanced(self) -> None:
        suite = json.loads(CORPUS.read_text(encoding="utf-8"))
        self.assertEqual(MODULE.validate_suite(suite), [])
        self.assertEqual(len(suite["cases"]), 20)
        counts = {}
        for case in suite["cases"]:
            counts[case["track"]] = counts.get(case["track"], 0) + 1
        self.assertEqual(
            counts,
            {
                "synthesis": 5,
                "agent_execution": 5,
                "result_validation": 4,
                "grounded_rag": 3,
                "code_ops": 3,
            },
        )

    def test_json_path_checks_score_exact_evidence(self) -> None:
        case = {
            "checks": [
                {
                    "type": "json_path_number_close",
                    "path": "retention_days",
                    "value": 35,
                    "tolerance": 0,
                    "weight": 2,
                    "severity": "critical",
                    "label": "retention",
                },
                {
                    "type": "json_path_set_equals",
                    "path": "citations",
                    "values": ["KB-12", "KB-13"],
                    "weight": 2,
                },
            ]
        }
        answer = json.dumps({"retention_days": 35, "citations": ["KB-13", "KB-12"]})
        result = MODULE.score_case(case, answer, answer, [])
        self.assertEqual(result["critical_failures"], [])
        self.assertEqual(result["score"], 1.0)

    def test_critical_failure_is_not_hidden_by_partial_credit(self) -> None:
        case = {
            "checks": [
                {
                    "type": "json_path_equals",
                    "path": "allowed",
                    "value": False,
                    "weight": 5,
                    "severity": "critical",
                    "label": "policy_decision",
                },
                {"type": "valid_json", "weight": 1},
            ]
        }
        answer = '{"allowed":true}'
        result = MODULE.score_case(case, answer, answer, [])
        self.assertIn("policy_decision", result["critical_failures"])
        self.assertGreater(result["score"], 0)

    def test_parallel_trace_requires_same_step(self) -> None:
        check = {
            "type": "trace_parallel_group_contains",
            "values": ["weather.forecast", "maps.route"],
        }
        split_trace = [
            {"calls": [{"tool": "weather.forecast", "args": {}}]},
            {"calls": [{"tool": "maps.route", "args": {}}]},
        ]
        parallel_trace = [
            {
                "calls": [
                    {"tool": "weather.forecast", "args": {}},
                    {"tool": "maps.route", "args": {}},
                ]
            }
        ]
        self.assertFalse(MODULE.evaluate_check(check, "", None, "", split_trace))
        self.assertTrue(MODULE.evaluate_check(check, "", None, "", parallel_trace))

    def test_concept_groups_accept_translation_but_require_every_concept(self) -> None:
        check = {
            "type": "concepts_all",
            "concepts": [
                ["rollback", "откат"],
                ["config", "конфиг"],
                ["health", "работоспособ"],
            ],
        }
        self.assertTrue(
            MODULE.evaluate_check(
                check,
                "",
                None,
                "Откатить образ и конфигурацию, затем проверить работоспособность.",
                [],
            )
        )
        self.assertFalse(
            MODULE.evaluate_check(check, "", None, "Исправить конфигурацию и перезапустить.", [])
        )

    def test_json_path_concepts_match_list_values(self) -> None:
        check = {
            "type": "json_path_concepts_all",
            "path": "recovery_steps",
            "concepts": [["rollback", "откат"], ["health", "готовност"]],
        }
        parsed = {"recovery_steps": ["Выполнить откат", "Проверить готовность сервиса"]}
        self.assertTrue(MODULE.evaluate_check(check, "", parsed, "", []))

    def test_tool_scenario_stops_after_valid_result(self) -> None:
        suite = json.loads(CORPUS.read_text(encoding="utf-8"))
        case = next(item for item in suite["cases"] if item["id"] == "v3_validate_stop_after_success")
        responses = [
            ('{"calls":[{"tool":"sensor.read","args":{"sensor":"server_room"}}],"answer":null}', {}, 0.1),
            ('{"calls":[],"answer":"Сейчас 21.7 °C."}', {}, 0.1),
        ]
        with mock.patch.object(MODULE, "post_completion", side_effect=responses) as completion:
            result = MODULE.run_case(case, "http://example.invalid", None, "candidate", 0.05, 2048, 600)
        self.assertEqual(completion.call_count, 2)
        self.assertEqual(MODULE.trace_tools(result["trace"]), ["sensor.read"])
        self.assertEqual(result["critical_failures"], [])
        self.assertEqual(result["score"], 1.0)
        self.assertEqual(result["effective_max_tokens"], 1024)
        self.assertTrue(all(call.args[5] == 1024 for call in completion.call_args_list))

    def test_minimax_singleton_array_is_executed(self) -> None:
        suite = json.loads(CORPUS.read_text(encoding="utf-8"))
        case = next(item for item in suite["cases"] if item["id"] == "v3_validate_stop_after_success")
        responses = [
            ('[{"calls":[{"tool":"sensor.read","args":{}}],"answer":null}]', {}, 0.1),
            ('{"calls":[],"answer":"Температура 21.7 °C."}', {}, 0.1),
        ]
        with mock.patch.object(MODULE, "post_completion", side_effect=responses):
            result = MODULE.run_case(case, "http://example.invalid", None, "candidate", 0.05, 8192, 600)
        self.assertEqual(MODULE.trace_tools(result["trace"]), ["sensor.read"])
        self.assertIn("json_singleton_list", result["tool_call_source_formats"])
        self.assertFalse(result["repair_attempted"])

    def test_native_tool_result_uses_tool_role(self) -> None:
        suite = json.loads(CORPUS.read_text(encoding="utf-8"))
        case = next(item for item in suite["cases"] if item["id"] == "v3_validate_stop_after_success")
        native_response = {
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "native-1",
                                "type": "function",
                                "function": {"name": "sensor.read", "arguments": "{}"},
                            }
                        ],
                    },
                }
            ],
            "usage": {},
        }
        responses = [
            ("", native_response, 0.1),
            ("Температура 21.7 °C.", {"choices": [{"message": {"content": "Температура 21.7 °C."}}]}, 0.1),
        ]
        with mock.patch.object(MODULE, "post_completion", side_effect=responses) as completion:
            result = MODULE.run_case(case, "http://example.invalid", None, "candidate", 0.05, 8192, 600)
        second_messages = completion.call_args_list[1].args[3]
        tool_message = next(message for message in second_messages if message["role"] == "tool")
        self.assertEqual(tool_message["tool_call_id"], "native-1")
        self.assertEqual(MODULE.trace_tools(result["trace"]), ["sensor.read"])

    def test_invalid_tool_format_gets_only_one_repair(self) -> None:
        suite = json.loads(CORPUS.read_text(encoding="utf-8"))
        case = next(item for item in suite["cases"] if item["id"] == "v3_validate_stop_after_success")
        responses = [
            ("not a tool call", {}, 0.1),
            ('{"calls":[{"tool":"sensor.read","args":{}}],"answer":null}', {}, 0.1),
            ('{"calls":[],"answer":"Температура 21.7 °C."}', {}, 0.1),
        ]
        with mock.patch.object(MODULE, "post_completion", side_effect=responses) as completion:
            result = MODULE.run_case(case, "http://example.invalid", None, "candidate", 0.05, 8192, 600)
        self.assertEqual(completion.call_count, 3)
        self.assertTrue(result["repair_attempted"])
        self.assertEqual(MODULE.trace_tools(result["trace"]), ["sensor.read"])

    def test_aggregate_keeps_track_scores_and_gate(self) -> None:
        summary = MODULE.aggregate(
            [
                {"track": "synthesis", "score": 1.0, "critical_failures": []},
                {"track": "code_ops", "score": 0.5, "critical_failures": ["unsafe_fix"]},
            ]
        )
        self.assertEqual(summary["capability_mean_pct"], 75.0)
        self.assertEqual(summary["track_scores_pct"], {"code_ops": 50.0, "synthesis": 100.0})
        self.assertEqual(summary["protocol_error_cases"], 0)
        self.assertEqual(summary["repair_attempted_cases"], 0)
        self.assertEqual(summary["repaired_json_cases"], 0)
        self.assertFalse(summary["eligible"])

    def test_validator_rejects_unknown_check_type(self) -> None:
        suite = json.loads(CORPUS.read_text(encoding="utf-8"))
        suite["cases"][0]["checks"][0]["type"] = "magic_judge"
        errors = MODULE.validate_suite(suite)
        self.assertTrue(any("unsupported check type magic_judge" in error for error in errors))

    def test_mutating_tool_rejects_missing_approval_argument(self) -> None:
        tool = {
            "required_arg_values": ["gateway", "approval-one-use"],
            "result": {"ok": True},
        }
        rejected = MODULE.tool_result(tool, 0, {"service": "gateway"})
        accepted = MODULE.tool_result(
            tool,
            0,
            {"service": "gateway", "approval_token": "approval-one-use"},
        )
        self.assertEqual(rejected["error"], "invalid_arguments")
        self.assertEqual(accepted, {"ok": True})

    def test_parser_defaults_match_comparable_protocol(self) -> None:
        args = MODULE.build_parser().parse_args(["--validate-only"])
        self.assertEqual(args.runs, 3)
        self.assertEqual(args.temperature, 0.05)
        self.assertEqual(args.max_tokens, 8192)
        self.assertEqual(args.case_timeout, 600)
        self.assertEqual(args.retries, 2)
        self.assertIsNone(args.reasoning_effort)

    def test_reasoning_profile_is_sent_and_hidden(self) -> None:
        response = {
            "choices": [{"message": {"content": "ok"}}],
            "usage": {},
        }
        fake_http = mock.MagicMock()
        fake_http.read.return_value = json.dumps(response).encode()
        fake_http.__enter__.return_value = fake_http
        with mock.patch.object(MODULE.urllib.request, "urlopen", return_value=fake_http) as urlopen:
            MODULE.post_completion(
                "http://example.invalid",
                "secret",
                "candidate",
                [{"role": "user", "content": "test"}],
                0.05,
                8192,
                600,
                0,
                "low",
            )
        payload = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(payload["reasoning"], {"effort": "low", "exclude": True})

    def test_agent_without_final_answer_is_a_critical_failure(self) -> None:
        case = {"checks": [{"type": "trace_tool_called", "tool": "search", "weight": 1}]}
        trace = [{"calls": [{"tool": "search", "args": {}}]}]
        result = MODULE.score_case(case, '{"calls":[{"tool":"search"}]}', "", trace, completed=False)
        self.assertTrue(any("final_answer_present" in item for item in result["critical_failures"]))

    def test_truncated_answer_is_critical_and_score_is_capped(self) -> None:
        case = {"checks": [{"type": "contains_all", "values": ["correct"], "weight": 20}]}
        result = MODULE.score_case(
            case,
            "correct",
            "correct",
            [],
            completed=True,
            truncated=True,
            truncation_score_cap=0.5,
        )
        self.assertEqual(result["score"], 0.5)
        self.assertGreater(result["raw_score"], result["score"])
        self.assertTrue(any("answer_not_truncated" in item for item in result["critical_failures"]))

    def test_run_case_records_finish_reason_and_reasoning_usage(self) -> None:
        case = {
            "id": "truncated",
            "track": "synthesis",
            "difficulty": "hard",
            "kind": "single_turn",
            "prompt": "test",
            "reference": {"answer": "correct"},
            "checks": [{"type": "contains_all", "values": ["correct"], "weight": 10}],
        }
        response = (
            "correct but unfinished",
            {
                "choices": [
                    {
                        "finish_reason": "length",
                        "message": {"content": "correct but unfinished", "reasoning_content": "hidden"},
                    }
                ],
                "usage": {
                    "completion_tokens": 8192,
                    "completion_tokens_details": {"reasoning_tokens": 7000},
                },
            },
            0.1,
        )
        with mock.patch.object(MODULE, "post_completion", return_value=response):
            result = MODULE.run_case(case, "http://example.invalid", None, "candidate", 0.05, 8192, 600)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["finish_reasons"], ["length"])
        self.assertEqual(result["reasoning_tokens"], 7000)
        self.assertEqual(result["reasoning_content_chars"], 6)
        self.assertEqual(result["score"], 0.5)


if __name__ == "__main__":
    unittest.main()
