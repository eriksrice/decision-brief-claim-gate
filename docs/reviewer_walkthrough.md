# Reviewer Walkthrough

This project is a deterministic release gate for synthetic public-health decision-brief claims. It checks whether structured brief claims still match the source data, chart values, source snapshot version, and required caveats before release.

It uses no real WTCHP data, records, documents, people, or official claims.

## Five-Minute Proof Path

Run:

```bash
./scripts/demo.sh
```

Expected console output:

```text
Decision Brief Claim Consistency Gate

Clean packet: PASS
Seeded stale text packet: RETURN_FOR_REVISION
Seeded stale source version packet: BLOCK_RELEASE

Failed claims written to artifacts/failed_claims.json
Review decision written to artifacts/review_decision.md
Evaluation report written to artifacts/evaluation_report.json

Evaluation: PASS
Self-comparison guard: PASS
```

## What The Gate Checks

The gate reads structured synthetic claim packets from `data/synthetic/brief_packets.csv` and source evidence from `data/synthetic/source_metrics.csv`.

It checks five claim types:

- `metric_value`: text value must match the source metric.
- `trend_direction`: stated trend must match source-derived trend.
- `source_version`: claim must use the current source snapshot.
- `chart_text_consistency`: chart, text, and source must agree.
- `required_caveat`: required caveat must be present with the expected code.

## Release Decisions

Generated artifact: `artifacts/review_decision.md`

| Packet | Expected | Predicted | Meaning |
|---|---|---|---|
| `PKT_CLEAN` | `PASS` | `PASS` | Valid release packet. |
| `PKT_STALE_TEXT` | `RETURN_FOR_REVISION` | `RETURN_FOR_REVISION` | Brief text uses a stale metric value. |
| `PKT_STALE_CHART` | `RETURN_FOR_REVISION` | `RETURN_FOR_REVISION` | Chart value disagrees with text and source. |
| `PKT_MISSING_CAVEAT` | `RETURN_FOR_REVISION` | `RETURN_FOR_REVISION` | Required caveat is missing. |
| `PKT_STALE_SOURCE` | `BLOCK_RELEASE` | `BLOCK_RELEASE` | Claim uses an old source snapshot. |
| `PKT_WRONG_TREND` | `RETURN_FOR_REVISION` | `RETURN_FOR_REVISION` | Stated trend disagrees with source-derived trend. |

## Failed-Claim Evidence

Generated artifact: `artifacts/failed_claims.json`

Examples:

```json
{
  "packet_id": "PKT_STALE_TEXT",
  "claim_type": "metric_value",
  "failure_status": "RETURN_FOR_REVISION",
  "evidence": {
    "source_value": "1240",
    "text_value": "1180"
  }
}
```

```json
{
  "packet_id": "PKT_STALE_SOURCE",
  "claim_type": "source_version",
  "failure_status": "BLOCK_RELEASE",
  "evidence": {
    "claim_source_table_version": "V2026_05",
    "current_source_table_version": "V2026_06",
    "metric_source_table_version": "V2026_06"
  }
}
```

These are the core reviewer artifacts: the gate does not merely say a brief failed. It names the claim, failure status, issue type, and exact evidence fields.

## Evaluation

Generated artifact: `artifacts/evaluation_report.json`

Current demo result:

```json
{
  "accuracy": 1.0,
  "correct_count": 6,
  "packet_count": 6,
  "self_comparison_guard": "PASS",
  "self_comparison_probe_detected": true
}
```

The self-comparison guard matters because a release gate should compare independent predictions against expected labels. The probe intentionally simulates copied expected labels and confirms the evaluator can reject that failure mode.

## What V1 Does Not Do

- It does not parse full documents.
- It does not use live LLM judgment.
- It does not generate memos.
- It does not make public-health recommendations.
- It does not use real WTCHP data.
- It does not duplicate P061 forecast governance.

## Why This Complements P061

P061 owns forecast governance and replay. This project owns leadership-brief claim integrity: the final release text, chart value, source version, and caveat state must match the evidence before the packet is released.

