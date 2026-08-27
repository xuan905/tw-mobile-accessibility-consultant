"""Typed Python framework for the audit-case v2.0 model.

The JSON Schema remains the source of truth. This module intentionally provides
small convenience types and document-level helpers rather than duplicating all
Schema validation rules.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypedDict
import json

AuditStatus = Literal["pass", "fail", "not_applicable", "pending"]
VerificationLevel = Literal[
    "observed", "reproducible", "inferred", "pending_review"
]


class Finding(TypedDict, total=False):
    finding_id: str
    check_id: str
    status: AuditStatus
    title: str
    severity: str
    evidence_ids: list[str]
    flow_ids: list[str]
    environment_ids: list[str]
    observation: str
    expected_result: str
    remediation: str
    owner_role: str
    next_action: str


class AuditCaseDocument(TypedDict, total=False):
    schema_version: str
    case: dict[str, Any]
    evidence: list[dict[str, Any]]
    findings: list[Finding]
    summary: dict[str, Any]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class StatusSummary:
    """Counts for a complete 42-item checklist."""

    passed: int
    failed: int
    not_applicable: int
    pending: int

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.not_applicable + self.pending


def load_case(path: str | Path) -> AuditCaseDocument:
    """Load a UTF-8 audit-case JSON document without performing validation."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def summarize_findings(
    findings: list[Finding], checklist_total: int = 42
) -> StatusSummary:
    """Count findings and treat unrecorded checklist items as pending."""

    counts = Counter(finding["status"] for finding in findings)
    pending = counts["pending"] + max(0, checklist_total - len(findings))
    return StatusSummary(
        passed=counts["pass"],
        failed=counts["fail"],
        not_applicable=counts["not_applicable"],
        pending=pending,
    )


def evidence_ids(document: AuditCaseDocument) -> set[str]:
    """Return evidence IDs available for cross-reference checks."""

    return {
        evidence["evidence_id"]
        for evidence in document.get("evidence", [])
        if "evidence_id" in evidence
    }
