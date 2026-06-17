import unittest

from decision_brief_gate.gate import aggregate_status, run_gate


class GateTests(unittest.TestCase):
    def test_seeded_packets_get_expected_decisions(self):
        gate_run = run_gate(
            "data/synthetic/source_metrics.csv",
            "data/synthetic/brief_packets.csv",
            "configs/claim_rules.json",
        )
        decisions = {
            decision.packet_id: decision.predicted_review_status
            for decision in gate_run.packet_decisions
        }
        self.assertEqual(decisions["PKT_CLEAN"], "PASS")
        self.assertEqual(decisions["PKT_STALE_TEXT"], "RETURN_FOR_REVISION")
        self.assertEqual(decisions["PKT_STALE_CHART"], "RETURN_FOR_REVISION")
        self.assertEqual(decisions["PKT_MISSING_CAVEAT"], "RETURN_FOR_REVISION")
        self.assertEqual(decisions["PKT_STALE_SOURCE"], "BLOCK_RELEASE")
        self.assertEqual(decisions["PKT_WRONG_TREND"], "RETURN_FOR_REVISION")

    def test_failed_claim_register_has_exact_evidence(self):
        gate_run = run_gate(
            "data/synthetic/source_metrics.csv",
            "data/synthetic/brief_packets.csv",
            "configs/claim_rules.json",
        )
        stale_text = next(
            result
            for result in gate_run.failed_claims
            if result.seeded_issue == "stale_text_value"
        )
        self.assertEqual(stale_text.evidence["source_value"], "1240")
        self.assertEqual(stale_text.evidence["text_value"], "1180")

    def test_block_status_wins_over_revision_status(self):
        class Failed:
            def __init__(self, status):
                self.failure_status = status

        self.assertEqual(
            aggregate_status([Failed("RETURN_FOR_REVISION"), Failed("BLOCK_RELEASE")]),
            "BLOCK_RELEASE",
        )


if __name__ == "__main__":
    unittest.main()

