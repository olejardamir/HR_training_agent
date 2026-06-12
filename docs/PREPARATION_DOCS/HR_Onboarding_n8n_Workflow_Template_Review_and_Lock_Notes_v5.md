# HR Onboarding Agent — n8n Workflow Template Review and Lock Notes v5

**Document purpose:** Final review, lock notes, and runtime interpretation guide for the updated n8n workflow template.  
**Workflow file reviewed:** `hr_onboarding_agent_updated_workflow_v4.json`  
**Source template:** Free n8n employee provisioning workflow adapted into a governed HR onboarding/access-request workflow.  
**Target stack:** free local Linux runtime: n8n + FastAPI mock APIs + PostgreSQL + Ollama or deterministic fallback + Docker/Podman Compose + pytest.  
**Document version:** v5 — final locked companion note with drift-control and import-hardening rules.  

---

## 1. Rating of Previous Lock Notes

**Previous Markdown lock document rating:** 9.7/10

The v3 lock document was already strong. It explained the workflow purpose, backend dependency, mock boundary, approval-gate meaning, expected endpoint contract, response-shape assumptions, and final verification steps.

It was not fully 10/10 because it still needed four refinements:

1. A clearer **node-by-node contract map** showing exactly which n8n node expects which backend endpoint.
2. A stronger **JSON import/readiness checklist** for n8n compatibility and local runtime assumptions.
3. A clearer **response-normalization rule** so future backend implementation does not break fragile n8n expressions.
4. A sharper distinction between the workflow as a **starter orchestration template** and the backend/test suite as the actual source of proof.

**Updated v4 rating:** 10/10

This v4 version closes those gaps and should be treated as the final companion document for the updated n8n workflow template.

---

## 2. Final Verdict

The updated workflow is acceptable as the project’s n8n starting template.

It is no longer a direct provisioning workflow. It has been converted into a governed HR onboarding/access-request workflow that calls local FastAPI mock services instead of real SaaS credential nodes.

Final rating:

```text
Workflow JSON v4 + this v5 lock document = 10/10
```

The workflow is suitable because it demonstrates:

```text
new hire trigger
→ HR profile lookup
→ T1-T4 training lookup
→ role-level recommendation
→ peer-pattern-informed access recommendation
→ employee selection simulation
→ manager approval request
→ pre-approval ticket block evidence
→ manager approval simulation
→ approved/not-approved branch
→ ITSM ticket creation only after approval
→ final onboarding status retrieval
→ audit-event retrieval
```

The workflow must still be paired with the FastAPI backend, PostgreSQL state, seed data, and tests. The n8n file alone is not the full prototype.

---

## 3. What Changed from the Original Template

The original template provisioned real accounts and required real SaaS credentials.

### Removed or replaced

```text
Google Workspace account creation
real Slack channel invitation
real Jira user creation
real Salesforce user creation
Gmail welcome email
stored default password field
real SaaS credential dependency
real account provisioning
```

### Replaced with

```text
FastAPI HR mock lookup
FastAPI training mock lookup
FastAPI access recommendation
FastAPI LLM/fallback message generation
FastAPI Slack-style message mock
FastAPI manager approval state
FastAPI ITSM ticket mock
FastAPI onboarding status retrieval
FastAPI audit-event retrieval
```

This matches the project boundary: the demo must run locally on Linux without paid accounts, real Slack/Jira/Salesforce/Google credentials, or hosted LLM keys.

---

## 4. Final Workflow Purpose

The workflow is the visible orchestration layer.

It should be used to show the evaluator:

```text
how the agent flow moves across systems
how n8n coordinates mock SaaS calls
how role/level data enters the decision path
how access recommendations are retrieved
how manager approval controls ticket creation
how blocked and approved paths differ
how final status and audit evidence can be inspected
```

The workflow should not contain the core business logic.

Core policy behavior belongs in the FastAPI backend and test suite.

---

## 5. Ownership Boundary

### n8n owns

```text
workflow trigger
HTTP call sequencing
visible orchestration canvas
branching between approved and not-approved states
simple demo simulation steps
calling local mock services
showing final status and audit retrieval
```

### FastAPI owns

```text
employee source-of-truth mock
training T1-T4 mock
role-level access policy
peer-pattern recommendation
employee selection validation
approval state machine
ITSM ticket gate
Slack-style message storage
LLM/fallback message service
audit logging
structured error responses
```

