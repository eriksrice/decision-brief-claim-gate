from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .checks import ClaimCheckResult
from .gate import GateRun, PacketDecision


def write_artifacts(gate_run: GateRun, evaluation: dict[str, Any], output_dir: str | Path) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    write_claim_audit(gate_run.claim_results, output / "brief_claim_consistency_audit.csv")
    write_failed_claims(gate_run.failed_claims, output / "failed_claims.json")
    write_review_decision(gate_run.packet_decisions, output / "review_decision.md")
    write_evaluation_report(evaluation, output / "evaluation_report.json")


def write_claim_audit(results: list[ClaimCheckResult], path: Path) -> None:
    fieldnames = [
        "packet_id",
        "brief_id",
        "claim_id",
        "claim_type",
        "source_metric_id",
        "seeded_issue",
        "check_passed",
        "failure_status",
        "message",
        "evidence",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            row = asdict(result)
            row["evidence"] = json.dumps(result.evidence, sort_keys=True)
            writer.writerow(row)


def write_failed_claims(results: list[ClaimCheckResult], path: Path) -> None:
    payload = [
        {
            "packet_id": result.packet_id,
            "brief_id": result.brief_id,
            "claim_id": result.claim_id,
            "claim_type": result.claim_type,
            "source_metric_id": result.source_metric_id,
            "seeded_issue": result.seeded_issue,
            "failure_status": result.failure_status,
            "message": result.message,
            "evidence": result.evidence,
        }
        for result in results
    ]
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_review_decision(decisions: list[PacketDecision], path: Path) -> None:
    lines = [
        "# Review Decision",
        "",
        "| Packet | Brief | Expected | Predicted | Failed Claims | Total Claims |",
        "|---|---|---|---|---:|---:|",
    ]
    for decision in decisions:
        lines.append(
            "| {packet} | {brief} | {expected} | {predicted} | {failed} | {total} |".format(
                packet=decision.packet_id,
                brief=decision.brief_id,
                expected=decision.expected_review_status,
                predicted=decision.predicted_review_status,
                failed=decision.failed_claim_count,
                total=decision.total_claim_count,
            )
        )
    lines.extend(
        [
            "",
            "Release rule: any `BLOCK_RELEASE` claim blocks the packet; otherwise any failed claim returns the packet for revision.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_evaluation_report(evaluation: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")

