# Traceability Matrix

```text
requirement -> endpoint -> service -> test -> demo evidence
```

> **Boundary:** The chatbot is read-only (audit logging only) and retrieves approved onboarding/training guidance only. It does not decide access, approval, ticket creation, training completion, Salesforce setup, or profile updates. Those remain controlled by deterministic workflow/database logic. If approved guidance is missing, the chatbot refuses to invent guidance, while still allowing simple status answers from deterministic employee/workflow state.

| Requirement | Endpoint | Service/Logic | Test | Evidence |
|---|---|---|---|---|
| HR role/level lookup | `GET /mock/hr/employees/{employee_id}` | `routers/hr.py:get_employee_profile` | `test_access_recommender.py:test_access_recommendations_emp001_returns_recommendations` | HR profile returns role, level, department, manager |
| Training status (T1-T4) | `GET /mock/training/status/{employee_id}` | `routers/training.py:get_training` / `services/training_service.py:get_training_status` | `test_training_module_update.py:test_training_status_get_valid_returns_modules` | T1-T4 module statuses returned |
| Training status update | `PATCH /mock/training/status/{employee_id}/modules/{module_id}` | `services/training_service.py:update_module` | `test_training_module_update.py:test_training_module_update_valid_returns_updated` | Module status advanced |
| Salesforce profile | `GET /mock/salesforce/profile/{employee_id}` | `routers/salesforce.py:get_salesforce_profile` / `services/salesforce_service.py:get_profile` | `test_profile_update.py:test_salesforce_profile_get_valid_returns_profile` | Setup status returned |
| Salesforce profile update | `PATCH /mock/salesforce/profile/{employee_id}` | `services/salesforce_service.py:update_profile` | `test_profile_update.py:test_salesforce_profile_patch_valid_returns_updated` | Setup status toggled |
| Role-level policy recommendations | `GET /mock/access/recommendations/{employee_id}` | `services/recommendation_service.py:get_recommendations` | `test_access_recommender.py:test_access_recommendations_emp001_returns_recommendations` | Required, recommended, blocked systems |
| Peer-pattern reason codes | `GET /mock/access/recommendations/{employee_id}` | `services/recommendation_service.py:get_recommendations` | `test_access_recommender.py:test_access_recommendations_department_standard_includes_reason_code` | PEER_COMMON_ACCESS reason code and frequency |
| Forbidden system rejection | `POST /onboarding/select-access` | `routers/onboarding.py:select_access` / `services/selection_service.py:validate_selection` | `test_approval_gate.py:test_access_selection_forbidden_system_returns_403` | 403 + audit BLOCKED event |
| Inactive employee blocked | `GET /mock/access/recommendations/{employee_id}` | `services/recommendation_service.py:get_recommendations` | `test_access_recommender.py:test_inactive_employee_blocked` | `emp_inactive` returns 400 INACTIVE_EMPLOYEE, no approval/ticket state |
| Employee selection validation | `POST /onboarding/select-access` | `routers/onboarding.py:select_access` / `services/selection_service.py:validate_selection` | `test_selection_service.py:test_onboarding_select_access_valid_returns_request_id` | Selection stored with EMPLOYEE_SELECTED status |
| Approval creation | `POST /mock/approvals` | `services/approval_service.py:create_approval` | `test_approval_gate.py:test_duplicate_approval_returns_existing` | Approval with PENDING status |
| Manager approve | `POST /mock/approvals/{approval_id}/approve` | `services/approval_service.py:approve_approval` | `test_approval_gate.py:test_itsm_ticket_created_after_approval_returns_created` | Status becomes APPROVED |
| Manager reject | `POST /mock/approvals/{approval_id}/reject` | `services/approval_service.py:reject_approval` | `test_approval_gate.py:test_itsm_ticket_rejected_approval_blocks_ticket` | Status becomes REJECTED |
| Wrong manager blocked | `POST /mock/approvals/{approval_id}/approve` | `services/approval_service.py:approve_approval` | `test_approval_gate.py:test_wrong_manager_cannot_approve`, `test_approval_gate.py:test_wrong_manager_cannot_reject` | 403 WRONG_MANAGER |
| Ticket blocked before approval | `POST /mock/itsm/tickets` | `services/itsm_service.py:create_ticket` | `test_approval_gate.py:test_itsm_ticket_blocked_before_approval_returns_409_with_blocked` | 409 MANAGER_APPROVAL_REQUIRED with pre_approval_blocked=true |
| Ticket created after approval | `POST /mock/itsm/tickets` | `services/itsm_service.py:create_ticket` | `test_approval_gate.py:test_itsm_ticket_created_after_approval_returns_created` | Ticket CREATED with ticket_id |
| Duplicate prevention | `POST /mock/itsm/tickets` | `services/itsm_service.py:create_ticket` | `test_approval_gate.py:test_itsm_ticket_idempotent_request_returns_duplicate` | Second call returns ok=true, status=CREATED, duplicate=true, same ticket_id |
| ITSM mock failure (503 recoverable) | `POST /mock/itsm/tickets` with `simulate_failure=true` | `services/itsm_service.py:create_ticket` (simulate_failure branch) | `test_approval_gate.py:test_itsm_ticket_mock_failure_returns_503_recoverable` | 503 FAILED, ticket_created=false, recoverable=true, no ticket row, itsm_ticket_failed audit event |
| Slack message storage | `POST /mock/slack/messages` | `routers/slack.py:store_slack_message` / `services/slack_service.py:store_message` | `test_mock_endpoints.py:test_slack_post_message_returns_stored` | Message stored |
| Slack mock failure | `POST /mock/slack/messages` with `simulate_failure=true` | `services/slack_service.py:store_message` (simulate_failure branch) | `test_mock_endpoints.py:test_slack_post_simulate_failure_returns_503` | 503 FAILED, message not stored, audit event logged |
| LLM/fallback messages | `POST /mock/llm/messages` | `services/llm_service.py:generate_message` | `test_llm_fallback.py:test_llm_employee_summary_fallback_returns_message`, `test_llm_fallback.py:test_llm_manager_message_fallback_returns_message` | Fallback message generated without keys |
| Ollama provider (mocked) | `POST /mock/llm/messages` with `LLM_PROVIDER=ollama` | `services/llm_service.py:generate_message` (ollama branch) | `test_llm_fallback.py:test_ollama_provider_returns_ollama_response` | 200, llm_provider=ollama, fallback_used=false |
| Bounded Q&A | `POST /onboarding/questions` | `routers/onboarding.py:onboarding_questions` | `test_mock_endpoints.py:test_onboarding_questions_valid_returns_answer`, `test_mock_endpoints.py:test_onboarding_questions_blocked_forbidden_action` | Answers questions, blocks boundary violations |
| Employee profile update | `PATCH /mock/hr/employees/{employee_id}/profile` | `routers/hr.py:patch_employee_profile` | `test_employee_service.py:test_hr_profile_patch_valid_update_returns_updated` | Profile field updated |
| Audit trail | `GET /audit/events` | `services/audit_service.py:log_event` | `test_approval_gate.py:test_audit_events_created_during_flow_returns_events` | Events filterable by correlation_id |
| Health probe | `GET /health` | `routers/health.py:health` | `test_mock_endpoints.py:test_health_check_returns_healthy` | Returns healthy status |
| Readiness probe | `GET /ready` | `routers/health.py:ready` | `test_mock_endpoints.py:test_health_ready_returns_ready` | Returns ready with database status |
| Version info | `GET /version` | `routers/health.py:version` | `test_mock_endpoints.py:test_health_version_returns_version` | Returns version info |
| Demo reset | `POST /demo/reset` | `seed.py:reset_and_seed` | `test_mock_endpoints.py:test_demo_reset_resets_database` | Database reseeded |
| Empty employee_id rejected | `POST /onboarding/start/{employee_id}` | `routers/onboarding.py:start_onboarding` | `test_approval_gate.py:test_empty_employee_id_rejected` | 400 INVALID_EMPLOYEE_ID |
| Duplicate approval idempotent | `POST /mock/approvals` | `services/approval_service.py:create_approval` | `test_approval_gate.py:test_duplicate_approval_returns_existing` | Returns existing approval |
| n8n workflow contract | `n8n/hr_onboarding_workflow.json` | `scripts/validate_workflow_contract.py` | `test_n8n_contract_drift.py:test_workflow_file_exists`, `test_n8n_contract_drift.py:test_workflow_contract_passes`, `test_n8n_contract_drift.py:test_workflow_contract_negative_passes` | Validates workflow structure against contract |
| Content seed (training) | `api/app/fixtures/training_content.json` | `seed.py` / Content routers | `test_mini_rag.py:test_content_fixtures_are_seeded` | 114 runtime-approved training items |
| Content seed (onboarding) | `api/app/fixtures/onboarding_content.json` | `seed.py` / Content routers | `test_mini_rag.py:test_content_fixtures_are_seeded` | 85 runtime-approved onboarding items |
| Content retrieval | `GET /mock/content/training?module_id=T2` | `routers/content.py` | `test_mini_rag.py:test_training_content_endpoint_filters_t2` | T2-filtered content returned |
| RAG index build | `app/rag/index_builder.py` | sentence-transformers/TF-IDF | `test_mini_rag.py:test_rag_index_builds_from_runtime_approved_content` | 212 chunks indexed |
| RAG retrieval | `app/rag/retriever.py` | cosine similarity + metadata filter | `test_mini_rag.py:test_retriever_returns_t2_content_for_t2_question` | T2 question returns T2 chunks |
| Agent chat | `POST /agent/chat` | `routers/agent_chat.py` + `services/agent_response.py` | `test_mini_rag.py:test_agent_chat_returns_answer_with_used_content_ids` | Chat returns answer with sources |
| Agent audit | `POST /agent/chat` | `services/audit_service.py` | `test_mini_rag.py:test_agent_chat_logs_audit_event` | agent_chat audit events logged |

