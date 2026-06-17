import unittest

from decision_brief_gate.checks import check_claim
from decision_brief_gate.data_contracts import BriefClaim, SourceMetric


RULES = {
    "current_source_table_version": "V2026_06",
    "numeric_tolerance": 0.000001,
    "missing_caveat_policy": "RETURN_FOR_REVISION",
    "stale_source_version_policy": "BLOCK_RELEASE",
    "trend_mismatch_policy": "RETURN_FOR_REVISION",
    "chart_text_mismatch_policy": "RETURN_FOR_REVISION",
    "metric_value_mismatch_policy": "RETURN_FOR_REVISION",
}


def metric():
    return SourceMetric(
        source_metric_id="cert_active",
        source_table_version="V2026_06",
        metric_name="Active certifications",
        reporting_period="2026-W24",
        source_value="1240",
        prior_source_value="1200",
        trend_direction="increase",
        caveat_required=True,
        required_caveat_code="PRELIMINARY_SNAPSHOT",
    )


def claim(**overrides):
    fields = {
        "packet_id": "PKT",
        "brief_id": "BRIEF",
        "claim_id": "CLM",
        "claim_type": "metric_value",
        "source_metric_id": "cert_active",
        "source_table_version": "V2026_06",
        "source_value": "1240",
        "chart_value": "1240",
        "text_value": "1240",
        "stated_trend_direction": "increase",
        "caveat_required": True,
        "caveat_present": True,
        "caveat_code_present": "PRELIMINARY_SNAPSHOT",
        "expected_review_status": "PASS",
        "seeded_issue": "none",
    }
    fields.update(overrides)
    return BriefClaim(**fields)


class CheckTests(unittest.TestCase):
    def test_metric_value_passes_exact_match(self):
        result = check_claim(claim(), metric(), RULES)
        self.assertTrue(result.check_passed)

    def test_metric_value_fails_stale_text(self):
        result = check_claim(claim(text_value="1180"), metric(), RULES)
        self.assertFalse(result.check_passed)
        self.assertEqual(result.failure_status, "RETURN_FOR_REVISION")
        self.assertEqual(result.evidence["source_value"], "1240")

    def test_trend_direction_fails_wrong_trend(self):
        result = check_claim(
            claim(claim_type="trend_direction", stated_trend_direction="decrease"),
            metric(),
            RULES,
        )
        self.assertFalse(result.check_passed)
        self.assertEqual(result.failure_status, "RETURN_FOR_REVISION")

    def test_source_version_blocks_stale_version(self):
        result = check_claim(
            claim(claim_type="source_version", source_table_version="V2026_05"),
            metric(),
            RULES,
        )
        self.assertFalse(result.check_passed)
        self.assertEqual(result.failure_status, "BLOCK_RELEASE")

    def test_chart_text_consistency_fails_stale_chart(self):
        result = check_claim(
            claim(claim_type="chart_text_consistency", chart_value="1200"),
            metric(),
            RULES,
        )
        self.assertFalse(result.check_passed)
        self.assertEqual(result.failure_status, "RETURN_FOR_REVISION")

    def test_required_caveat_fails_missing_caveat(self):
        result = check_claim(
            claim(claim_type="required_caveat", caveat_present=False, caveat_code_present=""),
            metric(),
            RULES,
        )
        self.assertFalse(result.check_passed)
        self.assertEqual(result.failure_status, "RETURN_FOR_REVISION")


if __name__ == "__main__":
    unittest.main()

