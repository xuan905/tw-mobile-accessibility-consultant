from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_audit_rules.py"
EXAMPLE = ROOT / "examples" / "audit-case.example.json"


class EvaluateAuditRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_case = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def write_json(self, value: object) -> Path:
        directory = Path(tempfile.mkdtemp(prefix="rule-engine-test-"))
        path = directory / "case.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(lambda: shutil.rmtree(directory, ignore_errors=True))
        return path

    def run_engine(self, path: Path, output_format: str = "text") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--format", output_format],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_example_has_no_rule_violations(self) -> None:
        result = self.run_engine(EXAMPLE)
        self.assertEqual(result.returncode, 0)
        self.assertIn("PASS", result.stdout)

    def test_fail_finding_without_evidence_is_rejected(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["findings"][0]["evidence_ids"] = []
        result = self.run_engine(self.write_json(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("R-FINDING-EVIDENCE", result.stdout)

    def test_fail_finding_without_remediation_is_rejected(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["findings"][0]["remediation"] = ""
        result = self.run_engine(self.write_json(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("R-FAIL-REMEDIATION", result.stdout)

    def test_pending_case_cannot_claim_pass(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["summary"]["overall_conclusion"] = "pass"
        result = self.run_engine(self.write_json(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("R-INCOMPLETE-SUMMARY", result.stdout)

    def test_json_output_is_machine_readable(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["findings"][0]["next_action"] = ""
        result = self.run_engine(self.write_json(document), output_format="json")
        self.assertNotEqual(result.returncode, 0)
        violations = json.loads(result.stdout)
        self.assertEqual(violations[0]["rule_id"], "R-FAIL-NEXT-ACTION")
        self.assertIn("path", violations[0])


if __name__ == "__main__":
    unittest.main()
