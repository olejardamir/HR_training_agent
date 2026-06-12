#!/usr/bin/env bash
set -euo pipefail

echo "=== Collect Evidence Manifest ==="
echo ""

echo "1. Docker compose config..."
docker compose config -q && echo "   pass" || echo "   fail"

echo "2. API health..."
curl -fsS http://localhost:8000/health > /dev/null && echo "   pass" || echo "   fail"

echo "3. API ready..."
curl -fsS http://localhost:8000/ready > /dev/null && echo "   pass" || echo "   fail"

echo "4. Pytest..."
docker compose exec api pytest -q && echo "   pass" || echo "   fail"

echo "5. No collapsed files..."
python3 scripts/validate_no_collapsed_files.py && echo "" || true

echo "6. No secrets..."
python3 scripts/validate_no_secrets.py && echo "" || true

echo "7. Workflow contract..."
python3 scripts/validate_workflow_contract.py && echo "" || true

echo "8. Smoke happy path..."
bash scripts/smoke_happy_path.sh && echo "   pass" || echo "   fail"

echo "9. Smoke pending path..."
bash scripts/smoke_pending_path.sh && echo "   pass" || echo "   fail"

echo "10. Smoke reject path..."
bash scripts/smoke_reject_path.sh && echo "   pass" || echo "   fail"

echo "11. Smoke forbidden path..."
bash scripts/smoke_forbidden_path.sh && echo "   pass" || echo "   fail"

echo "12. Smoke LLM fallback..."
bash scripts/smoke_llm_fallback.sh && echo "   pass" || echo "   fail"

echo ""
echo "=== Evidence collection complete. Run generate_evidence_manifest.py to write manifest. ==="