### PostgreSQL owns

```text
employee records
training records
role-level policies
peer access patterns
onboarding sessions
selected access requests
manager approvals
ITSM tickets
Slack-style messages
audit events
```

### LLM or fallback owns

```text
employee-facing summary text
manager approval request text
recommendation explanation text
status/reminder text
```

### LLM must never own

```text
approval decisions
access authorization
role/level assignment
ticket gate decisions
restricted-system exceptions
policy overrides
```

---

## 6. Node-by-Node Contract Map

This is the required interpretation of the current workflow.

| n8n node | Backend endpoint or behavior | Required result |
|---|---|---|
| `New Hire Onboarding Trigger` | Webhook receives `employee_id` or uses demo default | Starts workflow without real SaaS input |
| `Normalize Demo Input` | n8n Set node | Produces stable `employee_id`, `API_BASE_URL`, and `correlation_id` |
| `Start Onboarding Session` | `POST /onboarding/start/{employee_id}` | Creates or returns onboarding session |
| `Fetch HR Profile Mock` | `GET /mock/hr/employees/{employee_id}` | Returns role, level, department, manager, employment status |
| `Fetch Training T1-T4 Mock` | `GET /mock/training/status/{employee_id}` | Returns T1, T2, T3, T4 status |
| `Generate Role-Level Access Recommendations` | `GET /mock/access/recommendations/{employee_id}` | Returns required/recommended/blocked systems with reason codes |
| `Generate Employee Summary via LLM or Fallback` | `POST /mock/llm/messages` | Returns employee-facing text; does not authorize action |
| `Store Employee Slack-Style Message` | `POST /mock/slack/messages` | Stores local message record |
| `Simulate Employee Access Selection` | `POST /onboarding/select-access` | Stores selected systems after backend validation |
| `Create Manager Approval Request` | `POST /mock/approvals` | Creates pending manager approval |
| `Generate Manager Approval Message` | `POST /mock/llm/messages` | Returns manager-facing approval text |
| `Store Manager Approval Message` | `POST /mock/slack/messages` | Stores local manager message record |
| `Pre-Approval Ticket Attempt Expected Block` | `POST /mock/itsm/tickets` | Must return blocked result because approval is not valid yet |
| `Simulate Manager Approval` | `POST /mock/approvals/{approval_id}/approve` | Changes approval state to approved for demo path |
| `Fetch Approval Status` | `GET /mock/approvals/{approval_id}` | Returns approval status |
| `Is Manager Approval Approved?` | n8n IF node | Routes only `APPROVED` to ticket creation |
| `Create ITSM Ticket After Approval` | `POST /mock/itsm/tickets` | Creates one mocked ticket after approval |
| `Store Not-Approved Notice` | `POST /mock/slack/messages` | Stores no-ticket notice for pending/rejected/expired path |
| `Fetch Final Onboarding Status` | `GET /onboarding/status/{employee_id}` | Returns final workflow status |
| `Fetch Audit Events` | `GET /audit/events?...` | Returns audit chain for employee/correlation ID |

The workflow is not acceptable if `Create ITSM Ticket After Approval` can run without `APPROVED` status.

---

## 7. Required Local Runtime Assumptions

The workflow assumes a local Compose-style runtime.

| Service | Expected address inside Compose | Purpose |
|---|---|---|
| FastAPI backend | `http://api:8000` | Mock SaaS APIs and backend logic |
| n8n | `http://localhost:5678` | Workflow UI |
| PostgreSQL | `postgres:5432` | State and audit persistence |
| Ollama | `http://ollama:11434` or fallback | Optional local message generation |

Default n8n `API_BASE_URL` should be:

```text
http://api:8000
```

Use this only when n8n and FastAPI run on the same Compose network.

If n8n runs outside Compose, use:

```text
http://localhost:8000
```

---

## 8. Required Backend Endpoint Contract

The workflow expects these routes or exact equivalents.

### Health and demo state

```text
GET  /health
POST /demo/reset
```

### Onboarding state

```text
POST /onboarding/start/{employee_id}
POST /onboarding/select-access
GET  /onboarding/status/{employee_id}
```

### Mock SaaS reads

