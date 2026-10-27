from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "public_repo_audit.py"
SPEC = importlib.util.spec_from_file_location("public_repo_audit", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class PublicRepositoryAuditTest(unittest.TestCase):
    def audit_text(self, relative: str, content: bytes):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            return AUDIT.audit_paths(root, [Path(relative)])

    def test_rejects_secret_signature(self) -> None:
        findings = self.audit_text("config.txt", b"token=sk-or-v1-" + b"a" * 32)
        self.assertIn("openrouter-key", {finding.rule for finding in findings})

    def test_rejects_machine_identity_and_private_network(self) -> None:
        findings = self.audit_text(
            "report.md",
            b"/" + b"Users/example/models and host " + b"192.168." + b"1.20",
        )
        rules = {finding.rule for finding in findings}
        self.assertIn("personal-macos-path", rules)
        self.assertIn("private-network-address", rules)

    def test_allows_loopback_and_documentation_network(self) -> None:
        findings = self.audit_text(
            "example.md",
            b"http://127.0.0.1:8080 and ssh benchmark@192.0.2.20",
        )
        self.assertEqual(findings, [])

    def test_rejects_model_weights(self) -> None:
        findings = self.audit_text("models/example.gguf", b"placeholder")
        self.assertIn("forbidden-artifact", {finding.rule for finding in findings})


if __name__ == "__main__":
    unittest.main()
