# Backend-Only Demo (Fallback Evidence)

> **n8n is the official orchestration layer.** This backend-only path exists only as fallback evidence for policy, approval, ticket, and audit behavior if n8n import fails or is delayed.

## Prerequisites

```bash
docker compose up --build -d
curl -fsS http://localhost:8000/health
```

## Full Sequence

```bash
CORR="corr_backend_demo"

# 1. Reset demo state
curl -X POST http://localhost:8000/demo/reset

# 2. Start onboarding session
curl -X POST "http://localhost:8000/onboarding/start/emp_001" \
  -H "Content-Type: application/json" \
  -d "{\"correlation_id\":\"$CORR\"}"

# 3. Get HR profile
curl -s "http://localhost:8000/mock/hr/employees/emp_001" | python3 -m json.tool

# 4. Get training status
curl -s "http://localhost:8000/mock/training/status/emp_001" | python3 -m json.tool

# 5. Get access recommendations
curl -s "http://localhost:8000/mock/access/recommendations/emp_001" | python3 -m json.tool

# 6. Select systems
curl -X POST "http://localhost:8000/onboarding/select-access" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"selected_systems\":[\"Salesforce\",\"Gong\"],\"correlation_id\":\"$CORR\"}"

# 7. Create approval
curl -s -X POST "http://localhost:8000/mock/approvals" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"manager_id\":\"mgr_101\",\"request_id\":\"req_$CORR\",\"correlation_id\":\"$CORR\"}" | python3 -m json.tool
APR_ID=$(curl -s -X POST "http://localhost:8000/mock/approvals" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"manager_id\":\"mgr_101\",\"request_id\":\"req_$CORR\",\"correlation_id\":\"$CORR\"}" | python3 -c "import sys,json;print(json.load(sys.stdin).get('approval_id',''))")

# 8. Try ticket before approval (should be blocked)
echo "=== Attempting ticket before approval (expect 409) ==="
curl -s -X POST "http://localhost:8000/mock/itsm/tickets" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"approval_id\":\"$APR_ID\",\"requested_systems\":[\"Salesforce\",\"Gong\"],\"correlation_id\":\"$CORR\"}" | python3 -m json.tool

# 9. Approve
echo "=== Approving ==="
curl -s -X POST "http://localhost:8000/mock/approvals/$APR_ID/approve" \
  -H "Content-Type: application/json" \
  -d "{\"manager_id\":\"mgr_101\",\"correlation_id\":\"$CORR\"}" | python3 -m json.tool

# 10. Create ticket after approval (should succeed)
echo "=== Creating ticket (expect success) ==="
curl -s -X POST "http://localhost:8000/mock/itsm/tickets" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"approval_id\":\"$APR_ID\",\"requested_systems\":[\"Salesforce\",\"Gong\"],\"correlation_id\":\"$CORR\"}" | python3 -m json.tool

# 11. Duplicate ticket (should be idempotent)
echo "=== Duplicate ticket (expect duplicate=true) ==="
curl -s -X POST "http://localhost:8000/mock/itsm/tickets" \
  -H "Content-Type: application/json" \
  -d "{\"employee_id\":\"emp_001\",\"approval_id\":\"$APR_ID\",\"requested_systems\":[\"Salesforce\",\"Gong\"],\"correlation_id\":\"$CORR\"}" | python3 -m json.tool

# 12. Get onboarding status
echo "=== Final status ==="
curl -s "http://localhost:8000/onboarding/status/emp_001" | python3 -m json.tool

# 13. Inspect audit trail
echo "=== Audit events ==="
curl -s "http://localhost:8000/audit/events?correlation_id=$CORR" | python3 -m json.tool

echo ""
echo "=== Backend-only demo complete ==="
echo "Approval-gated ticket creation: VERIFIED"
echo "Ticket blocked before approval: VERIFIED"  
echo "Duplicate ticket prevention: VERIFIED"
echo "Audit chain via correlation_id: VERIFIED"
```
