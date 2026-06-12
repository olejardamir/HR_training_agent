#!/usr/bin/env bash
set -euo pipefail

BASE="${API_BASE_URL:-http://localhost:8000}"

echo "=== Smoke: LLM Fallback ==="

echo "1. Employee onboarding summary (no Ollama)"
curl -fsS -X POST "$BASE/mock/llm/messages" \
  -H "Content-Type: application/json" \
  -d '{"message_type":"employee_onboarding_summary","employee_id":"emp_001","correlation_id":"smoke_llm_1","context":{"employee_name":"Maya Chen","role":"Account Executive","level":"L2","training_summary":"All complete","recommended_systems_list":"Salesforce, Gong","manager_name":"Manager"}}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'message' in d; assert d['llm_provider'] in ('ollama','fallback')"
echo "   Employee summary OK"

echo "2. Manager approval request"
curl -fsS -X POST "$BASE/mock/llm/messages" \
  -H "Content-Type: application/json" \
  -d '{"message_type":"manager_approval_request","employee_id":"emp_001","correlation_id":"smoke_llm_2","context":{"manager_name":"Alice","employee_name":"Maya","role":"Account Executive","level":"L2","selected_systems_list":"Salesforce","correlation_id":"corr_123","request_id":"req_456"}}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'message' in d; assert 'Salesforce' in d['message'] or 'access' in d['message']"
echo "   Manager request OK"

echo "3. Fallback with empty context"
curl -fsS -X POST "$BASE/mock/llm/messages" \
  -H "Content-Type: application/json" \
  -d '{"message_type":"employee_onboarding_summary","employee_id":"emp_002","correlation_id":"smoke_llm_3","context":{}}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'message' in d"
echo "   Empty context OK"

echo ""
echo "=== LLM FALLBACK PASSED ==="