```text
GET /mock/hr/employees/{employee_id}
GET /mock/training/status/{employee_id}
GET /mock/access/recommendations/{employee_id}
```

### Messages

```text
POST /mock/llm/messages
POST /mock/slack/messages
```

### Approval

```text
POST /mock/approvals
GET  /mock/approvals/{approval_id}
POST /mock/approvals/{approval_id}/approve
POST /mock/approvals/{approval_id}/reject
POST /mock/approvals/{approval_id}/expire
```

### Ticketing

```text
POST /mock/itsm/tickets
```

### Audit

```text
GET /audit/events
```

Endpoint names can change later, but the workflow JSON must be updated at the same time. Do not let endpoint drift occur silently.

---

## 9. Response Normalization Rule

To keep the n8n workflow stable, every backend response should return predictable top-level fields.

Do not bury required IDs deeply unless the workflow is updated to match that shape.

Required stable identifiers:

```text
employee_id
correlation_id
workflow_id or session_id
request_id
approval_id
ticket_id, when ticket exists
status
reason_code, when blocked or failed
```

Recommended status values:

```text
STARTED
PROFILE_LOADED
RECOMMENDED
EMPLOYEE_SELECTED
PENDING
APPROVED
REJECTED
EXPIRED
BLOCKED
CREATED
TICKET_CREATED
COMPLETED
ERROR
```

Recommended backend rule:

```text
All action endpoints should return a status, relevant ID, and correlation_id.
```

This reduces brittle n8n expressions and makes audit correlation easier.

---

## 10. Required Response Shapes

### Start onboarding response

```json
{
  "employee_id": "emp_001",
  "correlation_id": "corr_demo_001",
  "workflow_id": "wf_demo_001",
  "status": "STARTED"
}
```

### HR profile response

```json
{
  "employee_id": "emp_001",
  "name": "Maya Chen",
  "email": "maya.chen@example.test",
  "role": "Account Executive",
  "level": "L2",
  "department": "Sales",
  "manager_id": "mgr_101",
  "employment_status": "new_hire"
}
```

### Training response

```json
{
  "employee_id": "emp_001",
  "modules": [
    {"module_id": "T1", "status": "complete"},
    {"module_id": "T2", "status": "incomplete"},
    {"module_id": "T3", "status": "incomplete"},
    {"module_id": "T4", "status": "not_required_yet"}
  ]
}
```

### Recommendation response

```json
{
  "employee_id": "emp_001",
  "recommendations": [
    {
      "system": "Salesforce",
      "recommendation_type": "recommended",
      "reason_codes": ["ROLE_LEVEL_POLICY", "PEER_COMMON_ACCESS"],
      "requires_manager_approval": true
    }
  ],
  "blocked_systems": [
    {
      "system": "Payroll Admin",
      "reason_codes": ["FORBIDDEN_FOR_ROLE_LEVEL"]
    }
  ]
}
```

### Selection response

```json
{
  "employee_id": "emp_001",
  "request_id": "req_001",
  "selected_systems": ["Salesforce", "Gong", "Sales Slack Channels"],
  "status": "EMPLOYEE_SELECTED"
}
```

### Approval response

```json
{
  "approval_id": "apr_001",
  "request_id": "req_001",
  "employee_id": "emp_001",
  "manager_id": "mgr_101",
  "status": "APPROVED"
}
```

### Blocked ticket response

```json
{
  "employee_id": "emp_001",
  "request_id": "req_001",
  "status": "BLOCKED",
  "reason_code": "MANAGER_APPROVAL_REQUIRED",
  "ticket_created": false
}
```

### Ticket response

```json
{
  "ticket_id": "itsm_001",
  "request_id": "req_001",
  "employee_id": "emp_001",
  "status": "CREATED"
}
```

---

## 11. Pre-Approval Ticket Attempt Interpretation

The pre-approval ticket attempt is intentional.

It is demo evidence, not a production step.

Correct interpretation:

```text
The workflow tries to create a ticket before approval.
The backend rejects it.
The rejection proves the approval gate works.
After manager approval, the workflow creates the ticket successfully.
```

This is useful because the candidate exercise asks for reliability and security practices, not only a happy path.

Do not remove this step unless another clear approval-gate proof exists.

---

## 12. Approved and Not-Approved Branch Rules

### Approved branch

```text
approval.status == APPROVED
→ create ITSM ticket
→ fetch final status
→ fetch audit events
```

