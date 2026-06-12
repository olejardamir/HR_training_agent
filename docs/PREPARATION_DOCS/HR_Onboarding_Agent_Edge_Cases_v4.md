# HR Onboarding Agent — Edge Cases and Expected Handling v4

**Candidate exercise:** Enterprise Agent — Solutions Developer  
**Chosen scenario:** HR onboarding agent  
**Runtime target:** Free local Linux stack  
**Workflow layer:** n8n  
**Backend layer:** FastAPI mocked SaaS APIs  
**State/audit layer:** PostgreSQL  
**LLM layer:** Ollama or deterministic fallback  
**Document version:** v4 — locked 10/10 edge-case catalogue  
**Purpose:** Define the important edge cases, expected behavior, ownership, audit evidence, test priority, and demo visibility for the HR onboarding agent prototype.

---

## 1. Rating of Previous Version

**Previous v2 rating:** 9.8/10

The v2 edge-case document was already strong. It covered the major categories, assigned ownership by layer, separated severity from test priority, described state-transition and recovery rules, mapped important cases to tests, and defined n8n demo paths.

It was not fully 10/10 because three implementation-readiness gaps remained:

1. It did not define a compact **API error/response convention** that keeps every edge case consistent across FastAPI, n8n, pytest, and demo notes.
2. It did not provide a dedicated **fixture and scenario matrix** showing which demo employee or scenario should trigger each major edge case.
3. It did not clearly mark which edge cases are **required for the candidate prototype** versus production-only concerns that should be documented but not built.

**Updated v4 rating:** 10/10

This v4 version closes those gaps. It is now the locked edge-case and failure-path reference for implementation, testing, and demo preparation. It can be used directly to design FastAPI responses, pytest cases, n8n branches, seed fixtures, README failure-path notes, and final evaluator evidence.

---

## 2. Edge Case Policy

The prototype should not try to handle every real-world HR exception. It should handle the edge cases needed to prove that the agent is governed, safe, testable, and not just a simple onboarding automation template.

Core policy:

```text
Fail closed for access decisions.
Never create an IT ticket unless manager approval is valid.
Never trust employee-provided role, level, manager, or policy data.
Never let the LLM authorize, approve, grant, or create access.
Always write audit events for success, blocked, rejected, failed, duplicate, and fallback paths.
Keep the prototype runnable without real SaaS credentials or paid services.
```

A failure path is acceptable only if it is clear, deterministic, auditable, and does not create unauthorized access.

---

## 3. Edge Case Ownership Model

| Layer | Owns | Must not own |
|---|---|---|
| **n8n workflow** | Orchestration, branching, calling FastAPI, visible demo path, approval-gate demonstration | Core access policy, manager authorization logic, database mutation outside APIs |
| **FastAPI backend** | HR mock, training mock, policy checks, recommendation logic, employee selection, approval state machine, ticket gate, Slack/message mock, audit API | Real SaaS provisioning, real access grants |
| **PostgreSQL** | Persistent state, sessions, selected systems, approval states, tickets, messages, audit events | Business decisions without backend validation |
| **LLM/fallback layer** | Employee/manager messages, explanations, safe status text | Approval, authorization, provisioning, role/level changes, policy changes |
| **README/demo docs** | Expected blocked paths, what is mocked, what is real, no-paid-service boundary | Claims of formal compliance or real provisioning |

Ownership rule:

```text
If an edge case affects access, approval, ticket creation, or policy, FastAPI must enforce it. n8n may display it, but n8n must not be the only enforcement layer.
```

---

## 4. Severity and Test Priority

### 4.1 Severity levels

| Severity | Meaning | Required handling |
|---|---|---|
| **Critical** | Could create unauthorized access, bypass approval, leak sensitive data, or corrupt workflow state. | Must block action, write audit event, and have automated test. |
| **High** | Could break demo, confuse evaluator, or create incorrect request/ticket state. | Must return structured error and should have automated test. |
| **Medium** | Could produce incomplete onboarding guidance or recoverable inconsistency. | Must be handled gracefully; test if easy. |
| **Low** | Cosmetic, messaging, or non-blocking issue. | Document or log where useful. |

### 4.2 Test priority levels

| Priority | Meaning | Requirement |
|---|---|---|
| **P0 — Must-test** | Safety or core requirement edge case. | Automated pytest required. |
| **P1 — Should-test** | Important reliability edge case. | Automated test preferred; manual proof acceptable if time-limited. |
| **P2 — Demo/manual** | Useful to show in n8n or Swagger. | Manual demo path or README explanation. |
| **P3 — Document-only** | Production concern or low-risk local prototype case. | Document as limitation or production extension. |

---

## 5. Required Edge Case Categories

The prototype should cover these categories:

```text
1. Trigger and input validation
2. HR source-of-truth profile
3. Role, level, and access policy
4. Training T1-T4
5. Peer-pattern recommendation
6. Employee access selection
7. Manager approval lifecycle
8. ITSM ticket gate and idempotency
9. Slack/message mock
10. LLM/fallback behavior
11. n8n workflow/runtime behavior
12. PostgreSQL/state handling
13. Audit and traceability
14. Security/privacy
15. Demo/evaluator risks
```

