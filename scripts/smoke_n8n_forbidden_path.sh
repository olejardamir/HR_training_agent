#!/usr/bin/env bash
set -euo pipefail

N8N_BASE="${N8N_BASE_URL:-http://localhost:5678}"
API_BASE="${API_BASE_URL:-http://localhost:8000}"
CORR="n8n_forbid_$(date +%s)"

echo "=== Smoke: n8n Forbidden Path ==="
echo ""

echo "1. n8n health check"
HEALTH=$(curl -fsS "$N8N_BASE/healthz")
echo "$HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('status')=='ok'"
echo "   ok"

echo ""
echo "2. Trigger n8n webhook with forbidden system (Payroll Admin)"
RESULT=$(curl -s -w "\n%{http_code}" -X POST "$N8N_BASE/webhook/hr-onboarding/new-hire" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"selected_systems\":[\"Salesforce\",\"Payroll Admin\"],\"approval_action\":\"approve\",\"correlation_id\":\"$CORR\"}")
BODY=$(echo "$RESULT" | sed '$d')
HTTP_CODE=$(echo "$RESULT" | tail -1)

echo "   HTTP code: $HTTP_CODE"
if [ "$HTTP_CODE" != "200" ]; then
  echo "FAIL: Expected HTTP 200, got $HTTP_CODE"
  exit 1
fi

echo "$BODY" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('forbidden') == True, f'expected forbidden=True, got {d}'
assert d.get('ticket_created') == False, f'expected ticket_created=False, got {d}'
assert d.get('approval_status') == 'FORBIDDEN', f'expected approval_status=FORBIDDEN, got {d}'
assert d.get('ticket_id') is None, f'expected ticket_id=null, got {d}'
assert d.get('audit_event_count', 0) > 0, f'expected audit_event_count > 0, got {d}'
ci = d.get('correlation_id', '')
assert ci == '$CORR', f'expected correlation_id=$CORR, got {ci}'
print(f'   forbidden=True, approval_status=FORBIDDEN, ticket_created=False, correlation_id={\"$CORR\"} ')
"

echo ""
echo "3. Verify audit trail via correlation_id"
AUDIT=$(curl -fsS "$API_BASE/audit/events?correlation_id=$CORR")
echo "$AUDIT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
events = d.get('events', [])
blocked = [e for e in events if e.get('action') == 'selection_blocked']
approved = [e for e in events if e.get('action') == 'approval_requested']
tickets = [e for e in events if e.get('action') == 'ticket_created']
assert len(blocked) >= 1, f'expected at least one selection_blocked event, got {len(blocked)}'
assert len(approved) == 0, f'expected no approval_requested event, got {len(approved)}'
assert len(tickets) == 0, f'expected no ticket_created event, got {len(tickets)}'
print(f'   selection_blocked={len(blocked)}, approval_requested={len(approved)}, ticket_created={len(tickets)}')
"

echo ""
echo "=== N8N FORBIDDEN PATH SMOKE PASSED ==="
