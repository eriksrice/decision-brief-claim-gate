# Roadmap

This roadmap is intentionally restrained. The project is strongest when v1 remains deterministic, auditable, and reviewer-fast.

## V1 Complete

- Structured synthetic decision-brief claim packets.
- Deterministic checks for:
  - metric value mismatch
  - trend direction mismatch
  - stale source version
  - chart/text/source disagreement
  - missing required caveat
- Packet-level release decisions:
  - `PASS`
  - `RETURN_FOR_REVISION`
  - `BLOCK_RELEASE`
- Generated artifacts:
  - claim audit
  - failed-claim register
  - review decision
  - evaluation report
- Self-comparison guard.
- Local demo command.
- Unit and gate tests.
- Reviewer walkthrough and case study.

## Near-Term Polish

- Add a small architecture diagram to the README.
- Add more synthetic packets with mixed failure modes.
- Add stricter schema validation error messages.
- Add a compact `make demo` or `make test` wrapper if repeated use justifies it.

## Future Extensions

- Optional claim extraction from markdown or structured JSON brief sections.
- Forecast-release claim regression as a P061 extension.
- Release evidence ledger inspired by the portfolio tournament's WTV33-004 candidate.
- More caveat policies and source-version rules.
- Richer public-safe synthetic examples across certification, outreach, enrollment, and service-utilization reporting.

## Explicit Non-Goals

- Real WTCHP data or documents.
- Official public-health recommendations.
- Live LLM judgment as the release decision.
- Dashboard-first development.
- Production deployment.
- Multi-team workflow management.