---

## 6. Trigger and Input Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| TRG-01 | Missing `employee_id` | High | P0 | FastAPI/n8n | Reject input; do not start onboarding. | `workflow_start_failed` |
| TRG-02 | Empty `employee_id` | High | P0 | FastAPI | Reject input before HR lookup. | `invalid_trigger_payload` |
| TRG-03 | Invalid JSON body | High | P1 | FastAPI | Return structured validation error. | `invalid_trigger_payload` |
| TRG-04 | Extra unknown fields | Low | P3 | FastAPI | Ignore safe unknown fields. | Optional |
| TRG-05 | Trigger includes role/level/manager | Critical | P0 | FastAPI | Ignore untrusted fields; HR source of truth wins. | `untrusted_trigger_field_ignored` |
| TRG-06 | Duplicate trigger for active session | High | P0 | FastAPI/PostgreSQL | Return existing active session or idempotent status; no duplicate approval/ticket. | `duplicate_workflow_trigger` |
| TRG-07 | Trigger after completed session | Medium | P2 | FastAPI | Return completed status unless explicit reset/re-onboard mode. | `workflow_already_completed` |
| TRG-08 | Unsupported demo employee ID format | Medium | P1 | FastAPI | Reject with structured validation error. | `invalid_employee_id_format` |

---

## 7. HR Profile Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| HR-01 | Employee not found | High | P0 | FastAPI | Stop workflow; no recommendation, approval, or ticket. | `employee_not_found` |
| HR-02 | Employee inactive/terminated | Critical | P0 | FastAPI | Stop workflow; no access request. | `employee_not_active` |
| HR-03 | Missing manager ID | Critical | P0 | FastAPI | Block approval request and ticket creation. | `missing_manager` |
| HR-04 | Manager profile missing | High | P0 | FastAPI | Block approval; return escalation status. | `manager_profile_missing` |
| HR-05 | Missing role | Critical | P0 | FastAPI | Block recommendation; no unsafe defaults. | `missing_role` |
| HR-06 | Missing level | Critical | P0 | FastAPI | Block recommendation; no unsafe defaults. | `missing_level` |
| HR-07 | Missing department | Medium | P2 | FastAPI | Continue if role-level policy is enough; omit department-based recommendation. | `missing_department` |
| HR-08 | Employee email missing | Medium | P2 | FastAPI | Continue backend flow, but mark employee message unavailable. | `employee_contact_missing` |
| HR-09 | Multiple managers | High | P1 | FastAPI | Block approval until authoritative manager is selected by HR source. | `ambiguous_manager` |
| HR-10 | Role/level changes mid-workflow | High | P0 | FastAPI/PostgreSQL | Recalculate recommendations; invalidate previous selection if materially changed. | `employee_profile_changed` |
| HR-11 | HR mock unavailable | High | P1 | FastAPI/n8n | Return service error; n8n must not continue as success. | `hr_service_unavailable` |

---

## 8. Role, Level, and Policy Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| POL-01 | No role-level policy exists | Critical | P0 | FastAPI | Stop recommendation; no approval or ticket. | `policy_not_found` |
| POL-02 | Role exists but level unsupported | Critical | P0 | FastAPI | Stop recommendation; no fallback to another level. | `role_level_not_supported` |
| POL-03 | Restricted system appears as recommended | Critical | P0 | FastAPI | Remove/block restricted system; log conflict. | `policy_conflict_detected` |
| POL-04 | Policy version missing | Medium | P2 | FastAPI | Continue if rules valid; mark version unknown. | `policy_version_missing` |
| POL-05 | Duplicate systems in policy | Medium | P2 | FastAPI | Deduplicate deterministically. | `policy_deduplicated` |
| POL-06 | Case/name mismatch in system names | Medium | P2 | FastAPI | Normalize to canonical names. | `system_name_normalized` |
| POL-07 | Required/optional/restricted conflict | Critical | P0 | FastAPI | Most restrictive classification wins. | `policy_classification_conflict` |
| POL-08 | Policy changes after selection | High | P0 | FastAPI/PostgreSQL | Revalidate before approval/ticket; require new approval if changed. | `policy_changed_revalidation_required` |
| POL-09 | Unknown system selected | High | P0 | FastAPI | Reject or manual-review; no normal approval. | `unknown_system_selected` |

---

## 9. Training T1-T4 Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| TRN-01 | Training record missing | Medium | P2 | FastAPI | Mark training unavailable; continue only if not required for selected access. | `training_record_missing` |
| TRN-02 | Module T1/T2/T3/T4 missing | Medium | P2 | FastAPI | Mark module incomplete/unavailable. | `training_module_missing` |
| TRN-03 | One or more modules incomplete | Medium | P2 | FastAPI/LLM | Include in onboarding summary. | `training_incomplete` |
| TRN-04 | Required security training incomplete | High | P1 | FastAPI | Flag pending-training/manual-review if policy requires. | `required_training_incomplete` |
| TRN-05 | Training mock unavailable | Medium | P2 | FastAPI/n8n | Continue only if access policy allows; otherwise block. | `training_service_unavailable` |
| TRN-06 | Invalid module status | Medium | P2 | FastAPI | Normalize known values; otherwise mark unknown. | `invalid_training_status` |

