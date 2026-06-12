#!/usr/bin/env bash
set -euo pipefail

N8N_BASE="${N8N_BASE_URL:-http://localhost:5678}"
WF_FILE="${1:-n8n/hr_onboarding_workflow.json}"

echo "=== n8n Workflow Import ==="
echo ""

if [ ! -f "$WF_FILE" ]; then
  echo "ERROR: Workflow file not found: $WF_FILE"
  exit 1
fi

echo "1. Checking n8n health..."
HEALTH=$(curl -fsS "$N8N_BASE/healthz" 2>/dev/null || true)
if [ -z "$HEALTH" ]; then
  echo "   n8n not reachable at $N8N_BASE"
  echo "   Make sure Docker stack is running: docker compose up --build -d"
  exit 1
fi
echo "   $HEALTH"

echo ""
echo "2. Importing workflow via n8n CLI..."
# Strip id and tags fields which cause SQLite NOT NULL constraint failures on import
TMP_FILE=$(mktemp)
python3 -c "
import json
wf = json.load(open('$WF_FILE'))
wf.pop('id', None)
wf.pop('tags', None)
json.dump(wf, open('$TMP_FILE', 'w'), indent=2)
" < /dev/null

WF_ID=$(docker compose exec -T n8n n8n import:workflow --input=/dev/stdin < "$TMP_FILE" 2>/dev/null | grep -oP 'Successfully imported \K\d+' || echo "")
rm -f "$TMP_FILE"

if [ -z "$WF_ID" ]; then
  echo "   CLI import output format unknown; checking for latest workflow..."
else
  echo "   Imported workflow count: $WF_ID"
fi

echo ""
echo "3. Finding the newly imported workflow..."
IMPORTED_ID=$(docker compose exec -T n8n sh -c 'n8n export:workflow --all --pretty 2>/dev/null' 2>/dev/null | python3 -c "
import sys, json
lines = sys.stdin.read()
start = lines.find('[')
if start >= 0: lines = lines[start:]
data = json.loads(lines)
data.sort(key=lambda w: w.get('createdAt', ''), reverse=True)
print(data[0]['id'])
" 2>/dev/null || echo "")

if [ -z "$IMPORTED_ID" ]; then
  echo "   WARNING: Could not determine imported workflow ID"
  echo "   Import may have failed. Check: docker compose logs n8n"
  exit 1
fi
echo "   Workflow ID: $IMPORTED_ID"

echo ""
echo "4. Activating workflow..."
ACTIVATE_OUTPUT=$(docker compose exec n8n n8n update:workflow --id="$IMPORTED_ID" --active=true 2>/dev/null || true)
if echo "$ACTIVATE_OUTPUT" | grep -q "Error"; then
  echo "   Activation requires n8n restart (will restart now)..."
  docker compose restart n8n
  sleep 5
  echo "   n8n restarted."
else
  echo "   $ACTIVATE_OUTPUT"
  docker compose restart n8n
  sleep 5
fi

echo ""
echo "5. Verifying workflow is active..."
ACTIVE_CHECK=$(docker compose exec -T n8n sh -c 'n8n export:workflow --all --pretty 2>/dev/null' 2>/dev/null | python3 -c "
import sys, json
lines = sys.stdin.read()
start = lines.find('[')
if start >= 0: lines = lines[start:]
data = json.loads(lines)
for w in data:
    if w['id'] == '$IMPORTED_ID':
        print(f'active={w.get(\"active\")}')
        break
" 2>/dev/null || echo "unknown")

echo "   Status: $ACTIVE_CHECK"

echo ""
echo "6. Webhook URL:"
echo "   POST $N8N_BASE/webhook/hr-onboarding/new-hire"
echo "   Content-Type: application/json"
echo '   {"employee_id":"emp_001","selected_systems":["Salesforce","Gong"],"approval_action":"approve","correlation_id":"corr_import_test"}'
echo ""
echo "=== n8n workflow import complete ==="
