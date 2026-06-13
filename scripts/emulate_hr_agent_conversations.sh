#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
OUTPUT_DIR="${OUTPUT_DIR:-demo_outputs/hr_agent_conversation_logs}"

python scripts/emulate_hr_agent_conversations.py \
  --base-url "$BASE_URL" \
  --output-dir "$OUTPUT_DIR"
