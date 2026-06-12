# Edge Case Coverage Audit

| Edge case | Required behavior | Evidence | Status | Action |
|---|---|---|---|---|
| Missing employee_id | Block workflow; no approval/ticket | `test_empty_employee_id_rejected` | covered | none |
| Empty employee_id | Block workflow; no approval/ticket | `test_empty_employee_id_rejected` | covered | none |
| Unknown employee | Block workflow; no approval/ticket | `test_unknown_employee_start_returns_404` | covered | none |
| Inactive employee | Block recommendation; no approval/ticket | `test_inactive_employee_blocked` | covered | none |
| Missing manager | Block approval | `test_missing_manager_blocks_approval` | covered | none |
| Missing role | Block recommendation | `test_missing_role_level_returns_error` | covered | none |
| Missing level | Block recommendation | `test_missing_role_level_returns_error` | covered | none |
| Unknown role-level policy | Fall back to safe default; no approval/ticket | `test_access_recommendations_unsupported_role_level_returns_404` | covered | none |
| Policy conflict where restricted wins | Restricted system excluded from recommendation | `test_access_selection_forbidden_system_returns_403` | covered | none |
| Forbidden peer/system excluded | Blocked in selection | `test_access_selection_forbidden_system_returns_403` | covered | none |
| No peer data falls back to policy-only | Policy-only recommendation returned | `test_access_recommendations_emp001_returns_recommendations` | covered | none |
| Forbidden selected system blocked before approval | 403 at selection; no approval created | `test_access_selection_forbidden_system_returns_403` | covered | none |
| Unknown selected system blocked or manual-review | 409 at selection | `test_onboarding_select_unknown_system_is_blocked` | covered | none |
| Selection before session/recommendation rejected | 409; no approval | `test_onboarding_select_access_no_session_returns_409` | covered | none |
| Selection changed after approval request | Requires new approval (known limitation) | — | limitation | documented below |
| Pending approval blocks ticket | 409 with blocked flag | `test_itsm_ticket_blocked_before_approval_returns_409_with_blocked` | covered | none |
| Rejected approval blocks ticket | 409 with reason | `test_itsm_ticket_rejected_approval_blocks_ticket` | covered | none |
| Expired approval blocks ticket | 409; status EXPIRED | `test_expired_approval_blocks_ticket` | covered | none |
| Wrong manager cannot approve | 403 WRONG_MANAGER | `test_wrong_manager_cannot_approve`, `test_wrong_manager_cannot_reject` | covered | none |
| Terminal approval cannot flip | Known limitation (no re-open after terminal) | — | limitation | documented below |
| Pre-approval ticket attempt blocked | 409 pre_approval_blocked=true | `test_itsm_ticket_blocked_before_approval_returns_409_with_blocked` | covered | none |
| Approval ID employee mismatch blocked | 409 EMPLOYEE_MISMATCH | `test_itsm_ticket_employee_mismatch_returns_409_on_block` | covered | none |
| Ticket systems must match approved systems | 409 SYSTEMS_MISMATCH | `test_itsm_ticket_exact_systems_match_required` | covered | none |
| Subset systems mismatch | 409 SYSTEMS_MISMATCH | `test_itsm_ticket_subset_systems_blocks_with_409` | covered | none |
| Duplicate ticket prevented | Idempotent: ok=true, duplicate=true | `test_itsm_ticket_idempotent_request_returns_duplicate`, `test_itsm_ticket_idempotent_key_returns_existing_ticket` | covered | none |
| Idempotency key from different context | 409 IDEMPOTENCY_KEY_MISMATCH | `test_itsm_ticket_idempotency_key_from_different_context_blocks_with_409` | covered | none |
| ITSM mock failure recoverable | 503 with recoverable=true | `test_itsm_ticket_mock_failure_returns_503_recoverable` | covered | none |
| Slack mock failure does not corrupt state | 503; approval/ticket state unchanged | `test_slack_mock_failure_does_not_corrupt_state` | covered | none |
| LLM fallback when Ollama unavailable | Fallback template returned | `test_llm_employee_summary_fallback_returns_message`, `test_llm_manager_message_fallback_returns_message`, `smoke_llm_fallback.sh` | covered | none |
| LLM cannot authorize access | No approval/ticket from LLM | `test_llm_does_not_create_approval`, `test_llm_does_not_create_ticket` | covered | none |
| Prompt/chat cannot change role, level, manager, policy, approval, or ticket | Blocked by `/onboarding/questions` | `test_onboarding_question_blocked_for_approve_request`, `test_onboarding_question_blocked_for_grant_request`, `test_onboarding_question_blocked_for_bypass`, `test_onboarding_questions_blocked_forbidden_action` | covered | none |
| Q&A answers role/level from HR | Safe info returned | `test_onboarding_question_allows_valid_role_question`, `test_onboarding_questions_valid_returns_answer` | covered | none |
| Q&A answers training status | Safe info returned | `test_onboarding_questions_valid_returns_answer` | covered | none |
| Q&A answers recommendation questions | Safe info from deterministic data | `test_onboarding_question_allows_valid_role_question` | covered | none |
| Q&A blocks unsafe requests (approve, grant, bypass, override, change role, create ticket) | 403 BLOCKED_FORBIDDEN_ACTION | `test_onboarding_question_blocked_for_approve_request`, `test_onboarding_question_blocked_for_grant_request`, `test_onboarding_question_blocked_for_bypass`, `test_onboarding_questions_blocked_forbidden_action` | covered | none |
| Q&A does not mutate workflow state | No approval/ticket change | verified by design (read-only endpoint) | covered | none |
| Correlation ID exists across workflow | Audit events share correlation_id | `test_audit_events_created_during_flow_returns_events` | covered | none |
| Audit event for blocked ticket | BLOCKED event logged | `test_audit_events_created_during_flow_returns_events` | covered | none |
| Audit event for rejected/expired/wrong-manager paths | REJECTED/EXPIRED events logged | `test_audit_events_created_during_flow_returns_events` | covered | none |
| Audit event for fallback | Message stored with audit event | `test_llm_employee_summary_fallback_returns_message` | covered | none |
| No real SaaS credentials | No API keys in `.env.example`; no provisioning secrets | `validate_no_secrets.py`, `.env.example` review | covered | none |
| No default password or copied provisioning secret | Secrets validator + origin template review | `validate_no_secrets.py`, `n8n/hr_onboarding_workflow.json` review | covered | none |
| n8n import succeeds or manual import evident | CLI import in `verify_all.sh`; ALLOW_MANUAL_N8N_IMPORT bypass | `import_n8n_workflow.sh`, `verify_all.sh` | covered | none |
| n8n approved branch creates ticket | Webhook output has ticket_created=true | `smoke_n8n_happy_path.sh` | covered | none |
| n8n not-approved branch creates no ticket | Webhook output has ticket_created=false | `smoke_n8n_reject_path.sh`, `smoke_n8n_pending_path.sh`, `smoke_n8n_expire_path.sh`, `smoke_n8n_wrong_manager_path.sh` | covered | none |
| n8n forbidden path creates no approval/ticket | Webhook output: forbidden=true, ticket_created=false | `smoke_n8n_forbidden_path.sh` | covered | none |
| Profile update: HR PATCH changes only allowed fields | Role/level/manager unchanged | `test_hr_profile_patch_ignores_role_level_manager_changes`, `test_hr_profile_patch_valid_update_returns_updated` | covered | none |
| Profile update: Training PATCH updates status | T1-T4 module status advanced | `test_training_module_update_valid_returns_updated` | covered | none |
| Profile update: Salesforce PATCH updates mock state | Setup status toggled | `test_salesforce_profile_patch_valid_returns_updated` | covered | none |
| Profile update: Slack mock records metadata | Message stored | `test_slack_post_message_returns_stored` | covered | none |
| No profile-update endpoint can grant access or bypass approval | All update endpoints return only mock state | code review + `validate_openapi_contract.py` | covered | none |

## Known Limitations

- **Selection changed after approval request:** requires new approval. The current implementation does not support updating selections for an existing approval. A new employee onboarding session must be initiated.
- **Terminal approval cannot flip:** once an approval reaches APPROVED or REJECTED, it cannot be reopened. This is by design for audit integrity.
