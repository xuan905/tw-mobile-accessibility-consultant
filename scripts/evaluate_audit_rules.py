#!/usr/bin/env python3
"""Evaluate deterministic quality rules against an audit-case document."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES = ROOT / "rules" / "default-rules.json"


@dataclass(frozen=True)
class RuleViolation:
    rule_id: str
    severity: str
    message: str
    path: str


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


def field_value(target: dict[str, Any], field: str) -> Any:
    return target.get(field)


def condition_matches(condition: dict[str, Any], target: dict[str, Any], document: dict[str, Any]) -> bool:
    if "status_equals" in condition and target.get("status") != condition["status_equals"]:
        return False
    if "status_in" in condition and target.get("status") not in condition["status_in"]:
        return False
    if "field_exists" in condition and condition["field_exists"] not in target:
        return False
    if "summary_pending_gt" in condition:
        if document.get("summary", {}).get("pending", 0) <= condition["summary_pending_gt"]:
            return False
    if "summary_overall_not_equals" in condition:
        if document.get("summary", {}).get("overall_conclusion") == condition["summary_overall_not_equals"]:
            return False
    return True


def assertion_passes(assertion: dict[str, Any], target: dict[str, Any]) -> bool:
    field = assertion.get("field")
    value = field_value(target, field) if field else None
    if "min_items" in assertion:
        if not isinstance(value, list) or len(value) < assertion["min_items"]:
            return False
    if "not_empty" in assertion and assertion["not_empty"]:
        if not isinstance(value, str) or not value.strip():
            return False
    if "summary_overall_not_equals" in assertion:
        summary = target.get("summary", {})
        if summary.get("overall_conclusion") == assertion["summary_overall_not_equals"]:
            return False
    return True


def targets_for_rule(rule: dict[str, Any], document: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    scope = rule.get("scope")
    if scope == "finding":
        return [(f"$.findings[{index}]", finding) for index, finding in enumerate(document.get("findings", []))]
    if scope == "case":
        return [("$.case", document.get("case", {}))]
    if scope == "document":
        return [("$", document)]
    raise ValueError(f"unsupported rule scope: {scope}")


def evaluate(document: dict[str, Any], rules_document: dict[str, Any]) -> list[RuleViolation]:
    violations: list[RuleViolation] = []
    for rule in rules_document.get("rules", []):
        for path, target in targets_for_rule(rule, document):
            if condition_matches(rule.get("when", {}), target, document) and not assertion_passes(
                rule.get("assert", {}), target
            ):
                violations.append(
                    RuleViolation(
                        rule_id=rule["rule_id"],
                        severity=rule.get("severity", "medium"),
                        message=rule.get("message", "規則未通過"),
                        path=path,
                    )
                )
    return violations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate audit-case quality rules.")
    parser.add_argument("case", type=Path, help="audit-case JSON file")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES, help="rules JSON file")
    parser.add_argument("--format", choices=("text", "json"), default="text", dest="output_format")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        document = load_json(args.case)
        rules_document = load_json(args.rules)
        violations = evaluate(document, rules_document)
    except ValueError as exc:
        print(f"ERROR {exc}")
        return 1

    if args.output_format == "json":
        print(json.dumps([asdict(item) for item in violations], ensure_ascii=False, indent=2))
    elif violations:
        print(f"FAIL {args.case}: {len(violations)} rule violation(s)")
        for violation in violations:
            print(f"  - [{violation.severity}] {violation.rule_id} {violation.path}: {violation.message}")
    else:
        print(f"PASS {args.case}: no rule violations")

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
