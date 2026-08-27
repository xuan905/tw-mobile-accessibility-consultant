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
SCRIPT = ROOT / "scripts" / "validate_audit_case.py"
EXAMPLE = ROOT / "examples" / "audit-case.example.json"


class ValidateAuditCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_case = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def write_case(self, document: object) -> Path:
        temp_dir = Path(tempfile.mkdtemp(prefix="audit-case-test-"))
        path = temp_dir / "case.json"
        path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        return path

    def run_validator(self, *paths: Path, output_format: str = "text") -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(SCRIPT), "--format", output_format]
        command.extend(str(path) for path in paths)
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def test_valid_example_passes(self) -> None:
        result = self.run_validator(EXAMPLE)
        self.assertEqual(result.returncode, 0)
        self.assertIn("PASS", result.stdout)

    def test_missing_required_case_field_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        del document["case"]["product"]
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("product", result.stdout)

    def test_invalid_json_fails_with_readable_error(self) -> None:
        path = Path(tempfile.mkdtemp(prefix="audit-case-json-test-")) / "invalid.json"
        path.write_text('{"case":', encoding="utf-8")
        self.addCleanup(lambda: shutil.rmtree(path.parent, ignore_errors=True))
        result = self.run_validator(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid JSON", result.stdout)

    def test_unknown_evidence_reference_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["findings"][0]["evidence_ids"] = ["E-999"]
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown evidence id E-999", result.stdout)

    def test_unknown_flow_reference_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["findings"][0]["flow_ids"] = ["FLOW-99"]
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown flow id FLOW-99", result.stdout)

    def test_summary_mismatch_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["summary"]["fail"] = 0
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("summary.fail", result.stdout)

    def test_json_output_is_machine_readable(self) -> None:
        result = self.run_validator(EXAMPLE, output_format="json")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload[0]["valid"], True)
        self.assertEqual(payload[0]["file"], str(EXAMPLE))

    def test_multiple_files_return_failure_when_one_is_invalid(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["case"]["version"] = ""
        invalid_path = self.write_case(document)
        result = self.run_validator(EXAMPLE, invalid_path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count("PASS"), 1)
        self.assertEqual(result.stdout.count("FAIL"), 1)

    def test_empty_schema_version_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["schema_version"] = ""
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("schema_version", result.stdout)

    def test_invalid_status_enum_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["findings"][0]["status"] = "unknown"
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown", result.stdout)

    def test_invalid_check_id_format_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["findings"][0]["check_id"] = "AA-0"
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("check_id", result.stdout)

    def test_invalid_evidence_id_format_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["evidence"][0]["evidence_id"] = "evidence-one"
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence_id", result.stdout)

    def test_additional_top_level_property_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["unexpected"] = True
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected", result.stdout)

    def test_invalid_summary_total_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["summary"]["total"] = 41
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("summary.total", result.stdout)

    def test_invalid_datetime_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["metadata"]["created_at"] = "not-a-datetime"
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("created_at", result.stdout)

    def test_null_case_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["case"] = None
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("case", result.stdout)

    def test_empty_flows_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["case"]["flows"] = []
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("flows", result.stdout)

    def test_negative_summary_count_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["summary"]["fail"] = -1
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("summary.fail", result.stdout)

    def test_unknown_environment_reference_fails(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["findings"][0]["environment_ids"] = ["ENV-999"]
        result = self.run_validator(self.write_case(document))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown environment id ENV-999", result.stdout)


if __name__ == "__main__":
    unittest.main()