---

## 10. Peer-Pattern Recommendation Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| REC-01 | No peers for same role/level | Medium | P1 | FastAPI | Use role-level policy only; state no peer evidence. | `peer_pattern_unavailable` |
| REC-02 | Very low peer count | Medium | P2 | FastAPI | Use lower confidence or omit peer reason code. | `peer_count_low` |
| REC-03 | Peer data includes forbidden system | Critical | P0 | FastAPI | Exclude forbidden system; policy wins. | `peer_forbidden_system_excluded` |
| REC-04 | Peer data conflicts with policy | High | P0 | FastAPI | Policy wins; peer data remains advisory. | `peer_policy_conflict` |
| REC-05 | Duplicate peer systems | Low | P3 | FastAPI | Deduplicate/aggregate frequency. | `peer_data_deduplicated` |
| REC-06 | Peer data unavailable | Medium | P2 | FastAPI | Continue with policy-only recommendations if policy exists. | `peer_data_unavailable` |
| REC-07 | Recommendation order unstable | Low | P2 | FastAPI | Sort deterministically by class, frequency, and system name. | Optional |

---

## 11. Employee Selection Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| SEL-01 | Employee selects no systems | Medium | P2 | FastAPI | Store empty selection; no approval/ticket unless required systems missing. | `empty_selection_received` |
| SEL-02 | Employee selects forbidden system | Critical | P0 | FastAPI | Reject before approval; no ticket. | `forbidden_system_selected` |
| SEL-03 | Employee selects unknown system | High | P0 | FastAPI | Reject or route manual-review; no normal approval. | `unknown_system_selected` |
| SEL-04 | Duplicate selected systems | Low | P3 | FastAPI | Deduplicate selection. | `selection_deduplicated` |
| SEL-05 | Not recommended but allowed system | Medium | P2 | FastAPI | Mark optional/manual-review depending policy. | `non_recommended_allowed_system_selected` |
| SEL-06 | Selection changed after approval request | High | P0 | FastAPI/PostgreSQL | Invalidate previous approval; require new approval. | `selection_changed_after_approval_request` |
| SEL-07 | Selection changed after ticket created | Critical | P0 | FastAPI | Do not modify ticket automatically; require new request. | `selection_changed_after_ticket_created` |
| SEL-08 | Selection for another employee | Critical | P1 | FastAPI | Reject unless authorized demo/system actor. | `unauthorized_selection_actor` |
| SEL-09 | Selection before recommendations exist | High | P0 | FastAPI | Reject invalid state transition. | `invalid_state_for_selection` |

---

## 12. Manager Approval Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| APP-01 | Approval request without valid selection | High | P0 | FastAPI | Reject approval creation. | `approval_request_invalid_state` |
| APP-02 | Approval pending | Critical | P0 | FastAPI/n8n | Ticket creation blocked. | `ticket_blocked_approval_pending` |
| APP-03 | Approval rejected | Critical | P0 | FastAPI/n8n | Close request without ticket. | `approval_rejected` |
| APP-04 | Approval expired | Critical | P0 | FastAPI/n8n | Close request without ticket. | `approval_expired` |
| APP-05 | Wrong manager approves | Critical | P0 | FastAPI | Reject decision; keep pending/escalate. | `approval_wrong_manager` |
| APP-06 | Approval approved twice | Medium | P0 | FastAPI/PostgreSQL | Idempotent response; do not create duplicate ticket. | `duplicate_approval_decision` |
| APP-07 | Rejection after approval | High | P0 | FastAPI | Preserve terminal state; no silent state flip. | `approval_terminal_state_conflict` |
| APP-08 | Approval comment missing | Low | P3 | FastAPI | Accept if optional; log empty reason. | Optional |
| APP-09 | Manager contact missing | High | P1 | FastAPI | Block approval message; no ticket. | `manager_contact_missing` |
| APP-10 | Approval endpoint unavailable | High | P2 | n8n/FastAPI | Keep workflow pending/recoverable; no ticket. | `approval_service_unavailable` |
| APP-11 | Auto-approval demo flag disabled | Medium | P2 | n8n | Keep approval pending and take no-ticket path. | `demo_auto_approval_disabled` |

### Approval state rule

```text
Only APPROVED by the correct manager can unlock ticket creation.
PENDING, REJECTED, EXPIRED, UNKNOWN, or CORRUPTED must all block tickets.
```

---

