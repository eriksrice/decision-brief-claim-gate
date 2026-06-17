# Decision Brief Claim Consistency Gate

Deterministic release gate for synthetic public-health decision briefs. It blocks a brief when structured claims, chart values, source snapshots, or required caveats no longer match the evidence.

## Reviewer Snapshot

- **Problem:** leadership-facing analytics briefs can carry stale values, chart/text mismatches, old source snapshots, or missing caveats even when they read cleanly.
- **System:** a local Python CLI that treats each brief claim as an evidence-bound release artifact.
- **Proof:** `./scripts/demo.sh` generates audit, failed-claim, review-decision, and evaluation artifacts from synthetic data.
- **Evaluation:** 6 seeded packets, 11 tests, expected-vs-predicted review-status comparison, and a self-comparison guard.
- **Boundary:** no real WTCHP data, no official claims, no dashboard, no free-form parsing, no live LLM judgment.

The senior signal is the release-control pattern: explicit data contracts, deterministic checks, generated proof artifacts, and honest failure boundaries.

## Why This Exists

Leadership-facing analytics briefs can look polished while carrying stale values, chart/text mismatches, old source snapshots, or missing caveats. This project treats brief claims as evidence-bound release artifacts: every claim must reconcile with its source metric, chart value, source version, and caveat rule before release.

This is a synthetic portfolio project. It uses no real WTCHP data, records, reports, people, or official claims.

## Quick Demo

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

Generated proof points:

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
docs/interview_walkthrough.md
docs/case_study.md
ROADMAP.md
artifacts/
```

The core interview story: I built the gate that stops a leadership brief when the prose no longer matches the data, chart, source snapshot, or required caveat.

## Reviewer Docs

- [Reviewer walkthrough](docs/reviewer_walkthrough.md)
- [Interview walkthrough](docs/interview_walkthrough.md)
- [Case study](docs/case_study.md)
- [Roadmap](ROADMAP.md)
