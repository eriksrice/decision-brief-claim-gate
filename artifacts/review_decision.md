# Review Decision

| Packet | Brief | Expected | Predicted | Failed Claims | Total Claims |
|---|---|---|---|---:|---:|
| PKT_CLEAN | BRIEF_CLEAN | PASS | PASS | 0 | 5 |
| PKT_MISSING_CAVEAT | BRIEF_MISSING_CAVEAT | RETURN_FOR_REVISION | RETURN_FOR_REVISION | 1 | 1 |
| PKT_STALE_CHART | BRIEF_STALE_CHART | RETURN_FOR_REVISION | RETURN_FOR_REVISION | 1 | 1 |
| PKT_STALE_SOURCE | BRIEF_STALE_SOURCE | BLOCK_RELEASE | BLOCK_RELEASE | 1 | 1 |
| PKT_STALE_TEXT | BRIEF_STALE_TEXT | RETURN_FOR_REVISION | RETURN_FOR_REVISION | 1 | 1 |
| PKT_WRONG_TREND | BRIEF_WRONG_TREND | RETURN_FOR_REVISION | RETURN_FOR_REVISION | 1 | 1 |

Release rule: any `BLOCK_RELEASE` claim blocks the packet; otherwise any failed claim returns the packet for revision.