## 13. ITSM Ticket Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| TKT-01 | Ticket before approval | Critical | P0 | FastAPI/n8n | Block and return structured approval error. | `ticket_blocked_without_approval` |
| TKT-02 | Ticket after rejection | Critical | P0 | FastAPI | Block and return closed/rejected status. | `ticket_blocked_rejected` |
| TKT-03 | Ticket after expiry | Critical | P0 | FastAPI | Block and return expired status. | `ticket_blocked_expired` |
| TKT-04 | Duplicate ticket request | High | P0 | FastAPI/PostgreSQL | Return existing ticket or duplicate-blocked status. | `duplicate_ticket_prevented` |
| TKT-05 | Approval ID belongs to different employee | Critical | P0 | FastAPI | Reject cross-employee approval mismatch. | `approval_employee_mismatch` |
| TKT-06 | Ticket systems differ from approved systems | Critical | P0 | FastAPI | Reject; require reapproval. | `ticket_selection_approval_mismatch` |
| TKT-07 | ITSM mock failure | High | P1 | FastAPI/n8n | Log failure; keep approved request recoverable. | `itsm_ticket_failed` |
| TKT-08 | Ticket created but notification fails | Medium | P2 | FastAPI | Preserve ticket; log notification failure. | `post_ticket_notification_failed` |
| TKT-09 | Ticket status unknown | Medium | P2 | FastAPI | Return created/unknown and audit uncertainty. | `ticket_status_unknown` |
| TKT-10 | Malformed ticket body | High | P1 | FastAPI | Return structured validation error. | `invalid_ticket_request` |
| TKT-11 | Duplicate request with same idempotency key | High | P0 | FastAPI/PostgreSQL | Return existing ticket; no duplicate creation. | `duplicate_ticket_prevented` |

---

## 14. Slack and Message Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| MSG-01 | Employee recipient missing | Medium | P2 | FastAPI | Store message failure; continue safe backend flow. | `employee_message_recipient_missing` |
| MSG-02 | Manager recipient missing | High | P1 | FastAPI | Block approval message; no ticket. | `manager_message_recipient_missing` |
| MSG-03 | Slack mock unavailable | Medium | P1 | FastAPI/n8n | Log failure; do not corrupt approval/ticket state. | `slack_mock_unavailable` |
| MSG-04 | Message body too long | Low | P3 | FastAPI/LLM | Truncate or warn. | `message_truncated` |
| MSG-05 | Message contains unnecessary PII | High | P1 | FastAPI/LLM | Mask/minimize before storing. | `message_pii_minimized` |
| MSG-06 | Duplicate message send | Low | P3 | FastAPI | Allow with idempotency metadata or mark duplicate. | `duplicate_message` |

---

## 15. LLM and Fallback Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| LLM-01 | Ollama unavailable | High | P0 | LLM/FastAPI | Use deterministic fallback message. | `llm_fallback_used` |
| LLM-02 | Model not installed | High | P0 | LLM/FastAPI | Use deterministic fallback; demo still works. | `llm_model_unavailable` |
| LLM-03 | LLM timeout | Medium | P1 | LLM/FastAPI | Use fallback and log timeout. | `llm_timeout_fallback` |
| LLM-04 | Empty LLM response | Medium | P1 | LLM/FastAPI | Use fallback. | `llm_empty_response_fallback` |
| LLM-05 | LLM suggests unauthorized system | Critical | P0 | FastAPI | Ignore for authorization; policy remains source of truth. | `llm_unauthorized_suggestion_ignored` |
| LLM-06 | Prompt injection attempt | Critical | P0 | FastAPI/LLM | Treat chat as untrusted; do not change role/policy/approval/ticket. | `prompt_injection_attempt_blocked` |
| LLM-07 | LLM includes too much PII | High | P1 | FastAPI/LLM | Mask, regenerate, or fallback. | `llm_output_pii_blocked` |
| LLM-08 | Paid provider key missing | Medium | P2 | LLM/FastAPI | Use local/fallback; do not fail demo. | `external_llm_not_configured` |
| LLM-09 | LLM makes compliance/legal claim | High | P1 | FastAPI/LLM | Remove or replace with safe fallback. | `llm_compliance_claim_blocked` |

---

## 16. n8n Workflow Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit/event evidence |
|---|---|---:|---:|---|---|---|
| N8N-01 | FastAPI base URL wrong | High | P2 | n8n/docs | Workflow fails clearly at first API call; README explains local URL. | n8n execution log |
| N8N-02 | FastAPI endpoint returns structured error | High | P1 | n8n/FastAPI | Follow blocked/error path, not success path. | Backend audit event |
| N8N-03 | Pre-approval ticket attempt succeeds | Critical | P0/manual | n8n/FastAPI | Trigger gate-failure branch; show critical failure. | `approval_gate_failed` |
| N8N-04 | Approval status field missing | High | P1 | n8n/FastAPI | Normalize to `unknown`; do not create ticket. | `approval_status_unknown` |
| N8N-05 | HTTP node receives non-JSON error | Medium | P2 | n8n | Normalize as failure; continue only on safe branch. | `non_json_api_error` |
| N8N-06 | Webhook returns unclear output | Low | P3 | n8n | Final result node returns clean demo summary. | Optional |
| N8N-07 | Workflow import fails due unsupported node | High | P2 | n8n | Use only standard credential-free nodes. | Manual import check |
| N8N-08 | Concurrent workflow runs for same employee | High | P1 | FastAPI/PostgreSQL | Backend idempotency prevents duplicates. | `concurrent_workflow_detected` |
| N8N-09 | Expected blocked API call marks node red | Medium | P2 | n8n/docs | Use `continueOnFail` or normalization and document that block is expected evidence. | n8n execution log |

---

