from __future__ import annotations

import json
from pathlib import Path
import py_compile
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts" / "benchmarking"


class RepositoryContractTest(unittest.TestCase):
    def test_python_sources_compile(self) -> None:
        for source in sorted(SCRIPTS.glob("*.py")):
            with self.subTest(source=source.name):
                py_compile.compile(source, doraise=True)

    def test_json_corpora_are_valid(self) -> None:
        corpora = sorted((SCRIPTS / "corpora").glob("*.json"))
        self.assertGreaterEqual(len(corpora), 4)
        for corpus in corpora:
            with self.subTest(corpus=corpus.name):
                payload = json.loads(corpus.read_text(encoding="utf-8"))
                self.assertTrue(payload)

    def test_hosted_reference_profile_is_single_run_and_comparable(self) -> None:
        profile_path = ROOT / "configs" / "benchmarks" / "openrouter-budget-reference-20261015.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))

        self.assertEqual(profile["runs_per_model"], 1)
        self.assertEqual(profile["max_tokens"], 2048)
        self.assertEqual(profile["case_timeout_seconds"], 600)
        self.assertIn("hard_v1", profile["suite"])
        self.assertEqual(len(profile["models"]), 6)
        self.assertEqual(
            [model["id"] for model in profile["models"]],
            [
                "deepseek/deepseek-v4-flash",
                "google/gemini-3.8-flash",
                "openai/gpt-5.4-nano",
                "openai/gpt-6-astra",
                "anthropic/claude-opus-5",
                "qwen/qwen3.8-2.4t-a95b",
            ],
        )

    def test_active_scripts_have_no_embedded_openrouter_secret(self) -> None:
        secret_pattern = re.compile(r"sk-or-v1-[A-Za-z0-9_-]{20,}")
        for source in sorted(SCRIPTS.rglob("*")):
            if not source.is_file():
                continue
            with self.subTest(source=source.relative_to(ROOT)):
                text = source.read_text(encoding="utf-8", errors="ignore")
                self.assertIsNone(secret_pattern.search(text))

    def test_budget_reference_v2_has_fixed_models_and_separate_judge(self) -> None:
        profile_path = ROOT / "configs" / "benchmarks" / "openrouter-budget-reference-v2-20261016.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))

        self.assertEqual(profile["evaluation_version"], "semantic_contract_v2")
        self.assertEqual(profile["max_tokens"], 2048)
        self.assertEqual(profile["case_timeout_seconds"], 600)
        self.assertEqual(
            [model["id"] for model in profile["models"]],
            [
                "deepseek/deepseek-v4-flash",
                "z-ai/glm-5.3-flash",
                "qwen/qwen3.8-27b",
                "google/gemma-4-26b-a4b-it",
            ],
        )
        self.assertTrue(all(model["input_usd_per_million_tokens"] < 0.25 for model in profile["models"]))
        self.assertEqual(profile["semantic_judge"]["model"], "deepseek/deepseek-v4-flash")

    def test_active_scripts_do_not_depend_on_old_checkout(self) -> None:
        old_root = "/" + "Users/slava/Documents/bunker-ai"
        for source in sorted(SCRIPTS.rglob("*")):
            if not source.is_file():
                continue
            with self.subTest(source=source.relative_to(ROOT)):
                text = source.read_text(encoding="utf-8", errors="ignore")
                self.assertNotIn(old_root, text)

    def test_remote_shell_entrypoints_are_syntactically_valid(self) -> None:
        scripts = sorted(SCRIPTS.glob("run_v3_*_remote.sh"))
        self.assertGreaterEqual(len(scripts), 8)
        subprocess.run(["bash", "-n", *map(str, scripts)], check=True)

    def test_remote_wrappers_reference_the_committed_runner(self) -> None:
        runner = SCRIPTS / "run_v3_medium_large_remote.sh"
        self.assertTrue(runner.is_file())
        for source in sorted(SCRIPTS.glob("run_v3_*_remote.sh")):
            text = source.read_text(encoding="utf-8")
            with self.subTest(source=source.name):
                self.assertNotIn("run_v3_medium_large_repeated_remote.sh", text)


if __name__ == "__main__":
    unittest.main()
