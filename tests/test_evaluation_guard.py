import unittest

from decision_brief_gate.evaluation import (
    SelfComparisonError,
    evaluate_decisions,
    reject_expected_label_predictions,
)
from decision_brief_gate.gate import run_gate


class EvaluationGuardTests(unittest.TestCase):
    def test_evaluation_is_perfect_for_seeded_demo(self):
        gate_run = run_gate(
            "data/synthetic/source_metrics.csv",
            "data/synthetic/brief_packets.csv",
            "configs/claim_rules.json",
        )
        evaluation = evaluate_decisions(gate_run.packet_decisions)
        self.assertEqual(evaluation["accuracy"], 1.0)
        self.assertEqual(evaluation["self_comparison_guard"], "PASS")
        self.assertTrue(evaluation["self_comparison_probe_detected"])

    def test_expected_label_predictions_are_rejected(self):
        gate_run = run_gate(
            "data/synthetic/source_metrics.csv",
            "data/synthetic/brief_packets.csv",
            "configs/claim_rules.json",
        )
        copied_predictions = {
            decision.packet_id: decision.expected_review_status
            for decision in gate_run.packet_decisions
        }
        with self.assertRaises(SelfComparisonError):
            reject_expected_label_predictions(
                copied_predictions,
                gate_run.packet_decisions,
                prediction_source="expected_labels",
            )


if __name__ == "__main__":
    unittest.main()

