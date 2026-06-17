# Decision Brief Claim Consistency Gate

Deterministic release gate for synthetic public-health decision briefs. It blocks a brief when structured claims, chart values, source snapshots, or required caveats no longer match the evidence.

## Why This Exists

Leadership-facing analytics briefs can look polished while carrying stale values, chart/text mismatches, old source snapshots, or missing caveats. This project treats brief claims as evidence-bound release artifacts: every claim must reconcile with its source metric, chart value, source version, and caveat rule before release.

This is a synthetic portfolio project. It uses no real WTCHP data, records, reports, people, or official claims.

## Quick Demo

```bash
./scripts/demo.sh
```

Expected proof points:

- Clean packet: `PASS`
- Stale text value: `RETURN_FOR_REVISION`
- Stale source version: `BLOCK_RELEASE`
- Failed-claim register written to `artifacts/failed_claims.json`
- Review decision written to `artifacts/review_decision.md`
- Evaluation report written to `artifacts/evaluation_report.json`
- Self-comparison guard: `PASS`

## Run Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Scope

In scope:

- Structured synthetic claim packets.
- Deterministic checks for metric values, trend direction, source version, chart/text consistency, and required caveats.
- Generated artifacts and evaluation report.
- Reviewer-fast local demo.

Out of scope:

- Free-form document parsing.
- Live LLM judgment.
- Dashboard UI.
- Production deployment.
- Real WTCHP data or official public-health claims.

## Project Shape

```text
configs/claim_rules.json
data/synthetic/source_metrics.csv
data/synthetic/brief_packets.csv
src/decision_brief_gate/
tests/
scripts/demo.sh
docs/reviewer_walkthrough.md
docs/case_study.md
artifacts/
```

The core interview story: I built the gate that stops a leadership brief when the prose no longer matches the data, chart, source snapshot, or required caveat.

