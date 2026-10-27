import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "benchmarking" / "openclaw_hosted_model_suite.py"
SPEC = importlib.util.spec_from_file_location("openclaw_hosted_model_suite", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class HostedModelSuiteTests(unittest.TestCase):
    def test_defaults_use_budget_reference(self):
        args = MODULE.build_parser().parse_args([])
        self.assertEqual(args.config, str(MODULE.DEFAULT_CONFIG))
        self.assertEqual(args.api_key_env, "OPENROUTER_API_KEY")
        self.assertFalse(args.retry_errors)
        self.assertFalse(args.retry_judge_errors)
        self.assertFalse(args.rejudge_all)

    def test_existing_results_can_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.json"
            path.write_text(json.dumps({"results": [{"model": "example/model", "cases": []}]}))
            self.assertEqual(MODULE.load_existing(path)[0]["model"], "example/model")

    def test_missing_results_are_empty(self):
        self.assertEqual(MODULE.load_existing(Path("/definitely/missing/results.json")), [])

    def test_evaluation_profile_replaces_aliases_and_case_checks(self):
        suite = {
            "cases": [
                {"id": "kept", "checks": [{"type": "no_thought_leak"}]},
                {"id": "replaced", "checks": [{"type": "contains_any", "values": ["old"]}]},
            ]
        }
        profile = {
            "evaluation_version": "v2",
            "check_type_aliases": {"no_thought_leak": "no_visible_reasoning_leak"},
            "case_overrides": {
                "replaced": {"checks": [{"type": "contains_any", "values": ["new"]}]}
            },
        }

        evaluated = MODULE.apply_evaluation_profile(suite, profile)

        self.assertEqual(evaluated["evaluation_version"], "v2")
        self.assertEqual(evaluated["cases"][0]["checks"][0]["type"], "no_visible_reasoning_leak")
        self.assertEqual(evaluated["cases"][1]["checks"][0]["values"], ["new"])
        self.assertEqual(suite["cases"][0]["checks"][0]["type"], "no_thought_leak")

    def test_semantic_judge_parses_score_and_usage(self):
        response = {
            "model": "judge/returned",
            "choices": [{"message": {"content": '{"score": 91, "reason": "Correct."}'}}],
            "usage": {"prompt_tokens": 42, "completion_tokens": 9},
        }
        with patch.object(MODULE, "_request_json", return_value=(response, 0.25)):
            result = MODULE.judge_semantic_quality(
                "https://example.invalid",
                "secret",
                {"model": "judge/requested"},
                {"prompt": "Task", "mode": "chat"},
                "Answer",
                60,
                0,
            )

        self.assertEqual(result["semantic_score"], 0.91)
        self.assertEqual(result["semantic_judge_returned_model"], "judge/returned")
        self.assertEqual(result["semantic_judge_prompt_tokens"], 42)


if __name__ == "__main__":
    unittest.main()