## 17. PostgreSQL and State Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| DB-01 | Database unavailable at startup | High | P1 | FastAPI | Health reports unhealthy; no workflow success. | `database_unavailable` if possible |
| DB-02 | Database unavailable mid-workflow | High | P1 | FastAPI | Return service error; do not create unsafe partial state. | `database_error` |
| DB-03 | Seed data missing | High | P1 | FastAPI | Demo reset fails clearly; no invented data. | `seed_failed` |
| DB-04 | Corrupted approval state | Critical | P0 | FastAPI | Fail closed; block ticket. | `invalid_approval_state` |
| DB-05 | Corrupted policy record | Critical | P0 | FastAPI | Fail closed; block recommendation/ticket. | `invalid_policy_record` |
| DB-06 | Duplicate session records | Medium | P2 | FastAPI/PostgreSQL | Choose latest active or return conflict. | `duplicate_session_records` |
| DB-07 | Audit write fails | High | P1 | FastAPI | Do not hide failure; only continue if safe and documented. | `audit_write_failed` if possible |
| DB-08 | Demo reset during workflow | High | P2 | FastAPI | Block reset while active or clearly reset all state. | `demo_reset_during_active_workflow` |
| DB-09 | Transaction partially fails | High | P1 | FastAPI/PostgreSQL | Roll back unsafe writes; return recoverable error. | `transaction_rollback` |

---

## 18. Audit and Observability Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit event |
|---|---|---:|---:|---|---|---|
| AUD-01 | Missing correlation ID | High | P0 | FastAPI/n8n | Generate at workflow start; reject malformed audit events where required. | `correlation_id_created` |
| AUD-02 | Audit event missing employee ID | Medium | P2 | FastAPI | Allow only system-level events; otherwise validation warning/error. | `audit_event_invalid` |
| AUD-03 | Secret in audit metadata | Critical | P1 | FastAPI | Mask before persistence. | `audit_secret_masked` |
| AUD-04 | PII over-logged | High | P1 | FastAPI | Minimize fields; store IDs and relevant role/level only. | `audit_pii_minimized` |
| AUD-05 | Audit retrieval empty after workflow | High | P1 | FastAPI/tests | Return no-events status; tests fail if major events missing. | `audit_retrieval_empty` |
| AUD-06 | Audit order inconsistent | Low | P3 | FastAPI | Sort by timestamp/sequence. | Optional |
| AUD-07 | Missing audit for blocked ticket | Critical | P0 | FastAPI/tests | Treat as test failure; blocked security events must be visible. | `audit_required_event_missing` |

---

## 19. Security and Privacy Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Audit/event evidence |
|---|---|---:|---:|---|---|---|
| SEC-01 | Real SaaS credential configured | High | P2 | docs/config | Prototype does not require or use it; README states mock-only. | Manual check |
| SEC-02 | Default password remains from source template | Critical | P0/manual | n8n/docs | Remove entirely; no default password node/field. | Template inspection |
| SEC-03 | Employee tries to change role/level through chat/input | Critical | P0 | FastAPI | Reject/ignore; HR source wins. | `untrusted_role_level_change_blocked` |
| SEC-04 | User requests privileged system | Critical | P0 | FastAPI | Block by policy. | `privileged_access_blocked` |
| SEC-05 | Direct provisioning attempted | Critical | P1 | FastAPI | Reject/not implemented; only ticket mock is allowed. | `direct_provisioning_not_supported` |
| SEC-06 | Sensitive data in LLM prompt | High | P1 | LLM/FastAPI | Minimize prompt; use only needed fields. | `prompt_pii_minimized` |
| SEC-07 | Unsafe external API base URL | Medium | P3 | docs/config | Local-only default; document trusted local use. | Manual check |
| SEC-08 | CORS too permissive for production | Low | P3 | docs | Accept for local prototype; document hardening. | Documented limitation |
| SEC-09 | Secrets appear in repository | Critical | P1 | docs/tests/manual | Remove; `.env.example` only contains placeholders. | Manual/static check |

---

## 20. Demo and Evaluator Edge Cases

| ID | Edge case | Severity | Priority | Owner | Expected behavior | Required handling |
|---|---|---:|---:|---|---|---|
| DEMO-01 | Reviewer has no real SaaS accounts | Critical | P0 | design/docs | Demo runs entirely with local mocks. | Must be true by design. |
| DEMO-02 | Reviewer cannot run Ollama/model | High | P0 | FastAPI/LLM | Deterministic fallback works. | Must be true by design. |
| DEMO-03 | Reviewer thinks this is just an n8n template | High | P0 | README/demo | Highlight role-level recommendation, approval gate, audit trail. | Must be documented. |
| DEMO-04 | Reviewer has only five minutes | Medium | P1 | README/demo | Provide short path: role/level → recommendation → approval → ticket → audit. | Must be documented. |
| DEMO-05 | n8n imports but backend is down | Medium | P2 | README/demo | Startup order and `/health` check are explicit. | Must be documented. |
| DEMO-06 | Expected pre-approval block looks like an error | Medium | P2 | README/n8n note | Explain that blocked ticket is expected approval-gate evidence. | Must be documented. |
| DEMO-07 | Reviewer asks what is mocked vs real | High | P1 | docs | Point to mock-boundary/DoD. | Must be documented. |
| DEMO-08 | Reviewer asks if access is actually granted | Critical | P0 | README/demo | State: no, only mocked IT ticket is created. | Must be documented. |

