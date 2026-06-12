#!/usr/bin/env bash
set -euo pipefail

echo "=== Collect Evidence Manifest ==="
echo ""

PASS=0
FAIL=0

check() {
  local name="$1"
  shift
  echo -n "$name... "
  if "$@" > /dev/null 2>&1; then
    echo "pass"
    PASS=$((PASS + 1))
  else
    echo "fail"
    FAIL=$((FAIL + 1))
  fi
}

echo "1. Infrastructure"
check "Docker compose config" docker compose config -q
check "API health" curl -fsS http://localhost:8000/health
check "API ready" curl -fsS http://localhost:8000/ready

echo ""
echo "2. Backend tests"
check "Pytest" docker compose exec -T api pytest -q

echo ""
echo "3. Static validation"
check "No collapsed files" python3 scripts/validate_no_collapsed_files.py
check "No secrets" python3 scripts/validate_no_secrets.py
check "Workflow contract (static)" python3 scripts/validate_workflow_contract.py
check "Workflow contract (negative)" python3 scripts/validate_workflow_contract.py --negative

echo ""
echo "4. FastAPI smoke tests"
check "Happy path" bash scripts/smoke_happy_path.sh
check "Pending path" bash scripts/smoke_pending_path.sh
check "Reject path" bash scripts/smoke_reject_path.sh
check "Forbidden path" bash scripts/smoke_forbidden_path.sh
check "LLM fallback" bash scripts/smoke_llm_fallback.sh

echo ""
echo "5. n8n webhook smoke tests"
check "n8n happy path" bash scripts/smoke_n8n_happy_path.sh
check "n8n reject path" bash scripts/smoke_n8n_reject_path.sh
check "n8n pending path" bash scripts/smoke_n8n_pending_path.sh
check "n8n expire path" bash scripts/smoke_n8n_expire_path.sh
check "n8n wrong manager path" bash scripts/smoke_n8n_wrong_manager_path.sh
check "n8n forbidden path" bash scripts/smoke_n8n_forbidden_path.sh

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
