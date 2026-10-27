import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "benchmarking" / "rescore_archived_openclaw_runs.py"
SPEC = importlib.util.spec_from_file_location("rescore_archived_openclaw_runs", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ArchivedRescoreTests(unittest.TestCase):
    def test_complete_result_is_rescored_without_model_call(self):
        case = {
            "id": "case-1",
            "mode": "chat",
            "checks": [{"type": "contains_any", "values": ["fixed"], "weight": 1}],
        }
        result = {
            "model": "example/model",
            "cases": [
                {"id": f"case-{index}", "score": 0.0, "response": "fixed"}
                for index in range(1, 29)
            ],
        }
        case_by_id = {
            f"case-{index}": {**case, "id": f"case-{index}"}
            for index in range(1, 29)
        }

        rescored = MODULE.rescore_result(result, case_by_id, "run", ROOT / "source.json")

        self.assertTrue(rescored["complete_hard28"])
        self.assertEqual(rescored["contract_v2_score_pct"], 100.0)
        self.assertEqual(rescored["delta_pct_points"], 100.0)


if __name__ == "__main__":
    unittest.main()
