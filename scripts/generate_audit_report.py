#!/usr/bin/env python3
"""Generate a traceable Markdown accessibility audit report from audit-case JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHECKLIST = ROOT / "references" / "taiwan-aa-checklist.md"
DEFAULT_RULES = ROOT / "rules" / "default-rules.json"

sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_audit_rules import evaluate, load_json  # noqa: E402
from validate_audit_case import validate_file  # noqa: E402

STATUS_LABELS = {
    "pass": "通過",
    "fail": "不通過",
    "not_applicable": "不適用",
    "pending": "待確認",
}


def cell(value: Any) -> str:
    """Convert a value to a safe, single-line Markdown table cell."""

    if value is None:
        return "—"
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    return str(value).replace("|", "\\|").replace("\n", " ").strip() or "—"


def parse_checklist(path: Path) -> dict[str, str]:
    pattern = re.compile(r"^\|\s*(AA-\d{2})\s*\|\s*([^|]+?)\s*\|")
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return result


def indexed(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {item[key]: item for item in items if key in item}


def join_lines(items: list[str]) -> str:
    return "<br>".join(cell(item) for item in items) if items else "—"


def generate_report(document: dict[str, Any], checklist: dict[str, str], violations: list[Any]) -> str:
    case = document.get("case", {})
    findings = indexed(document.get("findings", []), "check_id")
    evidence = indexed(document.get("evidence", []), "evidence_id")
    summary = document.get("summary", {})
    metadata = document.get("metadata", {})
    environments = document.get("case", {}).get("test_environments", [])
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rule_status = "通過" if not violations else f"有 {len(violations)} 項規則違規"

    lines = [
        "# 行動 App／網站無障礙檢測報告",
        "",
        "> 本報告由 v2.0 自動化報告生成器產出；結果只代表指定範圍、版本、環境與證據，不等同於官方認證。",
        "",
        "## 1. 執行摘要",
        "",
        f"**產品：** {cell(case.get('product'))}",
        f"**版本：** {cell(case.get('version'))}",
        f"**案件編號：** {cell(case.get('case_id'))}",
        f"**產出時間：** {generated_at}",
        f"**檢測範圍：** {cell(case.get('scope'))}",
        f"**整體結論：** {cell(summary.get('overall_conclusion'))}",
        f"**規則檢查：** {rule_status}",
        "",
        "| 狀態 | 數量 |",
        "|---|---:|",
    ]
    for key in ("pass", "fail", "not_applicable", "pending", "total"):
        lines.append(f"| {STATUS_LABELS.get(key, '總項目') if key != 'total' else '總項目'} | {cell(summary.get(key, 0))} |")

    lines.extend([
        "",
        "## 2. 範圍、環境與限制",
        "",
        "| 欄位 | 內容 |",
        "|---|---|",
        f"| 平台 | {cell(case.get('platforms'))} |",
        f"| 裝置與 OS | {cell([str(env.get('device_model', '未提供')) + ' / ' + str(env.get('os_version', '未提供')) for env in environments])} |",
        f"| 輔助工具 | {cell([env.get('assistive_technology') for env in environments])} |",
        f"| 測試流程 | {cell([flow.get('name') for flow in case.get('flows', [])])} |",
        f"| 提供材料 | {cell([item.get('type') for item in document.get('evidence', [])])} |",
        "| 未能驗證事項 | 讀屏、焦點、動態通知或其他未具備實機證據的項目應視為待確認。 |",
        "",
        "## 3. 重大缺失與優先順序",
        "",
        "| 優先級 | 編號 | 問題 | 受影響使用者 | 負責角色 |",
        "|---|---|---|---|---|",
    ])
    failures = [finding for finding in document.get("findings", []) if finding.get("status") == "fail"]
    if failures:
        for finding in failures:
            lines.append(
                f"| {cell(finding.get('severity'))} | {cell(finding.get('check_id'))} | {cell(finding.get('title'))} | {cell(finding.get('affected_users'))} | {cell(finding.get('owner_role'))} |"
            )
    else:
        lines.append("| — | — | 本次案件沒有已記錄的不通過項目。 | — | — |")

    lines.extend([
        "",
        "## 4. 逐項檢核結果",
        "",
        "| 編號 | 主題 | 狀態 | 證據 | 觀察結果 | 修正建議 | 回歸測試 |",
        "|---|---|---|---|---|---|---|",
    ])
    for check_id in sorted(checklist):
        finding = findings.get(check_id)
        if finding:
            regression = finding.get("regression", {})
            regression_text = regression.get("expected_result") or finding.get("next_action")
            lines.append(
                f"| {check_id} | {cell(checklist[check_id])} | {STATUS_LABELS.get(finding.get('status'), finding.get('status'))} | {cell(finding.get('evidence_ids'))} | {cell(finding.get('observation'))} | {cell(finding.get('remediation'))} | {cell(regression_text)} |"
            )
        else:
            lines.append(f"| {check_id} | {cell(checklist[check_id])} | 待確認 | — | 尚未有逐項紀錄。 | — | 需補充測試與證據。 |")

    lines.extend([
        "",
        "## 5. 平台測試紀錄",
        "",
        "| 平台 | 裝置／OS | 輔助工具與設定 | 核心流程 | 結果 | 證據 |",
        "|---|---|---|---|---|---|",
    ])
    if environments:
        evidence_by_env: dict[str, list[str]] = {}
        for item in document.get("evidence", []):
            if item.get("environment_id"):
                evidence_by_env.setdefault(item["environment_id"], []).append(item["evidence_id"])
        for env in environments:
            lines.append(
                f"| {cell(env.get('platform'))} | {cell(env.get('device_model'))} / {cell(env.get('os_version'))} | {cell(env.get('assistive_technology'))}: {cell(env.get('settings'))} | {cell([flow.get('name') for flow in case.get('flows', [])])} | 待依實機結果填寫 | {cell(evidence_by_env.get(env.get('environment_id'), []))} |"
            )
    else:
        lines.append("| — | — | — | — | 待確認 | — |")

    lines.extend([
        "",
        "## 6. 修正後回歸測試計畫",
        "",
        "| 編號 | 修正內容 | 測試步驟 | 預期結果 | 實際結果 | 結果 |",
        "|---|---|---|---|---|---|",
    ])
    regressions = [finding for finding in document.get("findings", []) if finding.get("regression")]
    if regressions:
        for finding in regressions:
            regression = finding["regression"]
            lines.append(
                f"| {cell(finding.get('check_id'))} | {cell(finding.get('remediation'))} | {cell(regression.get('steps'))} | {cell(regression.get('expected_result'))} | {cell(regression.get('actual_result'))} | {cell(regression.get('status'))} |"
            )
    else:
        lines.append("| — | 尚未建立回歸紀錄 | — | — | — | 待確認 |")

    pending = [check_id for check_id in sorted(checklist) if check_id not in findings or findings[check_id].get("status") == "pending"]
    lines.extend([
        "",
        "## 7. 待確認事項",
        "",
    ])
    if pending:
        lines.extend(f"{index}. `{check_id}`：{checklist[check_id]} 尚需實機、讀屏或補充證據。" for index, check_id in enumerate(pending, 1))
    else:
        lines.append("1. 本案件沒有待確認項目。")

    if violations:
        lines.extend(["", "### 規則引擎警告", ""])
        for violation in violations:
            lines.append(f"- `{violation.rule_id}`（{violation.severity}，{violation.path}）：{violation.message}")

    lines.extend([
        "",
        "## 8. 聲明",
        "",
        "本文件協助產品、設計、工程與 QA 團隊進行無障礙改善。檢測結果只代表本次指定範圍、版本、環境與證據；正式認證或申請標章前，應依主管機關最新規範與程序辦理。",
        "",
        f"<!-- generated_by=audit-report-generator; schema_version={cell(document.get('schema_version'))}; source_updated_at={cell(metadata.get('updated_at'))} -->",
    ])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a Markdown accessibility audit report.")
    parser.add_argument("case", type=Path, help="audit-case JSON file")
    parser.add_argument("-o", "--output", type=Path, required=True, help="output Markdown path")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--checklist", type=Path, default=DEFAULT_CHECKLIST)
    parser.add_argument("--allow-invalid", action="store_true", help="generate report despite Schema errors")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    validation_errors = validate_file(args.case, ROOT / "schemas" / "audit-case.schema.json")
    if validation_errors and not args.allow_invalid:
        print("ERROR: audit-case failed validation; use --allow-invalid only for a draft report", file=sys.stderr)
        for error in validation_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    try:
        document = load_json(args.case)
        rules_document = load_json(args.rules)
        checklist = parse_checklist(args.checklist)
        violations = evaluate(document, rules_document)
        report = generate_report(document, checklist, violations)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1

    print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
