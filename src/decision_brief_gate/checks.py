from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .data_contracts import BriefClaim, SourceMetric


@dataclass(frozen=True)
class ClaimCheckResult:
    packet_id: str
    brief_id: str
    claim_id: str
    claim_type: str
    source_metric_id: str
    seeded_issue: str
    check_passed: bool
    failure_status: str
    message: str
    evidence: dict[str, Any]


def check_claim(
    claim: BriefClaim,
    source_metric: SourceMetric | None,
    rules: dict[str, Any],
) -> ClaimCheckResult:
    if source_metric is None:
        return fail(
            claim,
            "BLOCK_RELEASE",
            f"Unknown source metric: {claim.source_metric_id}",
            {"source_metric_id": claim.source_metric_id},
        )

    if claim.claim_type == "metric_value":
        return check_metric_value(claim, source_metric, rules)
    if claim.claim_type == "trend_direction":
        return check_trend_direction(claim, source_metric, rules)
    if claim.claim_type == "source_version":
        return check_source_version(claim, source_metric, rules)
    if claim.claim_type == "chart_text_consistency":
        return check_chart_text_consistency(claim, source_metric, rules)
    if claim.claim_type == "required_caveat":
        return check_required_caveat(claim, source_metric, rules)

    return fail(claim, "BLOCK_RELEASE", f"Unsupported claim type: {claim.claim_type}", {})


def check_metric_value(
    claim: BriefClaim,
    source_metric: SourceMetric,
    rules: dict[str, Any],
) -> ClaimCheckResult:
    if values_equal(source_metric.source_value, claim.text_value, rules["numeric_tolerance"]):
        return passed(
            claim,
            "Text value matches source value.",
            {"source_value": source_metric.source_value, "text_value": claim.text_value},
        )
    return fail(
        claim,
        rules["metric_value_mismatch_policy"],
        "Text value does not match source value.",
        {"source_value": source_metric.source_value, "text_value": claim.text_value},
    )


def check_trend_direction(
    claim: BriefClaim,
    source_metric: SourceMetric,
    rules: dict[str, Any],
) -> ClaimCheckResult:
    if claim.stated_trend_direction == source_metric.trend_direction:
        return passed(
            claim,
            "Stated trend matches source-derived trend.",
            {
                "source_trend_direction": source_metric.trend_direction,
                "stated_trend_direction": claim.stated_trend_direction,
            },
        )
    return fail(
        claim,
        rules["trend_mismatch_policy"],
        "Stated trend does not match source-derived trend.",
        {
            "source_trend_direction": source_metric.trend_direction,
            "stated_trend_direction": claim.stated_trend_direction,
        },
    )


def check_source_version(
    claim: BriefClaim,
    source_metric: SourceMetric,
    rules: dict[str, Any],
) -> ClaimCheckResult:
    current_version = rules["current_source_table_version"]
    if claim.source_table_version == current_version == source_metric.source_table_version:
        return passed(
            claim,
            "Claim uses the current source table version.",
            {
                "claim_source_table_version": claim.source_table_version,
                "current_source_table_version": current_version,
                "metric_source_table_version": source_metric.source_table_version,
            },
        )
    return fail(
        claim,
        rules["stale_source_version_policy"],
        "Claim does not use the current source table version.",
        {
            "claim_source_table_version": claim.source_table_version,
            "current_source_table_version": current_version,
            "metric_source_table_version": source_metric.source_table_version,
        },
    )


def check_chart_text_consistency(
    claim: BriefClaim,
    source_metric: SourceMetric,
    rules: dict[str, Any],
) -> ClaimCheckResult:
    source_matches_text = values_equal(source_metric.source_value, claim.text_value, rules["numeric_tolerance"])
    source_matches_chart = values_equal(source_metric.source_value, claim.chart_value, rules["numeric_tolerance"])
    if source_matches_text and source_matches_chart:
        return passed(
            claim,
            "Chart, text, and source values agree.",
            {
                "source_value": source_metric.source_value,
                "chart_value": claim.chart_value,
                "text_value": claim.text_value,
            },
        )
    return fail(
        claim,
        rules["chart_text_mismatch_policy"],
        "Chart, text, and source values do not agree.",
        {
            "source_value": source_metric.source_value,
            "chart_value": claim.chart_value,
            "text_value": claim.text_value,
        },
    )


def check_required_caveat(
    claim: BriefClaim,
    source_metric: SourceMetric,
    rules: dict[str, Any],
) -> ClaimCheckResult:
    caveat_required = source_metric.caveat_required or claim.caveat_required
    expected_code = source_metric.required_caveat_code
    caveat_ok = (not caveat_required) or (
        claim.caveat_present and claim.caveat_code_present == expected_code
    )
    if caveat_ok:
        return passed(
            claim,
            "Required caveat is present.",
            {
                "caveat_required": caveat_required,
                "expected_caveat_code": expected_code,
                "caveat_present": claim.caveat_present,
                "caveat_code_present": claim.caveat_code_present,
            },
        )
    return fail(
        claim,
        rules["missing_caveat_policy"],
        "Required caveat is missing or uses the wrong code.",
        {
            "caveat_required": caveat_required,
            "expected_caveat_code": expected_code,
            "caveat_present": claim.caveat_present,
            "caveat_code_present": claim.caveat_code_present,
        },
    )


def values_equal(left: str, right: str, tolerance: float) -> bool:
    if left == "" or right == "":
        return left == right
    try:
        return abs(float(left) - float(right)) <= float(tolerance)
    except ValueError:
        return left == right


def passed(claim: BriefClaim, message: str, evidence: dict[str, Any]) -> ClaimCheckResult:
    return ClaimCheckResult(
        packet_id=claim.packet_id,
        brief_id=claim.brief_id,
        claim_id=claim.claim_id,
        claim_type=claim.claim_type,
        source_metric_id=claim.source_metric_id,
        seeded_issue=claim.seeded_issue,
        check_passed=True,
        failure_status="",
        message=message,
        evidence=evidence,
    )


def fail(
    claim: BriefClaim,
    failure_status: str,
    message: str,
    evidence: dict[str, Any],
) -> ClaimCheckResult:
    return ClaimCheckResult(
        packet_id=claim.packet_id,
        brief_id=claim.brief_id,
        claim_id=claim.claim_id,
        claim_type=claim.claim_type,
        source_metric_id=claim.source_metric_id,
        seeded_issue=claim.seeded_issue,
        check_passed=False,
        failure_status=failure_status,
        message=message,
        evidence=evidence,
    )

