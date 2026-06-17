# Interview Walkthrough

Use this as the five-minute narration path for a technical reviewer or hiring manager.

## 0:00 - Project Frame

"This is a deterministic release gate for synthetic public-health decision briefs. It catches the failure mode where a brief reads cleanly, but one of its analytic claims no longer matches the source data, chart value, source snapshot, or required caveat."

Boundary to say out loud:

"It uses only synthetic data. It does not parse real documents, use live LLM judgment, or make public-health recommendations."

## 0:45 - Why It Is Senior-Level

"The point is not a bigger app. The point is a trustworthy release-control pattern: explicit data contracts, deterministic checks, generated artifacts, and evaluation that separates expected labels from gate predictions."

Point to:

- `data/synthetic/brief_packets.csv`
- `data/synthetic/source_metrics.csv`
- `configs/claim_rules.json`

## 1:30 - Run The Demo

Run:

```bash
./scripts/demo.sh
```

Expected output:

```text
Clean packet: PASS
Seeded stale text packet: RETURN_FOR_REVISION
Seeded stale source version packet: BLOCK_RELEASE
Evaluation: PASS
Self-comparison guard: PASS
```

What to say:

"The clean packet passes. A stale text value returns for revision. A stale source snapshot blocks release."

## 2:15 - Show The Failed Claim

Open:

```bash
artifacts/failed_claims.json
```

Point to `PKT_STALE_TEXT`:

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

What to say:

"The gate does not just say the brief is bad. It shows the exact contradiction: source value 1240 versus text value 1180."

## 3:00 - Show The Hard Block

Point to `PKT_STALE_SOURCE`:

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

What to say:

"A stale source snapshot is stricter than a stale text value. It blocks release because the packet is tied to the wrong evidence version."

## 3:45 - Show Evaluation

Open:

```bash
artifacts/evaluation_report.json
```

Current result:

```json
{
  "accuracy": 1.0,
  "packet_count": 6,
  "self_comparison_guard": "PASS"
}
```

What to say:

"The evaluator compares expected review statuses to independent gate output. The self-comparison guard probes a common evaluation flaw: accidentally comparing expected labels to themselves."

## 4:30 - Close

"This v1 is intentionally structured and deterministic. The future extension would be optional claim extraction, but only after the evidence contract is proven. That keeps the first version auditable and prevents it from becoming a vague writing assistant."

## Likely Questions

**Why no LLM in v1?**

Because the release-control value depends on deterministic evidence checks. LLM extraction can be added later, but only downstream of a proven contract.

**Why synthetic data?**

The portfolio signal is the reliability pattern, not access to private records. Synthetic data keeps the project public-safe and reproducible.

**How is this different from P061?**

P061 handles forecast governance replay. This project handles leadership-brief claim integrity across source values, charts, source versions, and caveats.

**What would you add next?**

Optional claim extraction, richer synthetic scenarios, and a release evidence ledger. I would not add a dashboard until the contract and checks are boringly reliable.

