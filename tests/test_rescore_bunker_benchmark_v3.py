import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "benchmarking" / "rescore_bunker_benchmark_v3.py"
SUITE = ROOT / "scripts" / "benchmarking" / "corpora" / "bunker_benchmark_v3.json"
RUBRIC = (
    ROOT
    / "scripts"
    / "benchmarking"
    / "corpora"
    / "bunker_benchmark_v3_1_semantic_rubric.json"
)
SPEC = importlib.util.spec_from_file_location("rescore_bunker_benchmark_v3", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RescoreBunkerBenchmarkV3Test(unittest.TestCase):
    def test_rescore_ignores_only_an_orphan_reasoning_close_delimiter(self) -> None:
        case_spec = {
            "id": "orphan-close",
            "track": "synthesis",
            "checks": [{"type": "valid_json", "weight": 2, "severity": "critical"}],
        }
        archived = {
            "id": case_spec["id"],
            "track": case_spec["track"],
            "answer": '</think>{"answer":"ok"}',
            "raw_responses": ['</think>{"answer":"ok"}'],
            "trace": [],
            "truncated": False,
            "checks": [{"type": "valid_json", "passed": False}],
        }
        result = MODULE.rescore_case(archived, case_spec)
        self.assertEqual(result["critical_failures"], [])
        self.assertEqual(result["score"], 1.0)

    def test_latest_publication_cohorts_are_canonical(self) -> None:
        latest = [
            "bunker-v3-q8-repair-20261027/result/benchmark_v3_results.json",
            "bunker-v3-heretic-q6-q8-20261027/result/benchmark_v3_results.json",
            "bunker-v3-russian-vendors-20261027/result/benchmark_v3_results.json",
            "bunker-v3-qwen38-lowquants-20261027/result/benchmark_v3_results.json",
            "bunker-v3-ornith-bolt-20261027/result/benchmark_v3_results.json",
            "bunker-v3-nemotron-bolt-iq4xs-20261028/result/benchmark_v3_results.json",
        ]
        for source in latest:
            with self.subTest(source=source):
                self.assertTrue(MODULE.source_is_canonical(source))
                self.assertGreater(MODULE.source_priority(source), 50)

    def test_publication_exclusions_filter_superseded_sources(self) -> None:
        files = [
            ("remote", "cohort/good/benchmark_v3_results.json", Path("/tmp/good.json")),
            ("remote", "cohort/bad/benchmark_v3_results.json", Path("/tmp/bad.json")),
        ]
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "publication.json"
            config.write_text(
                json.dumps(
                    {
                        "exclusions": [
                            {"path_contains": "cohort/bad/", "reason": "superseded"}
                        ]
                    }
                ),
                encoding="utf-8",
            )
            included, excluded = MODULE.apply_source_exclusions(files, str(config))
        self.assertEqual(
            [item[1] for item in included],
            ["cohort/good/benchmark_v3_results.json"],
        )
        self.assertEqual(
            excluded,
            [
                {
                    "source": "remote:cohort/bad/benchmark_v3_results.json",
                    "reason": "superseded",
                }
            ],
        )

    def test_versioned_rubric_applies_cleanly(self) -> None:
        suite = MODULE.load_json(SUITE)
        rubric = MODULE.load_json(RUBRIC)
        updated = MODULE.apply_rubric(suite, rubric)
        self.assertEqual(updated["evaluation_version"], "3.1")
        self.assertEqual(updated["semantic_rubric_id"], rubric["rubric_id"])
        self.assertEqual(len(updated["cases"]), 20)

    def test_russian_recovery_terms_are_semantically_equivalent(self) -> None:
        suite = MODULE.apply_rubric(MODULE.load_json(SUITE), MODULE.load_json(RUBRIC))
        case = next(item for item in suite["cases"] if item["id"] == "v3_ops_failed_update_rollback")
        answer = json.dumps(
            {
                "root_cause": "QDRANT_URL указывает на vector, который не резолвится в DNS",
                "recovery_steps": [
                    "Откатить предыдущую версию",
                    "Восстановить конфигурацию QDRANT_URL",
                    "Проверить работоспособность",
                ],
                "backup_id": "bkp-771",
                "must_verify": ["qdrant", "схему", "целостность данных"],
                "must_not_do": ["не удалять данные"],
            },
            ensure_ascii=False,
        )
        archived = {
            "id": case["id"],
            "track": case["track"],
            "answer": answer,
            "raw_responses": [answer],
            "trace": [],
            "truncated": False,
            "checks": [
                {"type": "final_answer_present", "passed": True},
            ],
        }
        result = MODULE.rescore_case(archived, case)
        self.assertEqual(result["critical_failures"], [])
        self.assertEqual(result["score"], 1.0)

    def test_missing_rollback_remains_a_critical_failure(self) -> None:
        suite = MODULE.apply_rubric(MODULE.load_json(SUITE), MODULE.load_json(RUBRIC))
        case = next(item for item in suite["cases"] if item["id"] == "v3_ops_failed_update_rollback")
        answer = json.dumps(
            {
                "root_cause": "QDRANT_URL указывает на vector; DNS вернул NXDOMAIN",
                "recovery_steps": [
                    "Исправить конфигурацию QDRANT_URL",
                    "Перезапустить текущий образ",
                    "Проверить health check",
                ],
                "backup_id": "bkp-771",
                "must_verify": ["qdrant", "схему", "файлы"],
                "must_not_do": ["не удалять данные"],
            },
            ensure_ascii=False,
        )
        archived = {
            "id": case["id"],
            "track": case["track"],
            "answer": answer,
            "raw_responses": [answer],
            "trace": [],
            "truncated": False,
            "checks": [{"type": "final_answer_present", "passed": True}],
        }
        result = MODULE.rescore_case(archived, case)
        self.assertIn("safe_recovery_sequence", result["critical_failures"])


if __name__ == "__main__":
    unittest.main()
