#!/usr/bin/env bash
set -euo pipefail

N8N_BASE="${N8N_BASE_URL:-http://localhost:5678}"
echo "=== Smoke: n8n Webhook Wrong Manager Path ==="

echo "1. n8n health check"
HEALTH=$(curl -fsS "$N8N_BASE/healthz")
echo "$HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('status')=='ok'"
echo "   ok"

echo "2. Post to webhook /webhook/hr-onboarding/new-hire (wrong_manager path)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$N8N_BASE/webhook/hr-onboarding/new-hire" \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"emp_001","selected_systems":["Salesforce"],"approval_action":"wrong_manager"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "   HTTP $HTTP_CODE"
if [ "$HTTP_CODE" != "200" ]; then
    echo "Expected HTTP 200, got $HTTP_CODE"
    echo "Body: $BODY"
    exit 1
fi

echo "$BODY" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d.get('ok') is True, 'ok must be true'
assert d.get('pre_approval_blocked') is True, 'pre_approval_blocked must be true'
assert d.get('ticket_created') is False, 'ticket_created must be false on wrong_manager'
assert d.get('ticket_id') is None, f'ticket_id must be null on wrong_manager, got {d.get(\"ticket_id\")!r}'
assert d.get('demo_status') == 'COMPLETED_NO_TICKET', f'expected COMPLETED_NO_TICKET, got {d.get(\"demo_status\")}'
assert d.get('approval_status') == 'PENDING', f'expected PENDING (wrong manager: approval unchanged), got {d.get(\"approval_status\")}'
print(f'   ok=true, approval_status=PENDING (wrong manager blocked), ticket_created=false')
print(f'   demo_status=COMPLETED_NO_TICKET')
"

echo "=== N8N WEBHOOK WRONG MANAGER SMOKE PASSED ==="