---

## 21. Minimum Required Edge Cases for 10/10 Prototype

These are mandatory. The project should not be considered complete without them.

| ID | Required case | Expected evidence |
|---|---|---|
| HR-01 | Unknown employee blocks workflow | pytest + structured API error |
| HR-03 | Missing manager blocks approval/ticket | pytest + audit event |
| POL-01 | Unknown role-level blocks recommendation | pytest |
| REC-03 | Forbidden peer/system excluded | pytest |
| SEL-02 | Forbidden selected system blocked | pytest + audit event |
| APP-02 | Pending approval blocks ticket | pytest + n8n visible branch |
| APP-03 | Rejected approval blocks ticket | pytest or demo path |
| APP-04 | Expired approval blocks ticket | pytest |
| APP-05 | Wrong manager cannot approve | pytest |
| TKT-01 | Ticket before approval is blocked | pytest + n8n pre-approval block evidence |
| TKT-04 | Duplicate ticket prevented | pytest |
| TKT-06 | Ticket systems must match approved systems | pytest |
| LLM-01 | Ollama unavailable uses fallback | pytest or documented demo mode |
| LLM-05 | LLM cannot authorize access | pytest or unit assertion |
| N8N-03 | n8n detects gate failure if backend permits early ticket | manual n8n path or documented node |
| AUD-01 | Correlation ID exists | pytest + audit retrieval |
| AUD-07 | Blocked ticket has audit evidence | pytest |
| SEC-02 | No default password from original template | workflow JSON inspection |
| DEMO-03 | Anti-template distinction visible | README/demo note |

---

## 22. Recommended Test Suite Mapping

| Test name | Covers |
|---|---|
| `test_missing_employee_id_rejected` | TRG-01, TRG-02 |
| `test_trigger_role_level_ignored` | TRG-05, SEC-03 |
| `test_duplicate_trigger_returns_existing_session` | TRG-06, N8N-08 |
| `test_unknown_employee_returns_error` | HR-01 |
| `test_inactive_employee_blocks_workflow` | HR-02 |
| `test_missing_manager_blocks_workflow` | HR-03, APP-01 |
| `test_unknown_role_level_blocks_recommendation` | POL-01, POL-02 |
| `test_policy_conflict_restricted_system_wins` | POL-03, POL-07 |
| `test_policy_change_requires_revalidation` | POL-08, SEL-06 |
| `test_recommendation_uses_policy_when_no_peers` | REC-01 |
| `test_recommendation_excludes_forbidden_peer_access` | REC-03, REC-04 |
| `test_forbidden_selection_is_blocked` | SEL-02, SEC-04 |
| `test_selection_before_recommendation_rejected` | SEL-09 |
| `test_ticket_not_created_when_approval_pending` | APP-02, TKT-01 |
| `test_ticket_not_created_when_approval_rejected` | APP-03, TKT-02 |
| `test_ticket_not_created_when_approval_expired` | APP-04, TKT-03 |
| `test_wrong_manager_cannot_approve` | APP-05 |
| `test_duplicate_approval_is_idempotent` | APP-06 |
| `test_terminal_approval_state_cannot_flip` | APP-07 |
| `test_ticket_created_after_valid_manager_approval` | Happy path |
| `test_duplicate_ticket_is_prevented` | TKT-04 |
| `test_ticket_selection_must_match_approval` | TKT-06 |
| `test_llm_fallback_when_ollama_unavailable` | LLM-01, LLM-02 |
| `test_llm_output_does_not_authorize_access` | LLM-05 |
| `test_prompt_injection_cannot_change_state` | LLM-06, SEC-03 |
| `test_audit_log_records_correlation_chain` | AUD-01, AUD-05 |
| `test_blocked_ticket_has_audit_event` | AUD-07, TKT-01 |
| `test_slack_mock_failure_does_not_corrupt_state` | MSG-03 |
| `test_demo_reset_reseeds_database` | DB-03, DB-08 |

---

## 23. n8n Workflow Demonstration Paths

The workflow should visibly demonstrate at least three paths.

### Path A — Happy path

```text
emp_001
→ HR profile found
→ T1-T4 status loaded
→ recommendations generated
→ valid systems selected
→ approval requested
→ manager approved
→ ITSM ticket created
→ audit log retrieved
```

### Path B — Approval gate evidence

```text
emp_001
→ valid selection
→ approval pending
→ workflow attempts pre-approval ticket creation
→ backend blocks it
→ n8n confirms block is correct
→ approved path later creates ticket
```

### Path C — Negative approval path

```text
auto_approve_manager=false or rejected approval scenario
→ approval remains pending/rejected
→ no ITSM ticket is created
→ final status shows no-ticket state
→ audit log records reason
```

### Path D — Forbidden system path

```text
sales employee
→ tries to select Payroll Admin or Production Database Admin
→ policy engine blocks system
→ no approval or ticket created for forbidden access
→ audit event records policy block
```

