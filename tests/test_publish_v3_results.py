from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "benchmarking" / "publish_v3_results.py"
SPEC = importlib.util.spec_from_file_location("publish_v3_results", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PublishV3ResultsTest(unittest.TestCase):
    def test_readme_uses_manifest_publication_date(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            MODULE.write_readme(
                path,
                {
                    "publication_id": "test-publication",
                    "published_at": "2031-04-05T06:07:08+03:00",
                },
                [],
            )
            self.assertTrue(
                path.read_text(encoding="utf-8").startswith(
                    "# Bunker Benchmark v3 — public result bundle (2031-04-05)"
                )
            )

    def test_sanitizes_host_identity_without_changing_public_examples(self) -> None:
        private_address = ".".join(("192", "168", "1", "20"))
        benchmark_home = "/".join(("", "home", "bunker" + "ai", "bunker-data"))
        value = (
            f"{benchmark_home}/models/example.gguf "
            f"from {private_address}; public example 192.0.2.20"
        )
        sanitized = MODULE.sanitize_string(value)
        self.assertIn("<bunker-data>/models/example.gguf", sanitized)
        self.assertNotIn(private_address, sanitized)
        self.assertIn("192.0.2.20", sanitized)

    def test_summary_reports_stability_and_effective_throughput(self) -> None:
        cases = [
            {"id": f"case-{index}", "latency_s": 2, "usage": {"completion_tokens": 10}}
            for index in range(20)
        ]
        payload = {
            "runs": [
                {
                    "model": "example",
                    "cases": cases,
                    "summary": {"capability_mean_pct": score, "critical_failures": 0, "eligible": True},
                }
                for score in (80, 90)
            ]
        }
        summary = MODULE.summarize("cohort/result.json", payload, 20)
        self.assertEqual(summary["complete_runs"], 2)
        self.assertEqual(summary["v3_mean_pct"], 85)
        self.assertEqual(summary["eligible_runs"], 2)
        self.assertEqual(summary["effective_completion_tps"], 5)


if __name__ == "__main__":
    unittest.main()