## Service Mapping

| Service | File | Dependencies |
|---|---|---|
| API endpoints | `app/main.py` | FastAPI, SQLAlchemy, all routers |
| Access recommender | `app/logic/access_recommender.py` | models, fixtures |
| Recommendation service | `app/services/recommendation_service.py` | models, policy_service |
| Policy service | `app/services/policy_service.py` | models |
| Approval service | `app/services/approval_service.py` | models |
| ITSM service | `app/services/itsm_service.py` | models |
| Audit service | `app/services/audit_service.py` | models |
| LLM service | `app/services/llm_service.py` | httpx, fallback templates |
| Selection service | `app/services/selection_service.py` | models, recommendation_service |
| Slack service | `app/services/slack_service.py` | models |
| Salesforce service | `app/services/salesforce_service.py` | models |
| Employee service | `app/services/employee_service.py` | models |
| Training service | `app/services/training_service.py` | models |
| Seed/reset | `app/seed.py` | models, fixtures |
| Workflow validator | `scripts/validate_workflow_contract.py` | n8n workflow JSON, FastAPI app |
| RAG index builder | `app/rag/index_builder.py` | fixtures, sentence-transformers/TF-IDF |
| RAG retriever | `app/rag/retriever.py` | content chunks, vectors |
| Agent chat | `app/routers/agent_chat.py` | retriever, agent_response, audit_service |
| Agent response | `app/services/agent_response.py` | llm_service, deterministic templates |
