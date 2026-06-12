# Claim-to-Evidence Audit

| Claim | Evidence |
|---|---|
| Runs locally on Linux | `docker compose up --build -d` + `curl localhost:8000/health` |
| Requires no paid SaaS credentials | No API keys in `.env.example`; all mocks stateful in PostgreSQL |
| Uses n8n as visible workflow orchestrator | `n8n/hr_onboarding_workflow.json` + `scripts/smoke_n8n_*.sh` |
| FastAPI mocks HR, Slack, Training, Salesforce, ITSM | `api/app/routers/` contains endpoints for all five |
| PostgreSQL stores state and audit logs | `api/app/models.py` defines all tables |
| Ollama or fallback generates messages | `api/app/services/llm_service.py` + `scripts/smoke_llm_fallback.sh` |
| LLM does not authorize access | LLM only called for summary messages; no approval/selection routes touch LLM |
| Role/level come from HR source-of-truth mock | `GET /mock/hr/employees/{employee_id}` |
| Recommendations use role-level policy and peer patterns | `api/app/logic/access_recommender.py` |
| Forbidden systems are blocked | `test_forbidden_system_returns_403` + `scripts/smoke_forbidden_path.sh` |
| Manager approval is required before ticket creation | `test_itsm_ticket_blocked_before_approval_returns_409_with_blocked` |
| Pending/rejected/expired approvals block ticket creation | `test_approval_gate.py` tests for each |
| Wrong manager cannot approve | `test_wrong_manager_cannot_approve` |
| Duplicate tickets are prevented | `test_itsm_ticket_idempotent_request_returns_duplicate` |
| Audit trail uses correlation ID | `GET /audit/events?correlation_id=...` |
| n8n workflow matches backend contract | `scripts/validate_workflow_contract.py` (static + 24 negative tests) |
| Tests pass | `docker compose exec -T api pytest -q` (84 tests) |
| OpenAPI endpoint contract conforms | `scripts/validate_openapi_contract.py` |
| Edge cases covered | `docs/edge_case_coverage_audit.md` (15 edge cases) |
| Smoke scripts pass | `scripts/smoke_*.sh` all pass |
| Evidence manifest is commit-fresh | `scripts/validate_evidence_manifest_freshness.py` |
