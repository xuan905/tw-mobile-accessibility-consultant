#!/usr/bin/env python3
"""Validate an accessibility audit-case JSON document.

The validator performs two layers of checks:
1. JSON Schema Draft 2020-12 validation.
2. Cross-reference and summary consistency checks that are intentionally
   kept outside the schema because they depend on the complete document.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - exercised by CLI users
    raise SystemExit(
        "Missing dependency: install it with `python -m pip install jsonschema`."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "audit-case.schema.json"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


def schema_errors(document: Any, schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        location = "$." + ".".join(str(part) for part in error.path) if error.path else "$"
        errors.append(f"{location}: {error.message}")
    return errors


def cross_reference_errors(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence_ids = {item["evidence_id"] for item in document.get("evidence", [])}
    flow_ids = {
        flow["flow_id"]
        for flow in document.get("case", {}).get("flows", [])
    }
    environment_ids = {
        env["environment_id"]
        for env in document.get("case", {}).get("test_environments", [])
    }

    for index, finding in enumerate(document.get("findings", [])):
        prefix = f"$.findings[{index}]"
        for evidence_id in finding.get("evidence_ids", []):
            if evidence_id not in evidence_ids:
                errors.append(f"{prefix}.evidence_ids: unknown evidence id {evidence_id}")
        for flow_id in finding.get("flow_ids", []):
            if flow_id not in flow_ids:
                errors.append(f"{prefix}.flow_ids: unknown flow id {flow_id}")
        for environment_id in finding.get("environment_ids", []):
            if environment_id not in environment_ids:
                errors.append(
                    f"{prefix}.environment_ids: unknown environment id {environment_id}"
                )

    summary = document.get("summary")
    if summary:
        findings = document.get("findings", [])
        expected = Counter(
            {
                "pass": 0,
                "fail": 0,
                "not_applicable": 0,
                "pending": 0,
            }
        )
        expected.update(finding.get("status") for finding in findings)
        # A case may intentionally record only observed findings while the
        # remaining AA checks are still pending. Count those unrecorded checks
        # as implicit pending items so partial cases remain useful.
        implicit_pending = max(0, 42 - len(findings))
        expected["pending"] += implicit_pending
        for status, count in expected.items():
            if summary.get(status) != count:
                errors.append(
                    f"$.summary.{status}: expected {count} from findings, got {summary.get(status)}"
                )
        total = sum(expected.values())
        if summary.get("total") != 42:
            errors.append("$.summary.total: must be 42 for the complete AA checklist")
        if len(findings) > 42:
            errors.append(f"$.findings: contains {len(findings)} findings, which exceeds 42")

    return errors


def validate_file(path: Path, schema_path: Path) -> list[str]:
    try:
        document = load_json(path)
        schema = load_json(schema_path)
    except ValueError as exc:
        return [str(exc)]

    errors = schema_errors(document, schema)
    if not errors and isinstance(document, dict):
        errors.extend(cross_reference_errors(document))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate one or more accessibility audit-case JSON files."
    )
    parser.add_argument("files", nargs="+", type=Path, help="audit-case JSON file(s)")
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help=f"JSON Schema path (default: {DEFAULT_SCHEMA})",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
        help="output format for automation (default: text)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = []
    for file_path in args.files:
        errors = validate_file(file_path, args.schema)
        results.append({"file": str(file_path), "valid": not errors, "errors": errors})

    if args.output_format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            if result["valid"]:
                print(f"PASS {result['file']}")
            else:
                print(f"FAIL {result['file']}")
                for error in result["errors"]:
                    print(f"  - {error}")

    return 0 if all(result["valid"] for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
