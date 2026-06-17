from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .gate import PacketDecision


class SelfComparisonError(ValueError):
    """Raised when evaluation tries to use expected labels as predictions."""


def evaluate_decisions(
    decisions: list[PacketDecision],
    prediction_source: str = "gate_output",
) -> dict[str, Any]:
    guard = run_self_comparison_guard(decisions)
    correct = [
        decision
        for decision in decisions
        if decision.expected_review_status == decision.predicted_review_status
    ]
    mismatches = [
        asdict(decision)
        for decision in decisions
        if decision.expected_review_status != decision.predicted_review_status
    ]
    return {
        "prediction_source": prediction_source,
        "packet_count": len(decisions),
        "correct_count": len(correct),
        "accuracy": len(correct) / len(decisions) if decisions else 0.0,
        "mismatches": mismatches,
        "status_counts": status_counts(decisions),
        "self_comparison_guard": "PASS" if guard else "FAIL",
        "self_comparison_probe_detected": guard,
    }


def run_self_comparison_guard(decisions: list[PacketDecision]) -> bool:
    copied = {
        decision.packet_id: decision.expected_review_status
        for decision in decisions
    }
    try:
        reject_expected_label_predictions(copied, decisions, prediction_source="expected_labels")
    except SelfComparisonError:
        return True
    return False


def reject_expected_label_predictions(
    predictions_by_packet: dict[str, str],
    decisions: list[PacketDecision],
    prediction_source: str,
) -> None:
    if prediction_source == "expected_labels":
        raise SelfComparisonError("Predictions were copied from expected labels.")
    expected_by_packet = {
        decision.packet_id: decision.expected_review_status
        for decision in decisions
    }
    if predictions_by_packet == expected_by_packet:
        seeded_failures = [
            decision
            for decision in decisions
            if decision.expected_review_status != "PASS"
        ]
        if seeded_failures:
            raise SelfComparisonError(
                "Predictions exactly match expected labels across seeded failures; "
                "provide an independent prediction source."
            )


def status_counts(decisions: list[PacketDecision]) -> dict[str, int]:
    counts = {"PASS": 0, "RETURN_FOR_REVISION": 0, "BLOCK_RELEASE": 0}
    for decision in decisions:
        counts[decision.predicted_review_status] += 1
    return counts

