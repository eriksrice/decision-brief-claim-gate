from __future__ import annotations

import argparse
from pathlib import Path

from .artifacts import write_artifacts
from .evaluation import evaluate_decisions
from .gate import run_gate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="decision-brief-gate",
        description="Run the deterministic decision-brief claim consistency gate.",
    )
    parser.add_argument(
        "--source-metrics",
        default="data/synthetic/source_metrics.csv",
        help="Path to synthetic source metrics CSV.",
    )
    parser.add_argument(
        "--brief-packets",
        default="data/synthetic/brief_packets.csv",
        help="Path to structured synthetic brief packet CSV.",
    )
    parser.add_argument(
        "--claim-rules",
        default="configs/claim_rules.json",
        help="Path to claim rule JSON config.",
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts",
        help="Directory for generated proof artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    gate_run = run_gate(args.source_metrics, args.brief_packets, args.claim_rules)
    evaluation = evaluate_decisions(gate_run.packet_decisions)
    write_artifacts(gate_run, evaluation, args.output_dir)
    print_summary(gate_run, evaluation, Path(args.output_dir))
    if evaluation["accuracy"] != 1.0 or evaluation["self_comparison_guard"] != "PASS":
        return 1
    return 0


def print_summary(gate_run, evaluation, output_dir: Path) -> None:
    decisions_by_packet = {
        decision.packet_id: decision.predicted_review_status
        for decision in gate_run.packet_decisions
    }
    print("Decision Brief Claim Consistency Gate")
    print()
    print(f"Clean packet: {decisions_by_packet.get('PKT_CLEAN')}")
    print(f"Seeded stale text packet: {decisions_by_packet.get('PKT_STALE_TEXT')}")
    print(f"Seeded stale source version packet: {decisions_by_packet.get('PKT_STALE_SOURCE')}")
    print()
    print(f"Failed claims written to {output_dir / 'failed_claims.json'}")
    print(f"Review decision written to {output_dir / 'review_decision.md'}")
    print(f"Evaluation report written to {output_dir / 'evaluation_report.json'}")
    print()
    print("Evaluation: PASS" if evaluation["accuracy"] == 1.0 else "Evaluation: FAIL")
    print(f"Self-comparison guard: {evaluation['self_comparison_guard']}")

