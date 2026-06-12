#!/usr/bin/env bash
set -euo pipefail

BASE="${API_BASE_URL:-http://localhost:8000}"
CORR="smoke_forbid_$(date +%s)"

echo "=== Smoke: Forbidden Path (selecting forbidden system -> 403) ==="

echo "1. Start onboarding"
curl -fsS -X POST "$BASE/onboarding/start/emp_001" \
  -H "Content-Type: application/json" \
  -d "{\"correlation_id\":\"$CORR\"}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='STARTED'"

echo "2. Try to select Payroll Admin (forbidden for Account Executive L2)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/onboarding/select-access" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"selected_systems\":[\"Payroll Admin\"],\"correlation_id\":\"$CORR\",\"source\":\"test\"}")
if [ "$STATUS" != "403" ]; then
  echo "FAIL: Expected 403, got $STATUS"
  exit 1
fi
echo "   Got 403 as expected"

echo "3. Verify audit event for forbidden selection"
curl -fsS "$BASE/audit/events?correlation_id=$CORR" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert any(e['action']=='selection_blocked' for e in d['events']); assert any(e.get('reason_code')=='FORBIDDEN_SYSTEM_SELECTED' for e in d['events'])"
echo "   Audit event found"

echo "4. Verify no approval and no ticket were created"
curl -fsS "$BASE/audit/events?correlation_id=$CORR" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert not any(e['action']=='ticket_created' for e in d['events']), 'ticket_created should not exist'; assert not any(e['action']=='approval_requested' for e in d['events']), 'approval_requested should not exist'"
echo "   No ticket or approval created"

echo ""
echo "=== FORBIDDEN PATH PASSED ==="
