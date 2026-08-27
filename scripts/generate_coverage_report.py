#!/usr/bin/env python3
"""Run the test suite and generate coverage artifacts plus a Markdown summary."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path = ROOT, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=capture, check=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run tests and generate coverage artifacts.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "coverage-report")
    parser.add_argument("--source", nargs="+", default=["scripts", "src"])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    os.environ["COVERAGE_FILE"] = str(output_dir / ".coverage")
    data_file = output_dir / "coverage.json"
    xml_file = output_dir / "coverage.xml"
    html_dir = output_dir / "html"
    markdown_file = output_dir / "coverage.md"

    run([sys.executable, "-m", "coverage", "erase"])
    test_run = run([sys.executable, "-m", "coverage", "run", "--parallel-mode", "--source", ",".join(args.source), "-m", "unittest", "discover", "-s", "tests", "-v"])
    sys.stdout.write(test_run.stdout or "")
    sys.stderr.write(test_run.stderr or "")
    if test_run.returncode != 0:
        return test_run.returncode

    smoke_commands = [
        [sys.executable, "-m", "coverage", "run", "--parallel-mode", "--source", ",".join(args.source), "scripts/validate_audit_case.py", "examples/audit-case.example.json"],
        [sys.executable, "-m", "coverage", "run", "--parallel-mode", "--source", ",".join(args.source), "scripts/evaluate_audit_rules.py", "examples/audit-case.example.json"],
        [sys.executable, "-m", "coverage", "run", "--parallel-mode", "--source", ",".join(args.source), "scripts/generate_audit_report.py", "examples/audit-case.example.json", "--output", str(output_dir / "smoke-report.md")],
        [sys.executable, "-m", "coverage", "run", "--parallel-mode", "--source", ",".join(args.source), "scripts/package_report.py", str(output_dir / "smoke-report.md"), "--html", str(output_dir / "smoke-report.html")],
    ]
    for command in smoke_commands:
        smoke_run = run(command, capture=True)
        sys.stdout.write(smoke_run.stdout)
        sys.stderr.write(smoke_run.stderr)
        if smoke_run.returncode != 0:
            return smoke_run.returncode

    combined = run([sys.executable, "-m", "coverage", "combine", str(output_dir)], capture=True)
    if combined.returncode != 0:
        sys.stderr.write(combined.stderr)
        return combined.returncode

    report_run = run([sys.executable, "-m", "coverage", "report", "-m"], capture=True)
    sys.stdout.write(report_run.stdout)
    sys.stderr.write(report_run.stderr)
    if report_run.returncode != 0:
        return report_run.returncode

    for command in (
        [sys.executable, "-m", "coverage", "json", "-o", str(data_file)],
        [sys.executable, "-m", "coverage", "xml", "-o", str(xml_file)],
        [sys.executable, "-m", "coverage", "html", "-d", str(html_dir)],
    ):
        generated = run(command, capture=True)
        if generated.returncode != 0:
            sys.stderr.write(generated.stderr)
            return generated.returncode

    coverage_data = json.loads(data_file.read_text(encoding="utf-8"))
    totals = coverage_data["totals"]
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# v2.0 自動化測試覆蓋率報告",
        "",
        f"**產出時間：** {generated_at}",
        f"**測試結果：** {'通過' if test_run.returncode == 0 else '失敗'}",
        f"**Coverage.py：** {coverage_data.get('meta', {}).get('version', 'unknown')}",
        "",
        "## 總覽",
        "",
        "| 指標 | 數值 |",
        "|---|---:|",
        f"| Statements | {totals['num_statements']} |",
        f"| Missed | {totals['missing_lines']} |",
        f"| Branches | {totals.get('num_branches', 0)} |",
        f"| Partial branches | {totals.get('num_partial_branches', 0)} |",
        f"| **總覆蓋率** | **{totals['percent_covered']:.2f}%** |",
        "",
        "## 檔案明細",
        "",
        "| 檔案 | Statements | Missed | Branches | 覆蓋率 |",
        "|---|---:|---:|---:|---:|",
    ]
    for filename, payload in sorted(coverage_data["files"].items()):
        summary = payload["summary"]
        lines.append(
            f"| `{filename}` | {summary['num_statements']} | {summary['missing_lines']} | {summary.get('num_branches', 0)} | {summary['percent_covered']:.2f}% |"
        )
    lines.extend([
        "",
        "## 產物",
        "",
        f"- XML：`{xml_file}`，供 Codecov、SonarQube 或其他 CI 工具讀取。",
        f"- HTML：`{html_dir}/index.html`，供人員瀏覽逐行覆蓋率。",
        f"- JSON：`{data_file}`，供後續 Dashboard 或品質閘門使用。",
        "",
        "> 覆蓋率只反映自動化測試執行到的程式路徑，不代表無障礙規範合規，也不能取代 Android／iOS 實機人工檢測。",
        "",
    ])
    markdown_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {markdown_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