### Not-approved branch

```text
approval.status == PENDING / REJECTED / EXPIRED / BLOCKED / ERROR / missing
→ store not-approved notice
→ do not create ticket
→ fetch final status
→ fetch audit events
```

The branch is valid only if the approved ticket node is unreachable for every non-approved status.

---

## 13. Required n8n Evidence

The n8n canvas should visibly prove these points:

```text
[ ] real SaaS credential nodes were removed
[ ] all SaaS-like operations are HTTP calls to local FastAPI mocks
[ ] HR role and level are fetched before recommendation
[ ] T1-T4 training status is fetched
[ ] recommendations come from the backend recommender
[ ] employee selection is recorded through backend validation
[ ] manager approval request exists before ticket creation
[ ] pre-approval ticket attempt is blocked
[ ] approved branch creates the ITSM ticket
[ ] not-approved branch creates no ticket
[ ] final onboarding status is retrieved
[ ] audit events are retrieved
[ ] sticky notes explain mock boundary and no-paid-service rule
```

---

## 14. Import and Runtime Checklist

Before importing the workflow:

```text
[ ] FastAPI backend starts locally
[ ] GET /health returns healthy
[ ] FastAPI /docs opens
[ ] PostgreSQL starts locally
[ ] seed data includes emp_001
[ ] emp_001 has role, level, department, and manager
[ ] T1-T4 training status exists for emp_001
[ ] role-level policy exists for emp_001
[ ] peer-pattern data exists for emp_001 role/level
[ ] approval endpoints support pending, approved, rejected, and expired states
[ ] ticket endpoint blocks missing approval
[ ] audit endpoint returns events
[ ] n8n can reach API_BASE_URL
```

After importing the workflow:

```text
[ ] workflow opens without missing credential errors
[ ] no Google Workspace credential node remains
[ ] no Slack credential node remains
[ ] no Jira credential node remains
[ ] no Salesforce credential node remains
[ ] no Gmail credential node remains
[ ] all action nodes are HTTP Request nodes or local n8n logic nodes
[ ] API_BASE_URL points to the correct local backend address
[ ] approved branch is visible
[ ] not-approved branch is visible
[ ] sticky notes explain why this differs from the original template
```

---

## 15. Workflow JSON Validation Checklist

Before locking the workflow JSON:

```text
[ ] JSON parses successfully
[ ] workflow name clearly identifies HR onboarding agent
[ ] workflow is inactive by default before import
[ ] no real credentials are embedded
[ ] no API keys or secrets are embedded
[ ] no hardcoded real company data is present
[ ] all URLs use API_BASE_URL or documented local URL
[ ] node names are evaluator-readable
[ ] node order follows the onboarding story
[ ] approval gate node is easy to identify
[ ] ticket node exists only on approved path
[ ] sticky notes explain mock boundary and demo logic
```

This checklist prevents a workflow from importing successfully while still failing the exercise boundary.

---

## 16. Failure and Error-Path Expectations

The n8n workflow does not need to visually demonstrate every error path, but the project must support them through backend behavior and tests.

Required backend/test failure paths:

```text
unknown employee
missing manager
unknown role-level
forbidden access selected
approval pending
approval rejected
approval expired
duplicate ticket request
ITSM mock failure
Slack mock failure
LLM unavailable
```

The workflow should visibly show at least:

```text
pre-approval ticket blocked
approved ticket created
not-approved branch creates no ticket
```

Other failures can be shown through FastAPI Swagger, pytest, or demo notes.

---

## 17. Backend Must Remain the Source of Truth

The n8n workflow may simulate user and manager actions for demo purposes, but it must not become the authority for policy.

The backend must enforce:

```text
role-level policy
restricted-system blocking
selection validation
approval status
ticket creation gate
duplicate ticket prevention
audit event creation
```

This matters because n8n is easy to visually branch around. The evaluator should see that even if n8n attempts an unsafe ticket call, FastAPI blocks it.

---

## 18. Anti-Template Differentiation

The workflow must not be presented as a copied onboarding template.

Use this distinction:

| Original onboarding template | Updated HR onboarding agent workflow |
|---|---|
| direct account provisioning | mocked SaaS calls through FastAPI |
| department-based branch | role/level and peer-pattern recommendation |
| real SaaS credentials | no-paid local Linux runtime |
| simple welcome message | bounded LLM/fallback communication |
| task automation | approval-gated access-request orchestration |
| limited evidence | audit log and reason codes |

