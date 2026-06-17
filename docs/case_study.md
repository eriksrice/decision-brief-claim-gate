# Case Study

## Problem

Analytics teams often release leadership-facing briefs that combine prose, charts, caveats, and source-data snapshots. A brief can be well written and still be wrong: the text can carry a stale metric, the chart can lag behind the source table, the caveat can disappear, or the claim can reference an old snapshot.

This project builds a deterministic gate for that failure mode. It blocks or returns synthetic public-health decision-brief packets when their structured claims no longer match the evidence.

This is a synthetic public-safe portfolio project. It does not contain real WTCHP data, records, documents, people, or official claims.

## Design Choice: Structured Claims First

The most important scope decision is to avoid free-form document parsing in v1. Free-form parsing would make the project look more magical but less trustworthy. The stronger senior signal is the evidence contract:

- What claim is being made?
- Which source metric supports it?
- Which source snapshot is current?
- What chart value is shown?
- What value appears in the brief text?
- Is a caveat required?
- What release decision follows from the evidence?

That contract makes the gate deterministic, testable, and reviewer-fast.

## Architecture

Inputs:

- `data/synthetic/source_metrics.csv`: canonical synthetic source metric snapshot.
- `data/synthetic/brief_packets.csv`: structured synthetic claim rows.
- `configs/claim_rules.json`: current source version, tolerance, and failure policies.

Core modules:

- `data_contracts.py`: validates CSV and config contracts.
- `checks.py`: runs deterministic claim checks.
- `gate.py`: aggregates claim failures into packet-level release decisions.
- `evaluation.py`: compares expected and predicted statuses and probes self-comparison failure.
- `artifacts.py`: writes audit, failed-claim, decision, and evaluation artifacts.
- `cli.py`: exposes the local proof path.

Outputs:

- `artifacts/brief_claim_consistency_audit.csv`
- `artifacts/failed_claims.json`
- `artifacts/review_decision.md`
- `artifacts/evaluation_report.json`

## Failure Modes Tested

The synthetic demo includes six packet-level cases:

| Packet | Expected Decision | Failure Mode |
|---|---|---|
| `PKT_CLEAN` | `PASS` | No seeded issue. |
| `PKT_STALE_TEXT` | `RETURN_FOR_REVISION` | Text value does not match source value. |
| `PKT_STALE_CHART` | `RETURN_FOR_REVISION` | Chart value disagrees with text and source. |
| `PKT_MISSING_CAVEAT` | `RETURN_FOR_REVISION` | Required caveat is absent. |
| `PKT_STALE_SOURCE` | `BLOCK_RELEASE` | Claim references old source snapshot. |
| `PKT_WRONG_TREND` | `RETURN_FOR_REVISION` | Stated trend disagrees with source-derived trend. |

The block rule is intentionally stricter for stale source versions: a packet tied to the wrong source snapshot is not ready for release.

## Evaluation

The demo compares predicted release decisions against expected review statuses across all seeded packets.

Current result:

- Packet count: 6
- Correct count: 6
- Accuracy: 1.0
- Status counts: 1 `PASS`, 4 `RETURN_FOR_REVISION`, 1 `BLOCK_RELEASE`
- Self-comparison guard: `PASS`

The self-comparison guard addresses a subtle evaluation risk: an evaluator can look perfect if it compares expected labels to themselves. The guard includes a probe that simulates copied expected-label predictions and confirms that the evaluator rejects the pattern.

## Demo

Run:

```bash
./scripts/demo.sh
```

The demo writes artifacts and prints:

```text
Clean packet: PASS
Seeded stale text packet: RETURN_FOR_REVISION
Seeded stale source version packet: BLOCK_RELEASE
Evaluation: PASS
Self-comparison guard: PASS
```

## Senior Signal

This project is intentionally narrow. Its signal is not breadth; it is judgment:

- A synthetic data contract that makes release risk inspectable.
- Deterministic checks with explicit failure statuses.
- Artifact generation rather than hand-written proof.
- Evaluation that separates expected and predicted labels.
- Reviewer docs that expose the exact contradiction fields.
- Clear non-goals around real data, live LLM judgment, dashboards, and official public-health claims.

## Limitations

- V1 assumes claims are already structured.
- V1 does not parse PDF, Word, slide, or dashboard text.
- V1 does not use an LLM.
- V1 uses a compact synthetic dataset.
- V1 does not model complex approval workflows.

These are deliberate limits. They keep the first version deterministic and auditable.

## Future Extensions

- Add optional claim extraction after the structured v1 is proven.
- Add a P061 extension that applies claim regression to forecast-release briefs.
- Add a release evidence ledger inspired by WTV33-004.
- Add richer synthetic scenarios with more claim types and caveat policies.

