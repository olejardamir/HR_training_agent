# Traceability Matrix

```text
requirement -> endpoint -> service -> test -> demo evidence
```

| Requirement | Endpoint | Service/Logic | Test | Evidence |
|---|---|---|---|---|
| HR role/level lookup | `GET /mock/hr/employees/{employee_id}` | `hr.py:get_employee_profile` / `employee_service.py:get_employee` | `test_access_recommender.py:test_recommendations_for_emp_001` | HR profile returns role, level, department, manager |
| Training status (T1-T4) | `GET /mock/training/status/{employee_id}` | `training.py:get_training_status` / `training_service.py:get_training_status` | — | Demo walkthrough step 2 |
| Training status update | `PATCH /mock/training/status/{employee_id}/modules/{module_id}` | `training_service.py:update_training_module` | — | Module status can be advanced |
| Salesforce profile | `GET /mock/salesforce/profile/{employee_id}` | `salesforce.py:get_salesforce_profile` / `salesforce_service.py:get_profile` | — | Setup status returned |
| Salesforce profile update | `PATCH /mock/salesforce/profile/{employee_id}` | `salesforce_service.py:update_profile` | — | Setup status toggled |
| Role-level policy recommendations | `GET /mock/access/recommendations/{id}` | `access_recommender.py:get_access_recommendations` | `test_access_recommender.py:test_recommendations_for_emp_001` | Required, recommended, blocked systems |
| Peer-pattern reason codes | `GET /mock/access/recommendations/{id}` | `access_recommender.py:get_access_recommendations` | `test_access_recommender.py:test_department_standard_reason_code` | PEER_COMMON_ACCESS reason code and frequency |
| Forbidden system rejection | `POST /onboarding/select-access` | `onboarding.py:select_access` / `selection_service.py:validate_selection` | `test_approval_gate.py:test_access_selection_forbidden_system_returns_403` | 403 + audit BLOCKED event |
| Employee selection validation | `POST /onboarding/select-access` | `onboarding.py:select_access` / `selection_service.py:validate_selection` | — | Selection stored with EMPLOYEE_SELECTED status |
| Approval creation | `POST /mock/approvals` | `approval_service.py:create_approval` | `test_approval_gate.py:test_ticket_blocked_before_approval` | Approval with PENDING status |
| Manager approve | `POST /mock/approvals/{id}/approve` | `approval_service.py:approve_approval` | `test_approval_gate.py:test_ticket_created_after_approval` | Status becomes APPROVED |
| Manager reject | `POST /mock/approvals/{id}/reject` | `approval_service.py:reject_approval` | `test_approval_gate.py:test_rejected_approval_blocks_ticket` | Status becomes REJECTED |
| Ticket blocked before approval | `POST /mock/itsm/tickets` | `itsm_service.py:create_ticket` | `test_approval_gate.py:test_ticket_blocked_before_approval` | 409 MANAGER_APPROVAL_REQUIRED with pre_approval_blocked=true |
| Ticket created after approval | `POST /mock/itsm/tickets` | `itsm_service.py:create_ticket` | `test_approval_gate.py:test_ticket_created_after_approval` | Ticket CREATED |
| Duplicate prevention | `POST /mock/itsm/tickets` | `itsm_service.py:create_ticket` | `test_approval_gate.py:test_idempotency_prevents_duplicate` | Second call returns EXISTING |
| Slack message storage | `POST /mock/slack/messages` | `slack.py:store_slack_message` / `slack_service.py:store_message` | — | Message stored without corruption |
| LLM/fallback messages | `POST /mock/llm/messages` | `llm_service.py:generate_message` | `test_llm_fallback.py:*` | Fallback message generated without keys |
| Bounded Q&A | `POST /onboarding/questions` | `onboarding.py:onboarding_questions` | — | Answers questions, blocks boundary violations |
| Profile update | `PATCH /mock/hr/employees/{employee_id}/profile` | `hr.py:patch_employee_profile` | — | Field updated, profile returned |
| Audit trail | `GET /audit/events` | `audit_service.py:log_event` | `test_approval_gate.py:test_audit_events_created` | Events filterable by correlation_id |
| Health probe | `GET /health` | `health.py:health` | — | Returns {"status":"healthy"} |
| Readiness probe | `GET /ready` | `health.py:ready` | — | Returns {"status":"ready","database":"ready"} |
| Version info | `GET /version` | `health.py:version` | — | Returns version, name, stage |
| Demo reset | `POST /demo/reset` | `seed.py:reset_and_seed` | — | Database reseeded |

## Service Mapping

| Service | File | Dependencies |
|---|---|---|
| API endpoints | `app/main.py` | FastAPI, SQLAlchemy, all services |
| Access recommender | `app/logic/access_recommender.py` | models, fixtures |
| Approval service | `app/services/approval_service.py` | models |
| ITSM service | `app/services/itsm_service.py` | models |
| Audit service | `app/services/audit_service.py` | models |
| LLM service | `app/services/llm_service.py` | httpx, fallback templates |
| Seed/reset | `app/seed.py` | models, fixtures |