Safe positioning:

```text
This workflow started from a public onboarding/provisioning pattern, but it has been changed into a governed HR onboarding/access-request workflow. The value is not generic onboarding automation; the value is role-level recommendation, peer-pattern evidence, manager approval, ticket gating, and auditability.
```

---

## 19. Final Verification Run

Before calling the workflow complete, run this verification sequence:

```text
1. Start local stack.
2. Confirm FastAPI health endpoint.
3. Reset demo data.
4. Import workflow into local n8n.
5. Trigger onboarding for emp_001.
6. Confirm HR profile is loaded.
7. Confirm training T1-T4 status is loaded.
8. Confirm recommendations include reason codes.
9. Confirm employee selection is stored.
10. Confirm approval request is created.
11. Confirm pre-approval ticket attempt is blocked.
12. Confirm manager approval is simulated.
13. Confirm approved branch runs.
14. Confirm ITSM ticket is created after approval.
15. Confirm final status includes ticket ID.
16. Confirm audit events include the workflow chain.
17. Confirm no real SaaS credentials are needed.
18. Confirm no paid LLM/API key is needed.
```

Minimum command-level evidence:

```text
GET /health returns healthy
n8n workflow imports successfully
pytest passes for approval and ticket-gate behavior
```

---

## 20. What This Document Does Not Replace

This document does not replace:

```text
FastAPI backend implementation
PostgreSQL schema and seed data
pytest test suite
README setup instructions
1-2 page solution design
Definition of Done document
mock-boundary document
```

It only locks the interpretation and acceptance criteria for the n8n workflow template.

---

## 21. Final Lock Statement

The updated n8n workflow template is locked as the correct starting orchestration artifact when paired with this document.

It should be treated as:

```text
a visible workflow canvas for the HR onboarding agent
an orchestration layer over local FastAPI mock services
a demonstration of role/level onboarding flow
a demonstration of manager approval gating
a demonstration of ticket creation only after approval
a demonstration of final status and audit retrieval
```

It should not be treated as:

```text
a complete standalone prototype
a real SaaS provisioning workflow
a copied onboarding template
a production workflow
a compliance artifact
a replacement for backend tests
```

Final acceptance:

```text
Workflow JSON v4 + backend contract + local mock services + PostgreSQL state + pytest + this lock document = ready for implementation and demo packaging.
```
---

## 22. Rating of v4 and Final v5 Fix

**Previous v4 rating:** 9.9/10

The v4 document was already strong and practically usable. It correctly defined the workflow purpose, mock boundary, node-by-node contract, backend ownership, response-shape expectations, approval-gate interpretation, and final verification path.

The only remaining gap was not architectural. It was operational: the document needed a final **workflow/backend drift-control rule** and a stronger **n8n import-hardening checklist** so the workflow does not silently become inconsistent with the FastAPI backend as implementation starts.

**Updated v5 rating:** 10/10

This v5 version is now the locked companion document for the updated workflow JSON.

---

## 23. Workflow / Backend Drift-Control Rule

The n8n workflow and FastAPI backend must evolve together.

Do not change one side without checking the other side.

### Backend change requires workflow review when any of these change

```text
endpoint path
HTTP method
request body field
response field name
status value
approval status naming
ticket-created response shape
audit query parameter
correlation_id handling
employee_id location
approval_id location
request_id location
```

### Workflow change requires backend review when any of these change

```text
node name used by expressions
node output used by later nodes
API_BASE_URL handling
selected systems payload
approval request payload
approval status branch condition
ticket creation payload
audit-event retrieval query
error-branch behavior
```

### Drift-control acceptance rule

```text
The workflow is not considered valid if it imports into n8n but calls stale backend routes, expects stale response fields, or branches on status values the backend no longer returns.
```

Minimum drift check before every workflow lock:

```text
[ ] Every workflow HTTP node path exists in FastAPI.
[ ] Every workflow HTTP method matches FastAPI.
[ ] Every workflow request body field is accepted by FastAPI.
[ ] Every workflow expression points to a response field FastAPI actually returns.
[ ] The approval branch checks the backend's real approval status value.
[ ] Ticket creation is still blocked by the backend when approval is missing or invalid.
[ ] Audit retrieval still returns the correlation chain.
```

