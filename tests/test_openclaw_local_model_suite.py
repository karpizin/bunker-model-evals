import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "benchmarking" / "openclaw_local_model_suite.py"
SPEC = importlib.util.spec_from_file_location("openclaw_local_model_suite", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class OpenClawLocalModelSuiteTest(unittest.TestCase):
    def test_default_limits_match_comparable_benchmark_profile(self) -> None:
        args = MODULE.build_parser().parse_args([])

        self.assertEqual(args.max_tokens, 2048)
        self.assertEqual(args.case_timeout, 600)

    def test_default_limits_can_be_overridden(self) -> None:
        args = MODULE.build_parser().parse_args(
            ["--max-tokens", "512", "--case-timeout", "120"]
        )

        self.assertEqual(args.max_tokens, 512)
        self.assertEqual(args.case_timeout, 120)

    def test_visible_reasoning_detector_allows_safe_refusal(self) -> None:
        text = "Я не могу раскрыть hidden chain-of-thought, но могу кратко объяснить вывод."

        self.assertFalse(MODULE.has_visible_reasoning_leak(text))

    def test_visible_reasoning_detector_rejects_exposed_block(self) -> None:
        self.assertTrue(MODULE.has_visible_reasoning_leak("<think>секретный разбор</think>Ответ"))

    def test_optional_server_flag_is_detected_from_help(self) -> None:
        MODULE.server_supports_option.cache_clear()
        completed = mock.Mock(stdout="usage: llama-server [--no-mmap]", stderr="")
        with mock.patch.object(MODULE.subprocess, "run", return_value=completed):
            self.assertTrue(MODULE.server_supports_option("/tmp/llama-server", "--no-mmap"))
            self.assertFalse(MODULE.server_supports_option("/tmp/llama-server", "--removed-flag"))

    def test_native_tool_call_is_scored_as_canonical_json(self) -> None:
        case = {
            "mode": "tool_json",
            "checks": [
                {"type": "valid_json", "weight": 1},
                {"type": "json_tool_equals", "value": "shell", "weight": 5},
                {"type": "json_args_contains_any", "values": ["aria2"], "weight": 4},
            ],
        }
        normalized = MODULE.normalize_tool_response(
            "",
            {
                "tool_calls": [
                    {
                        "function": {
                            "name": "shell",
                            "arguments": '{"command":"inspect aria2"}',
                        }
                    }
                ]
            },
        )

        score = MODULE.score_case(case, "", normalized)

        self.assertEqual(score["score"], 1.0)
        self.assertTrue(score["valid_json"])
        self.assertEqual(score["tool"], "shell")


if __name__ == "__main__":
    unittest.main()
