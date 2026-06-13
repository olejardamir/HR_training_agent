#!/usr/bin/env bash
set -euo pipefail

PASS=0
FAIL=0

check() {
  local name="$1"; shift
  echo -n "  $name... "
  if "$@" > /dev/null 2>&1; then
    echo "pass"; PASS=$((PASS+1))
  else
    echo "FAIL"; FAIL=$((FAIL+1))
  fi
}

echo "=== Full Verification Suite ==="
echo ""

echo "--- Infrastructure ---"
check "docker compose config" docker compose config -q
check "API health" curl -fsS http://localhost:8000/health
check "API ready" curl -fsS http://localhost:8000/ready
check "API version" curl -fsS http://localhost:8000/version

echo ""
echo "--- Backend Tests ---"
check "pytest (all)" docker compose exec -T api pytest -q

echo ""
echo "--- Static Validation ---"
check "Workflow contract (static)" python3 scripts/validate_workflow_contract.py
check "Workflow contract (negative)" python3 scripts/validate_workflow_contract.py --negative
check "OpenAPI contract" python3 scripts/validate_openapi_contract.py
check "No collapsed files" python3 scripts/validate_no_collapsed_files.py
check "No secrets" python3 scripts/validate_no_secrets.py
check "Evidence freshness" python3 scripts/validate_evidence_manifest_freshness.py

echo ""
echo "--- Mini-RAG ---"
check "build mini-rag index" bash scripts/build_rag_index.sh
check "mini-rag agent chat" curl -fsS -X POST http://localhost:8000/agent/chat -H "Content-Type: application/json" -d '{"employee_id":"emp_001","message":"What do I need to do for T2?"}' > /dev/null
check "mini-rag smoke" bash scripts/smoke_agent_chat_rag.sh

echo ""
echo "--- Direct FastAPI Smokes ---"
check "Happy path" bash scripts/smoke_happy_path.sh
check "Pending path" bash scripts/smoke_pending_path.sh
check "Reject path" bash scripts/smoke_reject_path.sh
check "Forbidden path" bash scripts/smoke_forbidden_path.sh
check "LLM fallback" bash scripts/smoke_llm_fallback.sh

echo ""
echo "--- n8n Webhook Smokes (requires imported + active workflow) ---"
if bash scripts/import_n8n_workflow.sh > /dev/null 2>&1; then
  echo "  Waiting for n8n to be ready..."
  for i in $(seq 1 30); do
    if curl -fsS http://localhost:5678/healthz > /dev/null 2>&1; then
      echo "  n8n ready after ${i}s"
      break
    fi
    sleep 1
  done
  check "n8n happy path" bash scripts/smoke_n8n_happy_path.sh
  sleep 2
  curl -fsS -X POST http://localhost:8000/demo/reset > /dev/null 2>&1 || true
  check "n8n reject path" bash scripts/smoke_n8n_reject_path.sh
  sleep 2
  curl -fsS -X POST http://localhost:8000/demo/reset > /dev/null 2>&1 || true
  check "n8n pending path" bash scripts/smoke_n8n_pending_path.sh
  sleep 2
  curl -fsS -X POST http://localhost:8000/demo/reset > /dev/null 2>&1 || true
  check "n8n expire path" bash scripts/smoke_n8n_expire_path.sh
  sleep 2
  curl -fsS -X POST http://localhost:8000/demo/reset > /dev/null 2>&1 || true
  check "n8n wrong manager path" bash scripts/smoke_n8n_wrong_manager_path.sh
  sleep 2
  curl -fsS -X POST http://localhost:8000/demo/reset > /dev/null 2>&1 || true
  check "n8n forbidden path" bash scripts/smoke_n8n_forbidden_path.sh
else
  if [ "${ALLOW_MANUAL_N8N_IMPORT:-false}" = "true" ]; then
    echo "  WARNING: n8n workflow import failed; manual import mode explicitly allowed."
    echo "  Manual import evidence must be documented in docs/final_verification_report.md."
  else
    echo "  n8n workflow import... FAIL"
    FAIL=$((FAIL+1))
  fi
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] || exit 1
