from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_audit_report.py"
EXAMPLE = ROOT / "examples" / "audit-case.example.json"


class GenerateAuditReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_case = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def make_case(self, document: object) -> tuple[Path, Path]:
        directory = Path(tempfile.mkdtemp(prefix="report-generator-test-"))
        case_path = directory / "case.json"
        report_path = directory / "report.md"
        case_path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(lambda: shutil.rmtree(directory, ignore_errors=True))
        return case_path, report_path

    def run_generator(self, case_path: Path, report_path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(case_path), "--output", str(report_path), *extra],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_example_generates_report_with_all_aa_rows(self) -> None:
        case_path, report_path = self.make_case(self.valid_case)
        result = self.run_generator(case_path, report_path)
        self.assertEqual(result.returncode, 0)
        report = report_path.read_text(encoding="utf-8")
        checklist_section = report.split("## 4. 逐項檢核結果", 1)[1].split("## 5. 平台測試紀錄", 1)[0]
        aa_rows = re.findall(r"^\| AA-\d{2} \|", checklist_section, flags=re.MULTILINE)
        self.assertEqual(len(aa_rows), 42)
        self.assertIn("## 1. 執行摘要", report)
        self.assertIn("## 3. 重大缺失與優先順序", report)
        self.assertIn("AA-01", report)
        self.assertIn("talkback", report)

    def test_rule_violations_are_included_in_report(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["findings"][0]["remediation"] = ""
        case_path, report_path = self.make_case(document)
        result = self.run_generator(case_path, report_path, "--allow-invalid")
        self.assertEqual(result.returncode, 0)
        report = report_path.read_text(encoding="utf-8")
        self.assertIn("規則引擎警告", report)
        self.assertIn("R-FAIL-REMEDIATION", report)

    def test_invalid_case_is_rejected_by_default(self) -> None:
        document = copy.deepcopy(self.valid_case)
        del document["case"]["product"]
        case_path, report_path = self.make_case(document)
        result = self.run_generator(case_path, report_path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("failed validation", result.stderr)
        self.assertFalse(report_path.exists())

    def test_allow_invalid_creates_draft_report(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["case"]["product"] = ""
        case_path, report_path = self.make_case(document)
        result = self.run_generator(case_path, report_path, "--allow-invalid")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(report_path.exists())

    def test_report_escapes_table_pipes(self) -> None:
        document = copy.deepcopy(self.valid_case)
        document["findings"][0]["observation"] = "文字|錯誤"
        case_path, report_path = self.make_case(document)
        result = self.run_generator(case_path, report_path)
        self.assertEqual(result.returncode, 0)
        report = report_path.read_text(encoding="utf-8")
        self.assertIn("文字\\|錯誤", report)


if __name__ == "__main__":
    unittest.main()
