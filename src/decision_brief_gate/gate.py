from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .checks import ClaimCheckResult, check_claim
from .data_contracts import BriefClaim, load_brief_claims, load_rules, load_source_metrics


@dataclass(frozen=True)
class PacketDecision:
    packet_id: str
    brief_id: str
    expected_review_status: str
    predicted_review_status: str
    failed_claim_count: int
    total_claim_count: int


@dataclass(frozen=True)
class GateRun:
    claim_results: list[ClaimCheckResult]
    packet_decisions: list[PacketDecision]

    @property
    def failed_claims(self) -> list[ClaimCheckResult]:
        return [result for result in self.claim_results if not result.check_passed]


def run_gate(
    source_metrics_path: str | Path,
    brief_packets_path: str | Path,
    rules_path: str | Path,
) -> GateRun:
    rules = load_rules(rules_path)
    metrics = load_source_metrics(source_metrics_path)
    claims = load_brief_claims(brief_packets_path)
    claim_results = [check_claim(claim, metrics.get(claim.source_metric_id), rules) for claim in claims]
    return GateRun(
        claim_results=claim_results,
        packet_decisions=build_packet_decisions(claims, claim_results),
    )


def build_packet_decisions(
    claims: list[BriefClaim],
    results: list[ClaimCheckResult],
) -> list[PacketDecision]:
    claims_by_packet: dict[str, list[BriefClaim]] = defaultdict(list)
    results_by_packet: dict[str, list[ClaimCheckResult]] = defaultdict(list)
    for claim in claims:
        claims_by_packet[claim.packet_id].append(claim)
    for result in results:
        results_by_packet[result.packet_id].append(result)

    decisions: list[PacketDecision] = []
    for packet_id in sorted(claims_by_packet):
        packet_claims = claims_by_packet[packet_id]
        packet_results = results_by_packet[packet_id]
        expected_statuses = {claim.expected_review_status for claim in packet_claims}
        if len(expected_statuses) != 1:
            raise ValueError(f"Packet {packet_id} has conflicting expected statuses: {expected_statuses}")
        failed = [result for result in packet_results if not result.check_passed]
        predicted = aggregate_status(failed)
        decisions.append(
            PacketDecision(
                packet_id=packet_id,
                brief_id=packet_claims[0].brief_id,
                expected_review_status=expected_statuses.pop(),
                predicted_review_status=predicted,
                failed_claim_count=len(failed),
                total_claim_count=len(packet_claims),
            )
        )
    return decisions


def aggregate_status(failed_results: list[ClaimCheckResult]) -> str:
    if any(result.failure_status == "BLOCK_RELEASE" for result in failed_results):
        return "BLOCK_RELEASE"
    if failed_results:
        return "RETURN_FOR_REVISION"
    return "PASS"

