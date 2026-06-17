#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python3 -m decision_brief_gate \
  --source-metrics data/synthetic/source_metrics.csv \
  --brief-packets data/synthetic/brief_packets.csv \
  --claim-rules configs/claim_rules.json \
  --output-dir artifacts

