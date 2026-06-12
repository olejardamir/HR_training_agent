#!/usr/bin/env bash
set -euo pipefail

BASE="${API_BASE_URL:-http://localhost:8000}"
CORR="smoke_pending_$(date +%s)"

echo "=== Smoke: Pending Path (no approval -> no ticket) ==="

echo "1. Start onboarding"
curl -fsS -X POST "$BASE/onboarding/start/emp_001" \
  -H "Content-Type: application/json" \
  -d "{\"correlation_id\":\"$CORR\"}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='STARTED'"

echo "2. Select access"
REQ_ID=$(curl -fsS -X POST "$BASE/onboarding/select-access" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"selected_systems\":[\"Salesforce\"],\"correlation_id\":\"$CORR\",\"source\":\"test\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['request_id'])")

echo "3. Create approval (no approve call)"
APPROVAL_ID=$(curl -fsS -X POST "$BASE/mock/approvals" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"request_id\":\"$REQ_ID\",\"manager_id\":\"mgr_101\",\"correlation_id\":\"$CORR\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['approval_id'])")

echo "4. Try ticket before approval (should be 409 with pre_approval_blocked=true)"
curl -s -X POST "$BASE/mock/itsm/tickets" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"approval_id\":\"$APPROVAL_ID\",\"requested_systems\":[\"Salesforce\"],\"requested_by\":\"test\",\"idempotency_key\":\"pkey_$CORR\",\"correlation_id\":\"$CORR\"}" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
if 'detail' in d:
    d = d['detail']
assert d.get('status')=='BLOCKED', f'expected BLOCKED, got {d}'
assert d.get('pre_approval_blocked')==True, f'expected pre_approval_blocked=True'
assert d.get('ticket_created')==False, f'expected ticket_created=False'
assert d.get('reason_code')=='MANAGER_APPROVAL_REQUIRED', f'expected MANAGER_APPROVAL_REQUIRED, got {d}'
"
echo "   Got 409 with pre_approval_blocked=true, ticket_created=false"

echo "5. Verify audit contains ticket_blocked"
curl -fsS "$BASE/audit/events?correlation_id=$CORR" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert any(e['action']=='ticket_blocked' for e in d['events']), 'ticket_blocked event not found'"
echo "   Audit ticket_blocked found"

echo ""
echo "=== PENDING PATH PASSED ==="
