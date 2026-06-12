#!/usr/bin/env bash
set -euo pipefail

BASE="${API_BASE_URL:-http://localhost:8000}"
CORR="smoke_happy_$(date +%s)"

echo "=== Smoke: Happy Path (approve -> ticket created) ==="

echo "1. Demo reset"
curl -fsS -X POST "$BASE/demo/reset" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['ok'] is True"

echo "2. Health check"
curl -fsS "$BASE/health" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='healthy'"

echo "3. Readiness check"
curl -fsS "$BASE/ready" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='ready'"

echo "4. Version check"
curl -fsS "$BASE/version" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'version' in d"

echo "5. HR profile lookup"
curl -fsS "$BASE/mock/hr/employees/emp_001/profile" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['employee_id']=='emp_001'; assert 'profile_status' in d"

echo "6. Training status"
curl -fsS "$BASE/mock/training/status/emp_001" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['employee_id']=='emp_001'"

echo "7. Salesforce profile"
curl -fsS "$BASE/mock/salesforce/profile/emp_001" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'employee_id' in d"

echo "8. Access recommendations"
curl -fsS "$BASE/mock/access/recommendations/emp_001" | python3 -c "import sys,json; d=json.load(sys.stdin); assert len(d['recommendations'])>0"

echo "9. Start onboarding"
curl -fsS -X POST "$BASE/onboarding/start/emp_001" \
  -H "Content-Type: application/json" \
  -d "{\"correlation_id\":\"$CORR\"}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='STARTED'"

echo "10. Select access (valid)"
REQ_ID=$(curl -fsS -X POST "$BASE/onboarding/select-access" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"selected_systems\":[\"Salesforce\",\"Gong\"],\"correlation_id\":\"$CORR\",\"source\":\"test\"}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='EMPLOYEE_SELECTED'; print(d['request_id'])")

echo "11. Create approval"
APPROVAL_ID=$(curl -fsS -X POST "$BASE/mock/approvals" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"request_id\":\"$REQ_ID\",\"manager_id\":\"mgr_101\",\"correlation_id\":\"$CORR\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['approval_id'])")

echo "12. Try ticket before approval (should block with 409 + pre_approval_blocked=true)"
RESULT=$(curl -s -w "\n%{http_code}" -X POST "$BASE/mock/itsm/tickets" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"approval_id\":\"$APPROVAL_ID\",\"requested_systems\":[\"Salesforce\",\"Gong\"],\"requested_by\":\"test\",\"idempotency_key\":\"prekey_$CORR\",\"correlation_id\":\"$CORR\"}")
HTTP_CODE=$(echo "$RESULT" | tail -1)
BODY=$(echo "$RESULT" | sed '$d')
if [ "$HTTP_CODE" != "409" ]; then
  echo "FAIL: Expected HTTP 409 for blocked ticket, got $HTTP_CODE"
  exit 1
fi
echo "$BODY" | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert d['pre_approval_blocked']==True, f'expected pre_approval_blocked=True, got {d}'
assert d['ticket_created']==False, f'expected ticket_created=False'
assert d['reason_code']=='MANAGER_APPROVAL_REQUIRED', f'reason_code not MANAGER_APPROVAL_REQUIRED in {d}'
print(f'   HTTP 409, pre_approval_blocked=true, ticket_created=false')
"

echo "13. Manager approves"
curl -fsS -X POST "$BASE/mock/approvals/$APPROVAL_ID/approve" \
  -H "Content-Type: application/json" \
  -d "{\"decided_by\":\"mgr_101\",\"decision_reason\":\"approved\",\"correlation_id\":\"$CORR\"}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='APPROVED'"

echo "14. Create ticket (should succeed)"
TICKET_ID=$(curl -fsS -X POST "$BASE/mock/itsm/tickets" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"approval_id\":\"$APPROVAL_ID\",\"requested_systems\":[\"Salesforce\",\"Gong\"],\"requested_by\":\"test\",\"idempotency_key\":\"hkey_$CORR\",\"correlation_id\":\"$CORR\"}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['ticket_created']==True; print(d['ticket_id'])")

echo "15. Check idempotency"
curl -fsS -X POST "$BASE/mock/itsm/tickets" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"approval_id\":\"$APPROVAL_ID\",\"requested_systems\":[\"Salesforce\",\"Gong\"],\"requested_by\":\"test\",\"idempotency_key\":\"hkey_$CORR\",\"correlation_id\":\"$CORR\"}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['duplicate']==True; assert d['ticket_id']=='$TICKET_ID'"

echo "16. Audit events exist"
curl -fsS "$BASE/audit/events?correlation_id=$CORR" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['ok']==True; assert d['count']>0; assert len(d['events'])>0"

echo ""
echo "=== HAPPY PATH PASSED ==="