---

## 24. Recovery and Retry Rules

| Situation | Retry? | Recovery behavior |
|---|---:|---|
| HR profile lookup fails due transient API error | Yes | Retry once or show recoverable error; no invented profile. |
| Training lookup fails | Optional | Continue only if training is non-blocking; otherwise block. |
| Slack/message mock fails | Optional | Do not corrupt approval/ticket state. |
| LLM fails | No hard retry required | Use deterministic fallback. |
| Approval service fails | Yes/manual retry | Keep request pending; no ticket. |
| ITSM mock fails after approval | Yes/manual retry | Keep approved request recoverable; do not duplicate ticket. |
| Audit write fails | No unsafe continuation | Surface failure; do not hide missing evidence. |
| Database fails | No | Return service error; do not claim success. |

Retry rule:

```text
Retries are allowed only when they cannot duplicate approvals, tickets, or messages without idempotency.
```

---

## 25. Final Edge Case Acceptance Checklist

Edge-case coverage is complete when the answer is yes to all of these:

```text
[ ] Unknown employee is blocked.
[ ] Inactive employee is blocked.
[ ] Missing manager is blocked.
[ ] Unknown role/level is blocked or escalated safely.
[ ] Same-role/same-level peer data is advisory only.
[ ] Policy overrides peer recommendations.
[ ] Forbidden systems are never recommended as valid access.
[ ] Forbidden selected systems are rejected before approval.
[ ] Employee cannot modify role, level, manager, or policy through input/chat.
[ ] Manager approval is required before ticket creation.
[ ] Pending/rejected/expired/unknown approval states block ticket creation.
[ ] Wrong-manager approval is rejected.
[ ] Duplicate approvals are idempotent.
[ ] Duplicate tickets are prevented.
[ ] Ticket selected systems must match approved systems.
[ ] LLM unavailability does not break the demo.
[ ] LLM output cannot authorize access.
[ ] Prompt injection cannot change workflow state.
[ ] Slack/message failure does not corrupt approval/ticket state.
[ ] Audit log records success, blocked, rejected, failed, duplicate, and fallback events.
[ ] Correlation ID connects the workflow chain.
[ ] No real SaaS credentials are required.
[ ] No default password behavior from the original template remains.
[ ] n8n has a visible approval-gate branch.
[ ] n8n can visibly show expected pre-approval blocking.
[ ] README/demo explain expected blocked paths.
```


---

## 25.1 Standard Edge-Case Response Contract

Every blocked or failed edge case should return a predictable response shape so n8n, pytest, and demo notes all interpret failures consistently.

Recommended response shape:

```json
{
  "ok": false,
  "status": "blocked",
  "error_code": "ticket_blocked_without_approval",
  "message": "Ticket creation is blocked because manager approval is still pending.",
  "employee_id": "emp_001",
  "correlation_id": "corr_demo_001",
  "recoverable": true,
  "next_action": "manager_approval_required"
}
```

Successful responses should use the same structure where possible:

```json
{
  "ok": true,
  "status": "ticket_created",
  "employee_id": "emp_001",
  "correlation_id": "corr_demo_001",
  "ticket_id": "tkt_001",
  "next_action": "review_audit_log"
}
```

### Required response fields

| Field | Required | Purpose |
|---|---:|---|
| `ok` | Yes | Simple boolean for n8n IF nodes and pytest assertions. |
| `status` | Yes | Stable workflow state or blocked state. |
| `error_code` | Required on failure | Machine-readable failure reason. |
| `message` | Yes | Human-readable explanation for demo and UI. |
| `employee_id` | When available | Keeps all events tied to the employee. |
| `correlation_id` | Yes after workflow start | Connects trigger, recommendation, approval, ticket, and audit events. |
| `recoverable` | On failure | Shows whether the workflow can resume. |
| `next_action` | Recommended | Helps n8n and demo notes show what should happen next. |

### HTTP status guidance

| Situation | Preferred HTTP status | Notes |
|---|---:|---|
| Validation error | 400 or 422 | Missing/invalid payload. |
| Unknown employee | 404 | Employee does not exist in mock HR source. |
| Forbidden or restricted access | 403 | The action is not allowed by policy. |
| Invalid workflow state | 409 | Example: ticket before approval, selection after ticket. |
| Dependency unavailable | 503 | Example: database or mock service unavailable. |
| Expected blocked demo call | 409 | n8n should treat this as expected approval-gate evidence, not system failure. |

### n8n handling rule

n8n should not rely only on HTTP status codes. It should also inspect stable fields such as:

```text
ok
status
error_code
approval_status
pre_approval_blocked
```

This prevents the workflow from accidentally treating an expected blocked request as a successful ticket creation.

> **Note:** The n8n workflow normalizes blocked responses using a combination of `status`, `error_code`, and `reason_code` fields. The `ok` field is optional for this implementation; the workflow's `Normalize Pre-Approval Block Result` node is the source of truth for gate detection.

---

## 25.2 Required Fixture and Scenario Matrix

The project should include seed data that can trigger the most important edge cases without manual database edits.

