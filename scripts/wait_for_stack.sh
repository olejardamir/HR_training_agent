#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE_URL:-http://localhost:8000}"
N8N_BASE="${N8N_BASE_URL:-http://localhost:5678}"
MAX_RETRIES=30
SLEEP=3

echo "=== Waiting for Docker stack ==="

echo -n "  PostgreSQL (via API /ready)..."
for i in $(seq 1 $MAX_RETRIES); do
  if curl -fsS "$API_BASE/ready" > /dev/null 2>&1; then
    echo " ready after ${i}s"
    break
  fi
  if [ "$i" -eq "$MAX_RETRIES" ]; then
    echo " FAILED after ${MAX_RETRIES}s"
    echo "  Try: docker compose logs postgres api"
    exit 1
  fi
  sleep "$SLEEP"
done

echo -n "  FastAPI /health..."
for i in $(seq 1 $MAX_RETRIES); do
  if curl -fsS "$API_BASE/health" > /dev/null 2>&1; then
    echo " ready after ${i}s"
    break
  fi
  if [ "$i" -eq "$MAX_RETRIES" ]; then
    echo " FAILED after ${MAX_RETRIES}s"
    exit 1
  fi
  sleep "$SLEEP"
done

echo -n "  n8n /healthz..."
for i in $(seq 1 $MAX_RETRIES); do
  if curl -fsS "$N8N_BASE/healthz" > /dev/null 2>&1; then
    echo " ready after ${i}s"
    break
  fi
  if [ "$i" -eq "$MAX_RETRIES" ]; then
    echo " FAILED after ${MAX_RETRIES}s"
    exit 1
  fi
  sleep "$SLEEP"
done

echo "=== Stack ready ==="
