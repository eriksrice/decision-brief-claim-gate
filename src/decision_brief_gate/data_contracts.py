from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CLAIM_TYPES = {
    "metric_value",
    "trend_direction",
    "source_version",
    "chart_text_consistency",
    "required_caveat",
}
REVIEW_STATUSES = {"PASS", "RETURN_FOR_REVISION", "BLOCK_RELEASE"}
TREND_VALUES = {"increase", "decrease", "flat", "unavailable", ""}


class DataContractError(ValueError):
    """Raised when synthetic inputs violate the explicit data contract."""


@dataclass(frozen=True)
class SourceMetric:
    source_metric_id: str
    source_table_version: str
    metric_name: str
    reporting_period: str
    source_value: str
    prior_source_value: str
    trend_direction: str
    caveat_required: bool
    required_caveat_code: str


@dataclass(frozen=True)
class BriefClaim:
    packet_id: str
    brief_id: str
    claim_id: str
    claim_type: str
    source_metric_id: str
    source_table_version: str
    source_value: str
    chart_value: str
    text_value: str
    stated_trend_direction: str
    caveat_required: bool
    caveat_present: bool
    caveat_code_present: str
    expected_review_status: str
    seeded_issue: str


def parse_bool(raw: str, field_name: str) -> bool:
    value = raw.strip().lower()
    if value == "true":
        return True
    if value == "false":
        return False
    raise DataContractError(f"{field_name} must be true or false, got {raw!r}")


def load_rules(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        rules = json.load(handle)
    required = {
        "current_source_table_version",
        "numeric_tolerance",
        "missing_caveat_policy",
        "stale_source_version_policy",
        "trend_mismatch_policy",
        "chart_text_mismatch_policy",
        "metric_value_mismatch_policy",
    }
    missing = required - set(rules)
    if missing:
        raise DataContractError(f"Missing claim rule fields: {sorted(missing)}")
    return rules


def load_source_metrics(path: str | Path) -> dict[str, SourceMetric]:
    metrics: dict[str, SourceMetric] = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            metric = SourceMetric(
                source_metric_id=require(row, "source_metric_id"),
                source_table_version=require(row, "source_table_version"),
                metric_name=require(row, "metric_name"),
                reporting_period=require(row, "reporting_period"),
                source_value=require(row, "source_value"),
                prior_source_value=require(row, "prior_source_value"),
                trend_direction=require(row, "trend_direction"),
                caveat_required=parse_bool(require(row, "caveat_required"), "caveat_required"),
                required_caveat_code=row.get("required_caveat_code", "").strip(),
            )
            if metric.trend_direction not in TREND_VALUES - {""}:
                raise DataContractError(f"Invalid trend direction for {metric.source_metric_id}")
            if metric.source_metric_id in metrics:
                raise DataContractError(f"Duplicate source metric: {metric.source_metric_id}")
            metrics[metric.source_metric_id] = metric
    if not metrics:
        raise DataContractError("source_metrics.csv has no rows")
    return metrics


def load_brief_claims(path: str | Path) -> list[BriefClaim]:
    claims: list[BriefClaim] = []
    seen_claim_ids: set[str] = set()
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            claim = BriefClaim(
                packet_id=require(row, "packet_id"),
                brief_id=require(row, "brief_id"),
                claim_id=require(row, "claim_id"),
                claim_type=require(row, "claim_type"),
                source_metric_id=require(row, "source_metric_id"),
                source_table_version=require(row, "source_table_version"),
                source_value=row.get("source_value", "").strip(),
                chart_value=row.get("chart_value", "").strip(),
                text_value=row.get("text_value", "").strip(),
                stated_trend_direction=row.get("stated_trend_direction", "").strip(),
                caveat_required=parse_bool(require(row, "caveat_required"), "caveat_required"),
                caveat_present=parse_bool(require(row, "caveat_present"), "caveat_present"),
                caveat_code_present=row.get("caveat_code_present", "").strip(),
                expected_review_status=require(row, "expected_review_status"),
                seeded_issue=require(row, "seeded_issue"),
            )
            validate_claim(claim)
            if claim.claim_id in seen_claim_ids:
                raise DataContractError(f"Duplicate claim id: {claim.claim_id}")
            seen_claim_ids.add(claim.claim_id)
            claims.append(claim)
    if not claims:
        raise DataContractError("brief_packets.csv has no rows")
    return claims


def validate_claim(claim: BriefClaim) -> None:
    if claim.claim_type not in CLAIM_TYPES:
        raise DataContractError(f"Invalid claim type for {claim.claim_id}: {claim.claim_type}")
    if claim.expected_review_status not in REVIEW_STATUSES:
        raise DataContractError(
            f"Invalid expected review status for {claim.claim_id}: {claim.expected_review_status}"
        )
    if claim.stated_trend_direction not in TREND_VALUES:
        raise DataContractError(
            f"Invalid stated trend direction for {claim.claim_id}: {claim.stated_trend_direction}"
        )


def require(row: dict[str, str], field_name: str) -> str:
    value = row.get(field_name, "").strip()
    if value == "":
        raise DataContractError(f"Missing required field: {field_name}")
    return value

