from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "package_report.py"


class PackageReportTests(unittest.TestCase):
    def test_html_output_preserves_markdown_table(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / "report.md"
            output = folder / "report.html"
            source.write_text("# 測試報告\n\n| 狀態 | 數量 |\n|---|---:|\n| 通過 | 1 |\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--html", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            html = output.read_text(encoding="utf-8")
            self.assertIn("lang=\"zh-Hant\"", html)
            self.assertIn("<table>", html)
            self.assertIn("測試報告", html)

    def test_missing_output_argument_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "report.md"
            source.write_text("# Report", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("--html and/or --pdf", result.stderr)


if __name__ == "__main__":
    unittest.main()