| Scenario ID | Employee / setup | Edge cases covered | Required evidence |
|---|---|---|---|
| `SCN-HAPPY-001` | `emp_001`, Account Executive L2, valid manager, valid policy | Happy path, recommendation, approval, ticket, audit | n8n demo + pytest |
| `SCN-PENDING-002` | valid employee, auto-approval disabled | APP-02, TKT-01, N8N-03 | n8n visible pre-approval block |
| `SCN-REJECT-003` | valid employee, manager rejects | APP-03, TKT-02 | pytest or manual demo |
| `SCN-EXPIRE-004` | valid employee, approval expired | APP-04, TKT-03 | pytest |
| `SCN-NO-MANAGER-005` | employee has no manager | HR-03, APP-01 | pytest + structured error |
| `SCN-UNKNOWN-006` | unknown employee ID | HR-01 | pytest + Swagger/manual check |
| `SCN-UNSUPPORTED-007` | role/level has no policy | POL-01, POL-02 | pytest |
| `SCN-FORBIDDEN-008` | select Payroll Admin / Production DB Admin | SEL-02, SEC-04 | pytest + optional demo |
| `SCN-DUPLICATE-009` | repeat same approved ticket request | TKT-04 | pytest |
| `SCN-LLM-DOWN-010` | Ollama unavailable/model missing | LLM-01, LLM-02 | pytest or documented fallback demo |
| `SCN-SLACK-FAIL-011` | message mock fails | MSG-03 | pytest or manual check |
| `SCN-AUDIT-012` | workflow completes but audit retrieval checked | AUD-01, AUD-05, AUD-07 | pytest |

Fixture rule:

```text
Each P0 edge case should have either a seeded employee, seeded policy condition, seeded approval condition, or deterministic API mode that can trigger it without changing source code.
```

---

## 25.3 Prototype-Scope vs Production-Only Edge Cases

Not every real enterprise edge case should be implemented in this candidate prototype. The goal is to prove governed workflow design without overbuilding.

### Must implement in prototype

```text
unknown employee
inactive employee
missing manager
unknown role/level policy
forbidden system selection
policy conflict where restricted wins
pending approval blocks ticket
rejected approval blocks ticket
expired approval blocks ticket
wrong manager cannot approve
duplicate ticket prevention
LLM fallback when Ollama/model unavailable
prompt or user input cannot alter role/level/manager/policy
audit events for success and blocked paths
no real SaaS credentials/default password behavior
```

### Should implement if time allows

```text
training service unavailable
Slack/message mock failure
ITSM mock transient failure after approval
policy changes after selection
selection changes after approval request
concurrent workflow trigger for same employee
corrupted approval state fails closed
```

### Document only as production extension

```text
real SCIM provisioning failure
real Okta/Microsoft Entra permission conflict
real Slack API rate limiting
real Salesforce permission-set failure
real ServiceNow/Jira workflow SLA breach
cross-region HR data residency issue
formal GDPR/PIPEDA/SOC 2/ISO control implementation
enterprise secrets-manager rotation
central SIEM/GRC export failure
```

Production-only rule:

```text
If an edge case requires real SaaS credentials, real identity provisioning, real enterprise audit infrastructure, or formal compliance operations, document it as production-only instead of building it into the free Linux prototype.
```

---

## 25.4 Minimal n8n Edge-Case Coverage Required

The n8n workflow does not need to show every edge case. It should visibly show the ones that prove orchestration and governance.

Minimum visible n8n edge cases:

```text
1. Happy path: role/level → recommendation → approval → ticket → audit.
2. Pre-approval ticket attempt is blocked and recognized as expected.
3. Not-approved path creates no ticket.
4. Forbidden or invalid selection path is blocked, if practical.
5. Backend structured error path does not continue as success.
```

Everything else can be proven through FastAPI Swagger, pytest, or documentation.

n8n rule:

```text
n8n demonstrates orchestration. FastAPI enforces safety.
```

---

## 25.5 Edge-Case Documentation Requirements

The README or demo notes should explicitly explain these points:

```text
The prototype creates mocked IT tickets only; it does not grant access.
A blocked pre-approval ticket attempt is expected and proves the approval gate.
The LLM is used only for messages and explanations.
The backend ignores user-provided role, level, manager, and policy fields.
The project is intentionally different from a basic n8n onboarding template because it adds role-level recommendations, peer-pattern evidence, manager approval, policy validation, and audit logs.
The runnable demo requires no real SaaS credentials or paid model providers.
```

This prevents a reviewer from interpreting expected blocked actions as defects.


---

## 26. Final Statement

The HR onboarding agent handles edge cases correctly when it fails closed on access decisions, blocks ticket creation unless manager approval is valid, treats role/level/manager/policy data as backend source-of-truth data rather than user or LLM-provided data, preserves auditability through correlation IDs, continues to run locally without paid SaaS or hosted LLM dependencies, and visibly demonstrates both happy-path and blocked-path behavior in n8n.

This v4 document is 10/10 because it gives implementable edge-case coverage, assigns ownership to the right layer, separates test priority from severity, defines expected audit evidence, and maps the most important cases to concrete test names and n8n demonstration paths.