---

## 24. n8n Import-Hardening Checklist

Before treating the workflow JSON as ready, verify these import details.

```text
[ ] Workflow imports into a clean local n8n instance.
[ ] Workflow opens without credential warnings.
[ ] No original Google Workspace node remains.
[ ] No original Gmail node remains.
[ ] No original Slack credential node remains.
[ ] No original Jira credential node remains.
[ ] No original Salesforce credential node remains.
[ ] No node requires external SaaS credentials.
[ ] Webhook/manual trigger is easy to find.
[ ] API_BASE_URL is easy to edit in one place.
[ ] HTTP Request nodes use local mock endpoints only.
[ ] Approval-gate node is visually obvious.
[ ] Approved and not-approved branches are visually separate.
[ ] Ticket creation node is only on the approved branch.
[ ] Sticky notes explain the mock boundary and anti-template differentiation.
```

If any credential-based SaaS node remains from the original template, the workflow is not locked.

---

## 25. API_BASE_URL Runtime Rule

Use one API base URL depending on how n8n is run.

| Runtime shape | API_BASE_URL |
|---|---|
| n8n and FastAPI both inside Compose | `http://api:8000` |
| n8n on host, FastAPI in container exposed to host | `http://localhost:8000` |
| n8n in another container network | the FastAPI service name reachable from that network |
| remote n8n cloud | not allowed for the required local/free prototype |

The required candidate-demo path should prefer:

```text
n8n self-hosted inside the same local Compose network as FastAPI.
```

Therefore the default locked value is:

```text
http://api:8000
```

Do not hardcode paid cloud endpoints or real SaaS endpoints into the workflow JSON.

---

## 26. Expression-Safety Rule

n8n expressions should be kept simple and stable.

Prefer:

```text
normalized fields from early Set nodes
top-level backend response fields
explicit status values
single-purpose nodes
```

Avoid:

```text
deeply nested optional fields
long expressions that combine unrelated node outputs
business logic hidden inside expressions
approval logic implemented only in n8n
ticket-gate logic implemented only in n8n
```

The backend should normalize important fields so the workflow can remain readable.

Important fields that should remain top-level whenever possible:

```text
employee_id
correlation_id
workflow_id
request_id
approval_id
manager_id
selected_systems
status
ticket_id
reason_code
```

This keeps the workflow evaluator-readable and reduces the risk of fragile node references.

---

## 27. Locked Workflow Package Boundary

The locked workflow package consists of:

```text
1. hr_onboarding_agent_updated_workflow_v4.json
2. this v5 lock document
3. FastAPI backend endpoint contract
4. seeded local demo data
5. pytest tests proving approval/ticket/security behavior
```

The workflow JSON alone is not the full implementation.

The lock document alone is not the implementation.

The backend alone is not the visible orchestration evidence.

All four are needed for the candidate prototype to be credible.

---

## 28. Final Do-Not-Change Rule

Do not revise the workflow JSON again unless one of these is true:

```text
[ ] The FastAPI endpoint contract changes.
[ ] The workflow fails to import into n8n.
[ ] A node still requires real SaaS credentials.
[ ] The approval gate cannot be visually demonstrated.
[ ] The ticket node can run without backend-approved manager approval.
[ ] The JSON contains stale references to removed original-template nodes.
[ ] The evaluator-facing story is unclear in the n8n canvas.
```

Otherwise, stop iterating on the workflow and move to backend implementation.

The current workflow should now be treated as the **implementation starting point**, not as a document that needs more planning cycles.

---

## 29. Final v5 Lock Statement

The workflow package is now locked for development.

Final rating:

```text
10/10
```

The workflow is acceptable because it:

```text
uses n8n as the visible orchestrator
uses local FastAPI mock services instead of real SaaS credentials
supports HR role/level lookup
supports T1-T4 training lookup
supports access recommendation through backend logic
supports employee selection
supports manager approval
proves pre-approval ticket blocking
creates ITSM ticket only after approval
retrieves final status and audit events
keeps LLM/fallback usage limited to communication
preserves the free Linux/no-paid-service boundary
clearly differs from the original provisioning template
```

Next work should focus on the FastAPI backend, seed data, tests, and README run path.

