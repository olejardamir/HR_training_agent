# HR Onboarding Agent — Definition of Done, Mock Boundary, and Free Linux Stack

**Candidate exercise:** Enterprise Agent — Solutions Developer  
**Chosen scenario:** HR onboarding agent  
**Document version:** v4 — final locked Definition of Done  
**Purpose:** Define exactly what counts as complete, what is mocked, what is real, how the mocks behave, which technologies are used, and how the prototype can be run on Linux without paid services.  
**Source of requirements:** This Definition of Done implements the **HR use case** described in `Agent_Developer_Case_Study.pdf` (provided with the exercise).

---

## 1. Final Rating of the Previous Version

The previous v3 document rates **9.8/10**.

It was already strong enough to guide implementation, but it still had two small gaps:

1. It did not explicitly define a hard **no-paid-service validation rule** for every runtime dependency.
2. It did not give a compact final **implementation evidence matrix** showing exactly what the evaluator should be able to inspect, run, and verify.

This v4 version closes those gaps and is the locked **10/10 Definition of Done** for the HR onboarding agent prototype.

---

## 2. Executive Definition of Done

The prototype is done when it can be run locally on Linux with free tools and no paid SaaS accounts, and it demonstrates this full workflow:

```text
new employee onboarding trigger
→ HR profile lookup
→ role, level, department, manager, and employment-status identification
→ onboarding task status check
→ training T1-T4 status check
→ role-level access policy lookup
→ same-role/same-level peer access comparison
→ deterministic access recommendation with reason codes
→ employee access selection
→ policy validation of selected systems
→ manager approval request
→ asynchronous approval / rejection / expiry handling
→ ITSM ticket creation only after approval
→ Slack-style employee and manager messages
→ PostgreSQL state persistence and audit logging
→ tests proving policy, approval, ticketing, recommendation, and error paths
```

The prototype is **not done** if it only shows generic employee onboarding automation. The submission must visibly show the differentiator:

```text
role-level access recommendation + peer-pattern comparison + manager approval gate + deterministic policy validation + auditability
```

---

## 3. Free Linux Technology Stack

All technologies must be usable locally on Linux without paid accounts.

| Layer | Technology | Required | Prototype role | Free/Linux status |
|---|---|---:|---|---|
| Operating system | Ubuntu 22.04+, Ubuntu 24.04+, Debian, Fedora, or similar Linux | Yes | Local runtime | Free |
| Container runtime | Docker Engine or Podman | Yes | Reproducible local services | Free local runtime options |
| Compose runner | Docker Compose or Podman Compose | Yes | Start multi-service stack | Free |
| Workflow orchestration | n8n self-hosted | Yes | Visual workflow, branching, orchestration, HTTP calls | Free to self-host for this prototype; describe as self-hosted/fair-code, not OSI-open-source |
| Backend API | Python 3.11+ with FastAPI | Yes | Mock SaaS APIs and local agent support API | Free/open-source |
| ASGI server | Uvicorn | Yes | Run FastAPI app | Free/open-source |
| Data validation | Pydantic | Yes | Request/response schemas | Free/open-source |
| Database | PostgreSQL | Yes | Persistent workflow state, approvals, tickets, messages, audit log | Free/open-source |
| DB layer | SQLAlchemy + psycopg | Yes | Persistence access | Free/open-source |
| HTTP client | HTTPX | Yes | Internal API and LLM calls | Free/open-source |
| LLM runtime | Ollama | Yes, with fallback | Local message generation | Free local runtime |
| LLM model | Small local model such as Gemma 2B, Llama 3.1 8B, or Mistral 7B | Optional if fallback enabled | Human-readable messages | Free local use subject to model license |
| Tests | pytest | Yes | Verification | Free/open-source |
| Configuration | `.env` and `.env.example` | Yes | Local config | Free |
| API docs | FastAPI Swagger UI | Yes | Manual verification | Included with FastAPI |
| Version control | Git | Yes | Submission history | Free/open-source |

### Required local stack

```text
n8n + FastAPI + PostgreSQL + Ollama-or-deterministic-fallback + Docker/Podman + pytest
```

### Explicitly not required

The runnable prototype must not require:

```text
paid n8n Cloud
Workato
Zapier
real Slack credentials
real Jira / ServiceNow credentials
real Salesforce credentials
real Workday / BambooHR / HiBob / SuccessFactors credentials
real Okta / Microsoft Entra ID credentials
paid OpenAI / Gemini / Azure OpenAI API
Kubernetes
managed cloud services
```

A paid or enterprise service may be mentioned only as a **production extension**, not as a requirement for running the prototype.

---

## 4. Runtime Services and Ports

| Service | Default port | Required evidence |
|---|---:|---|
| n8n | 5678 | UI opens locally; workflow imports and runs. |
| FastAPI API | 8000 | `GET /health` returns healthy; `/docs` opens. |
| PostgreSQL | 5432 | Schema is created; seed data loads; state persists. |
| Ollama | 11434 | Message generation works, or fallback mode is explicitly logged. |

Minimum startup commands:

```bash
cp .env.example .env
docker compose up --build
pytest -q
```

Podman alternative:

```bash
cp .env.example .env
podman compose up --build
pytest -q
```

The project is not complete if the reviewer must create external SaaS accounts, API keys, cloud projects, or paid subscriptions to run the core demo.

---

## 5. Prototype Acceptance Boundary

This table is the strict boundary for what must be real, what may be mocked, and what must be documented as production-only.

| Capability | Prototype implementation | Mocked or real? | Production equivalent |
|---|---|---:|---|
| Workflow orchestration | n8n workflow export | Real | n8n, Workato, Temporal, Airflow, or enterprise workflow platform |
| HR employee source | FastAPI HR mock + PostgreSQL fixtures | Mocked but stateful | Workday, BambooHR, HiBob, SuccessFactors, internal HRIS |
| Slack messages | FastAPI Slack mock + message table | Mocked but stateful | Slack API with approved bot scopes |
| Training status | FastAPI LMS mock + T1-T4 table | Mocked but stateful | LMS API, Workday Learning, Docebo, Cornerstone |
| Salesforce setup | Fixture or FastAPI endpoint | Mocked | Salesforce REST API / permission-set workflow |
| Access recommendation | Local deterministic recommender | Real prototype logic | Policy service / IAM governance engine |
| Peer-pattern comparison | Local fixture + calculation | Real prototype logic over mocked data | HRIS/IAM/warehouse-derived access analytics |
| Manager approval | FastAPI approval state machine | Real prototype logic | Slack approval, ITSM approval, email approval, or IAM approval workflow |
| IT ticket creation | FastAPI ITSM mock + ticket table | Mocked but stateful | Jira Service Management, ServiceNow, Zendesk, internal ticketing |
| Access granting | Not implemented | Not implemented | SCIM / IAM / manual IT fulfillment |
| LLM messages | Ollama or deterministic fallback | Real local behavior | Approved enterprise LLM endpoint or self-hosted model |
| Audit log | PostgreSQL audit table | Real prototype behavior | SIEM, GRC system, central audit store |
| Tests | pytest | Real | CI/CD regression suite |

The prototype **creates mocked IT tickets**. It does **not** grant real system access.

---

## 6. No-Paid-Service Validation Rule

The prototype is acceptable only if it can be run on Linux without paid SaaS accounts, paid APIs, paid LLM keys, or proprietary cloud dependencies.

This means:

```text
No Slack workspace is required.
No Salesforce org is required.
No Workday/BambooHR/HiBob account is required.
No Jira Service Management, ServiceNow, or Zendesk account is required.
No Okta or Microsoft Entra tenant is required.
No OpenAI, Gemini, Anthropic, or hosted LLM key is required.
No cloud database is required.
No paid n8n cloud account is required.
```

The local implementation must use:

```text
self-hosted n8n
FastAPI mocked SaaS services
PostgreSQL running locally in a container
Ollama running locally, or deterministic fallback text if the local model is unavailable
pytest for automated verification
Docker Compose or Podman Compose for runtime setup
```

External providers may be mentioned only as **production replacements**. They must not be required for the prototype to run.

---

## 7. Runtime Dependency Decision Table

| Dependency | Allowed in prototype? | Required to run? | Notes |
|---|---:|---:|---|
| n8n self-hosted | Yes | Yes | Main visible workflow layer |
| n8n Cloud | No | No | Do not require a paid hosted account |
| FastAPI | Yes | Yes | Local mock SaaS/API layer |
| PostgreSQL local container | Yes | Yes | Persistent state and audit evidence |
| Slack real API | No | No | Replace with Slack mock endpoint |
| Salesforce real API | No | No | Replace with Salesforce mock endpoint |
| HRIS real API | No | No | Replace with HR mock endpoint |
| LMS real API | No | No | Replace with training mock endpoint |
| ITSM real API | No | No | Replace with ticketing mock endpoint |
| Okta / Entra real API | No | No | Mention only as production path |
| Ollama local | Yes | Preferred | Used only for message generation |
| Deterministic text fallback | Yes | Yes | Required fallback when Ollama/model is unavailable |
| OpenAI/Gemini/Anthropic API | Optional production note only | No | Do not require API keys |
| Docker/Podman | Yes | Yes | Free Linux runtime |

---


## 8. Mock Boundary

### Mocked systems

| Mocked system | Mock mechanism | Required behavior |
|---|---|---|
| HR Platform | FastAPI endpoints + PostgreSQL/fixtures | Return employee role, level, department, manager, status, and profile-completion state. |
| Slack | FastAPI endpoint + `slack_messages` table | Store employee and manager messages with recipient, type, content, metadata, and status. |
| Training/LMS | FastAPI endpoints + `training_status` table | Return and update T1-T4 completion state. |
| ITSM/Jira/ServiceNow | FastAPI endpoint + `itsm_tickets` table | Create a ticket only after approval; prevent duplicate tickets. |
| Salesforce | Fixture or endpoint | Represent role-relevant setup/access state. |
| Identity provider | Optional fixture/endpoint | Represent future Okta/Entra/SCIM path; not required for actual provisioning. |
| Manager approval | FastAPI endpoints + `manager_approvals` table | Support pending, approved, rejected, expired, and ticket-created states. |

### Not mocked because it is real local logic

```text
access recommendation algorithm
policy validation
approval state machine
ticket gate
audit logging
test suite
n8n orchestration
FastAPI service behavior
PostgreSQL persistence
LLM/fallback message generation behavior
```

### Not implemented at all

```text
real Slack API calls
real ServiceNow/Jira ticket creation
real Salesforce provisioning
real Workday/BambooHR/HiBob/SuccessFactors integration
real Okta/Microsoft Entra ID provisioning
real SCIM provisioning
real SAML/OIDC enterprise SSO
real production RBAC administration
real employee access grants
real HR data processing
real secrets manager
real SIEM/GRC integration
formal SOC 2, ISO 27001, ISO 42001, GDPR, or PIPEDA compliance
```

---

## 9. Mock Fidelity Levels

| Level | Meaning | Required use |
|---:|---|---|
| Level 1 | Static JSON fixture only | Acceptable for Salesforce and optional identity-provider placeholder. |
| Level 2 | Stateful mock backed by PostgreSQL | Required for HR, Slack, Training, Approvals, ITSM tickets. |
| Level 3 | Failure-capable mock with controlled error cases | Required for unknown employee, missing manager, forbidden access, ITSM failure, LLM unavailable. |
| Level 4 | Production-shaped adapter boundary | Recommended for HR, Slack, ITSM, LMS, and identity production path. |

Definition of Done requires Level 2 for all core mocks and Level 3 for critical failure paths.

---

## 10. Candidate Exercise Requirement Coverage

| Exercise requirement | Required evidence |
|---|---|
| Design autonomous/chat-based HR agent | n8n workflow plus FastAPI endpoints demonstrate guided autonomous onboarding flow. |
| Identify employee level and role | HR mock returns role, level, department, manager, and employee status. |
| Guide through onboarding tasks | Workflow shows HR profile, Slack profile, Salesforce setup, and T1-T4 training status. |
| Update personal information on Slack, HR Platform, Salesforce, etc. | Mock endpoints or fixtures represent profile-update state for HR, Slack, and Salesforce-style setup. |
| Complete onboarding training T1-T4 | Training mock exposes T1-T4 status and update behavior. |
| Request access needed for job role-level | Recommender uses role-level policy and peer-pattern data. |
| Assess employees with same role and level | Peer-pattern fixture stores same-role/same-level common access. |
| Let employee choose systems | `POST /onboarding/select-access` records selected systems. |
| Require manager approval | Approval gate blocks ticket creation until manager approval. |
| Handle asynchronous approval | Approval can remain pending, be approved later, rejected, or expired. |
| Answer tailored questions | LLM/fallback message service uses supplied role/task context. |
| Integrate at least two SaaS platforms | At least HR, Slack, Training, and ITSM are represented through mock APIs. |
| Use LLM or rules-based fixtures | Rules perform policy; LLM/fallback generates messages. |
| Demonstrate orchestration | n8n visibly controls branching, HTTP calls, approval path, and error branch. |
| Demonstrate reliability/security | Tests, audit log, approval gate, policy gate, structured errors, and PII minimization. |

---

## 11. Core Workflow Definition of Done

The happy-path workflow is complete when this sequence works end-to-end:

```text
1. Trigger onboarding for emp_001.
2. Load employee profile from HR mock.
3. Extract role, level, department, manager, and employment status.
4. Load training status for T1, T2, T3, T4.
5. Load role-level access policy.
6. Load peer access pattern for the same role and level.
7. Generate deterministic recommendations with reason codes.
8. Generate employee-facing onboarding summary through Ollama or fallback text.
9. Record Slack-style employee message.
10. Employee selects systems.
11. Validate selected systems against policy.
12. Create manager approval request.
13. Keep ticket creation blocked while approval is pending.
14. Approve as manager.
15. Create ITSM ticket with selected systems.
16. Record all major steps in audit log.
17. Show final onboarding status.
```

The workflow fails Definition of Done if ticket creation can occur before manager approval.

---

## 12. n8n Workflow Definition of Done

The n8n workflow is complete when it contains these nodes or equivalent steps:

```text
[ ] Manual trigger or webhook representing new employee onboarding
[ ] HTTP request: fetch employee profile from HR mock
[ ] HTTP request: fetch training status
[ ] HTTP request: fetch access recommendations
[ ] LLM step or HTTP call: generate onboarding summary
[ ] HTTP request: send employee message to Slack mock
[ ] HTTP request: create approval request
[ ] Conditional branch: approval pending / approved / rejected
[ ] HTTP request: create ITSM ticket only when approved
[ ] HTTP request: retrieve or write audit events
[ ] Error branch: failed mock API call produces clear status and audit event
```

The n8n workflow export is complete when:

```text
[ ] `n8n/hr_onboarding_workflow.json` exists
[ ] workflow imports into local n8n
[ ] local API URLs use environment variables or documented defaults
[ ] workflow can run after `docker compose up --build`
[ ] demo notes explain the main path and failure paths
```

---

## 13. FastAPI Mock API Definition of Done

The FastAPI service is complete when:

```text
[ ] `GET /health` returns healthy status
[ ] `/docs` opens Swagger UI
[ ] all mock endpoints are visible in Swagger UI
[ ] Pydantic schemas define request and response bodies
[ ] PostgreSQL connection works
[ ] database seeding works
[ ] structured errors are returned
[ ] audit events are written for important actions
[ ] no external SaaS credentials are required
[ ] service runs inside Docker or Podman
```

Minimum endpoint list:

```text
GET  /health
POST /demo/reset
POST /onboarding/start/{employee_id}
POST /onboarding/select-access
GET  /onboarding/status/{employee_id}
GET  /mock/hr/employees/{employee_id}
PATCH /mock/hr/employees/{employee_id}/profile
GET  /mock/training/status/{employee_id}
PATCH /mock/training/status/{employee_id}/modules/{module_id}
POST /mock/slack/messages
POST /mock/approvals
GET  /mock/approvals/{approval_id}
POST /mock/approvals/{approval_id}/approve
POST /mock/approvals/{approval_id}/reject
POST /mock/approvals/{approval_id}/expire
GET  /mock/access/recommendations/{employee_id}
POST /mock/llm/messages
POST /mock/itsm/tickets
GET  /audit/events
```

---

## 14. Mock Data Contracts

### 12.1 HR employee fixture

```json
{
  "employee_id": "emp_001",
  "name": "Maya Chen",
  "email": "maya.chen@example.test",
  "role": "Account Executive",
  "level": "L2",
  "department": "Sales",
  "manager_id": "mgr_101",
  "start_date": "2026-07-01",
  "employment_status": "new_hire",
  "profile_status": {
    "hr_profile_complete": true,
    "slack_profile_complete": false,
    "salesforce_profile_complete": false
  }
}
```

Done when known employees load successfully, unknown employees return a structured error, and missing manager data can be tested.

### 12.2 Training status fixture

```json
{
  "employee_id": "emp_001",
  "modules": [
    {"module_id": "T1", "title": "Security Basics", "status": "complete"},
    {"module_id": "T2", "title": "HR Policies", "status": "incomplete"},
    {"module_id": "T3", "title": "Sales Tools", "status": "incomplete"},
    {"module_id": "T4", "title": "Advanced Role Training", "status": "not_required_yet"}
  ]
}
```

Done when T1-T4 status appears in the onboarding summary and missing records are handled.

### 12.3 Role-level access policy fixture

```json
{
  "role": "Account Executive",
  "level": "L2",
  "required_systems": ["Slack", "HR Platform"],
  "recommended_systems": ["Salesforce", "Gong", "Outreach", "Sales Slack Channels"],
  "forbidden_systems": ["Payroll Admin", "Production Database Admin"]
}
```

Done when forbidden systems are blocked before approval request.

### 12.4 Peer access pattern fixture

```json
{
  "role": "Account Executive",
  "level": "L2",
  "peer_count": 8,
  "common_access": [
    {"system": "Salesforce", "frequency": 8},
    {"system": "Gong", "frequency": 7},
    {"system": "Outreach", "frequency": 6},
    {"system": "Sales Slack Channels", "frequency": 8}
  ]
}
```

Done when recommendation reasons distinguish required, recommended-by-policy, and common-among-peers.

### 12.5 Slack message request

```json
{
  "channel_or_user": "maya.chen@example.test",
  "message_type": "onboarding_summary",
  "message": "Your onboarding checklist is ready...",
  "metadata": {
    "employee_id": "emp_001",
    "workflow_id": "wf_001"
  }
}
```

Done when employee and manager messages are stored and visible.

### 12.6 Approval state machine

```text
PENDING → APPROVED → TICKET_CREATED
PENDING → REJECTED → CLOSED_NO_TICKET
PENDING → EXPIRED → CLOSED_NO_TICKET
```

Done when pending, rejected, and expired approvals block ticket creation, while approved approvals allow exactly one ticket.

### 12.7 ITSM ticket request

```json
{
  "employee_id": "emp_001",
  "approval_id": "apr_001",
  "requested_systems": ["Salesforce", "Gong", "Sales Slack Channels"],
  "requested_by": "hr-onboarding-agent",
  "manager_id": "mgr_101",
  "idempotency_key": "emp_001:req_5001:7ac43d"
}
```

Done when ticket creation persists ticket ID, selected systems, approval ID, queue/status, and duplicate-prevention metadata.

---

## 15. PostgreSQL Definition of Done

The database is complete when it stores these tables or equivalent schemas:

```text
employees
training_status
role_access_policies
peer_access_patterns
onboarding_sessions
selected_access_requests
manager_approvals
itsm_tickets
slack_messages
audit_events
```

Minimum audit event fields:

```text
event_id
created_at
workflow_id
employee_id
event_type
actor_type
actor_id
action
status
reason_code
correlation_id
metadata_json
```

Done when:

```text
[ ] audit events are written for every major workflow step
[ ] workflow state survives service restart
[ ] approval state survives service restart
[ ] duplicate ticket prevention uses persisted state
[ ] demo reset can clear and reseed the database
```

---

## 16. Access Recommendation Definition of Done

The recommender is complete when it produces deterministic output like this:

```json
{
  "employee_id": "emp_001",
  "role": "Account Executive",
  "level": "L2",
  "recommendations": [
    {
      "system": "Salesforce",
      "recommendation_type": "recommended",
      "reason_codes": ["ROLE_LEVEL_POLICY", "PEER_COMMON_ACCESS"],
      "peer_frequency": 8,
      "requires_manager_approval": true
    },
    {
      "system": "Slack",
      "recommendation_type": "required",
      "reason_codes": ["BASE_ONBOARDING_REQUIRED"],
      "requires_manager_approval": false
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

Done when recommendations are explainable without relying on the LLM.

---

## 17. LLM Definition of Done

The LLM is complete when it is used only for communication and never for authorization.

Allowed LLM tasks:

```text
generate employee onboarding summary
generate manager approval request message
generate explanation of why systems were recommended
answer low-risk onboarding questions using supplied role/task context
generate reminder text
```

Forbidden LLM tasks:

```text
approve access
grant access
invent role-level access rules
override policy engine
change manager approval status
create ticket without approval
use hidden HR data not supplied in prompt
use secrets or credentials
make legal/compliance promises
```

Done when:

```text
[ ] Ollama endpoint is configurable
[ ] model name is configurable
[ ] deterministic fallback text exists if Ollama is unavailable
[ ] prompts include only minimum necessary employee data
[ ] LLM output is not used as authorization evidence
[ ] LLM output is logged as generated communication, not policy decision
```

---

## 18. Security, Governance, and Privacy Definition of Done

The prototype is complete when it demonstrates these controls:

```text
[ ] least privilege: the agent requests access; it does not grant access
[ ] manager approval is mandatory before ticket creation
[ ] forbidden systems are blocked by deterministic policy
[ ] employee-selected systems are validated before approval request
[ ] no secrets are stored in source code
[ ] `.env.example` contains placeholders only
[ ] prompts minimize personal data
[ ] audit log records recommendations, selections, approvals, rejections, and ticket outcomes
[ ] errors do not expose secrets or unnecessary personal data
[ ] prototype clearly states that it is not formally certified under SOC 2, ISO 27001, ISO 42001, GDPR, or PIPEDA
```

External standards/frameworks may be referenced only as alignment, not certification:

```text
NIST AI RMF: AI risk management framing
OWASP Top 10 for LLM Applications: LLM-specific threat awareness
ISO/IEC 42001: AI management-system direction
SOC 2 Trust Services Criteria: enterprise control categories
SCIM 2.0: production provisioning path
OAuth 2.0 / OpenID Connect / SAML 2.0: production identity and authorization path
RBAC / ABAC: production access-control model
ITIL-style ITSM: production ticketing process alignment
GDPR-style principles: data minimization and purpose limitation
```

---

## 19. Error Handling Definition of Done

| Failure case | Required behavior | Test required |
|---|---|---:|
| Unknown employee | Structured error; no approval; no ticket | Yes |
| Missing manager | Blocked status; no approval; no ticket | Yes |
| Unknown role/level | Blocked or conservative recommendation; no unsafe defaults | Yes |
| Forbidden access selected | Reject forbidden system before approval request | Yes |
| Approval pending | Do not create ticket | Yes |
| Approval rejected | Close request without ticket | Yes |
| Approval expired | Close request without ticket | Yes |
| Duplicate approval | Do not create duplicate ticket | Yes |
| Duplicate ticket request | Return existing ticket or duplicate-blocked status | Yes |
| ITSM mock failure | Log failure and keep state recoverable | Yes |
| LLM unavailable | Use deterministic fallback message | Yes |
| Database unavailable | Return service error and do not claim workflow success | Yes |
| Slack mock failure | Log failed notification without corrupting approval/ticket state | Yes |

---

## 20. Test Definition of Done

The project is complete when `pytest -q` passes for at least these tests:

```text
[ ] test_known_employee_profile_loaded
[ ] test_unknown_employee_returns_error
[ ] test_missing_manager_blocks_workflow
[ ] test_training_status_loaded
[ ] test_access_recommendations_for_role_level
[ ] test_peer_pattern_recommendations_have_reason_codes
[ ] test_forbidden_access_is_blocked
[ ] test_employee_selection_creates_pending_approval
[ ] test_ticket_not_created_without_approval
[ ] test_ticket_created_after_approval
[ ] test_rejected_approval_blocks_ticket
[ ] test_expired_approval_blocks_ticket
[ ] test_duplicate_ticket_is_prevented
[ ] test_audit_log_records_major_events
[ ] test_llm_fallback_when_ollama_unavailable
[ ] test_slack_mock_records_message
[ ] test_demo_reset_reseeds_database
```

The project is not done if the workflow works only manually and the approval gate, ticket gate, recommender, and failure paths are untested.

---

## 21. Demo Definition of Done

The demo is complete when it can be shown in under five minutes.

### Demo path A — normal approval

```text
1. Start local stack.
2. Trigger onboarding for emp_001.
3. Show role and level loaded from HR mock.
4. Show training status T1-T4.
5. Show recommended access with reason codes.
6. Select systems.
7. Show approval is pending.
8. Approve as manager.
9. Show IT ticket created.
10. Show audit log entries.
```

### Demo path B — approval gate blocks action

```text
1. Trigger onboarding for emp_002.
2. Select systems.
3. Do not approve, or reject approval.
4. Show no IT ticket is created.
5. Show audit log records blocked/rejected outcome.
```

### Demo path C — forbidden system blocked

```text
1. Trigger onboarding for sales employee.
2. Attempt to request Payroll Admin or Production Database Admin.
3. Show policy engine blocks the request.
4. Show no approval or ticket is created for forbidden access.
```

---

## 22. Build Sequence Definition of Done

Build in this order:

```text
1. Create repository structure.
2. Create Docker/Podman compose file.
3. Create PostgreSQL service and schema.
4. Create FastAPI app with health endpoint.
5. Add fixture seeding and demo reset.
6. Add HR mock.
7. Add training mock.
8. Add access recommender and policy engine.
9. Add approval service.
10. Add ITSM ticket mock.
11. Add Slack message mock.
12. Add audit logger.
13. Add Ollama/fallback LLM service.
14. Add tests.
15. Create n8n workflow.
16. Write README and demo notes.
17. Export n8n workflow JSON.
18. Run full demo and final checks.
```

A build step is complete only when it is runnable, testable, and documented.

---

## 23. Repository Definition of Done

Final repository should contain:

```text
hr-onboarding-agent/
  README.md
  docker-compose.yml
  .env.example

  docs/
    solution_design.md
    definition_of_done.md
    demo_walkthrough.md
    mock_boundary.md
    standards_alignment.md

  n8n/
    hr_onboarding_workflow.json

  api/
    Dockerfile
    requirements.txt
    app/
      main.py
      config.py
      database.py
      models.py
      schemas.py
      seed.py
      services/
        hr_service.py
        training_service.py
        slack_service.py
        approval_service.py
        itsm_service.py
        llm_service.py
        audit_service.py
      logic/
        access_recommender.py
        policy_engine.py
      fixtures/
        employees.json
        training_status.json
        role_access_policies.json
        peer_access_patterns.json
    tests/
      test_employee_lookup.py
      test_training_status.py
      test_access_recommender.py
      test_approval_gate.py
      test_ticket_creation.py
      test_audit_log.py
      test_llm_fallback.py
```

---

## 24. README Definition of Done

README is complete when it includes:

```text
[ ] short project summary
[ ] why this is not just an n8n template
[ ] architecture diagram or text diagram
[ ] free Linux stack
[ ] install prerequisites
[ ] how to start services
[ ] how to import n8n workflow
[ ] how to run tests
[ ] how to run demo scenario
[ ] what is mocked
[ ] what is real
[ ] limitations
[ ] production extension path
```

---

## 25. Environment Variables Definition of Done

`.env.example` must contain only placeholder values:

```env
POSTGRES_DB=hr_onboarding
POSTGRES_USER=hr_agent
POSTGRES_PASSWORD=hr_agent_dev_password
DATABASE_URL=postgresql+psycopg://hr_agent:hr_agent_dev_password@postgres:5432/hr_onboarding
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=gemma2:2b
LLM_FALLBACK_ENABLED=true
N8N_HOST=localhost
N8N_PORT=5678
API_BASE_URL=http://api:8000
```

No real keys, tokens, passwords, or SaaS credentials should appear in the repository.

---

## 26. Anti-Template Differentiation Requirement

Because n8n already has employee-onboarding and IT Ops workflow examples, the prototype must not be presented as “onboarding automation” alone.

The README, solution design, and demo must explicitly show this distinction:

| Basic n8n onboarding template | This prototype must show |
|---|---|
| Creates onboarding tasks | Guides onboarding by role, level, department, and manager |
| Sends notifications | Generates tailored employee and manager messages |
| Creates accounts or tasks | Recommends access using role-level policy and peer-pattern comparison |
| Simple branch logic | Deterministic policy validation and approval state machine |
| May create IT task directly | Blocks IT ticket until manager approval |
| Limited evidence trail | Persistent audit log with reason codes |
| Workflow automation | Governed HR access-request agent |

The final project is not done unless the evaluator can see why it is more than a copied workflow template.

---

## 27. Evaluator Evidence Package

The final submission should include these evaluator-visible artifacts:

```text
[ ] 1-2 page solution design document
[ ] README.md with run commands
[ ] docker-compose.yml
[ ] FastAPI source code
[ ] PostgreSQL schema/seed logic
[ ] n8n workflow export JSON
[ ] pytest test suite
[ ] demo walkthrough notes
[ ] mock-boundary / Definition-of-Done document
```

Minimum evidence commands:

```bash
docker compose up --build
curl http://localhost:8000/health
pytest -q
```

Minimum evidence screenshots or demo views:

```text
n8n workflow canvas
FastAPI /docs
onboarding status for emp_001
manager approval state before and after approval
created ITSM ticket record
audit log entries
pytest passing output
```

---

## 28. Production Extension Path

| Prototype mock | Production replacement |
|---|---|
| HR Platform mock | Workday, BambooHR, HiBob, SuccessFactors, or internal HRIS API |
| Slack mock | Slack API with approved bot scopes |
| Training mock | LMS API such as Workday Learning, Docebo, Cornerstone, or internal training service |
| ITSM mock | Jira Service Management, ServiceNow, Zendesk, or internal ticketing API |
| Salesforce mock | Salesforce REST API and permission-set workflow |
| Identity Provider mock | Okta or Microsoft Entra ID |
| Local `.env` secrets | Vault, AWS Secrets Manager, Azure Key Vault, or equivalent |
| Local Ollama | Approved enterprise LLM endpoint or self-hosted model service |
| Docker Compose | Managed containers, Kubernetes, or enterprise workflow runtime |
| Local audit table | Central audit log, SIEM, or GRC evidence store |

Production must add:

```text
RBAC/ABAC policy store
SCIM provisioning where appropriate
SAML/OIDC identity integration
secrets manager
monitoring and alerting
rate limits and retries
data-retention policy
privacy review if applicable
formal access review process
human review and escalation path
```

---

## 29. Final Submission Boundary

The final candidate submission should include practical deliverables, not the entire planning archive.

Submit:

```text
1. solution_design.md or short PDF version, 1-2 pages
2. README.md
3. source code
4. docker-compose.yml
5. n8n workflow export JSON
6. test suite
7. demo walkthrough notes
```

Keep deeper planning documents as supporting material unless the evaluator asks for them.

---

## 30. Implementation Evidence Matrix

The evaluator should be able to verify completion from concrete files and runtime behavior.

| Evidence item | Required file or behavior | Done when |
|---|---|---|
| Local startup | `docker-compose.yml` or `compose.yml` | `docker compose up` starts n8n, FastAPI, PostgreSQL, and optional Ollama wiring |
| n8n workflow | `n8n/workflows/hr_onboarding_agent.json` | Workflow imports and shows the full role-level onboarding path |
| Mock APIs | `app/main.py` plus routers/services | HR, Slack, Training, Salesforce, Approval, and ITSM endpoints respond locally |
| Seed data | `seed/` or startup seed script | Includes employees, managers, peer access records, training status, and role-level policies |
| Recommendation logic | Access recommender service/module | Uses role, level, policy, and peer patterns; does not depend on LLM output |
| Approval gate | Approval service/module and n8n branch | Ticket creation is impossible without manager approval |
| ITSM ticket mock | Ticket endpoint and DB table | Approved selections create ticket records with stable IDs |
| Audit log | PostgreSQL `audit_events` table | Every major action is logged with timestamp, actor/system, event type, and result |
| LLM boundary | Message-generation service/module | LLM only writes summaries/messages; it does not approve or authorize access |
| Fallback behavior | Deterministic message fallback | Demo still works if Ollama is unavailable |
| Test suite | `tests/` | `pytest` passes for success, rejection, expiry, policy denial, duplicate ticket, and service-error paths |
| README | `README.md` | Explains local setup, ports, mocked services, demo flow, and known limits |
| Demo notes | `DEMO.md` or README section | Shows the evaluator exactly what to click/run and what result to expect |

---

## 31. Must-Run Verification Commands

The repository should expose a small verification path that works on Linux.

```bash
cp .env.example .env
docker compose up --build
pytest -q
```

The README should also include manual checks such as:

```text
Open n8n locally.
Import or open the HR onboarding workflow.
Run the seeded employee onboarding scenario.
Confirm role and level are detected.
Confirm access recommendations are produced.
Select requested systems.
Approve as manager.
Confirm ticket is created only after approval.
Inspect PostgreSQL audit events.
Run a rejection scenario and confirm no ticket is created.
Run a policy-denied system scenario and confirm it is blocked.
```

---

## 32. Final Acceptance Checklist

The prototype can be considered complete only if the answer is yes to all of these:

```text
[ ] Can someone run it locally on Linux without paid accounts?
[ ] Does n8n visibly orchestrate the workflow?
[ ] Are at least two SaaS-style integrations demonstrated through mock API calls?
[ ] Is the LLM used for message generation only?
[ ] Is access recommendation deterministic and explainable?
[ ] Is manager approval mandatory before ticket creation?
[ ] Is ticket creation blocked when approval is missing, rejected, or expired?
[ ] Are role and level used in the decision flow?
[ ] Are peer access patterns used for recommendation?
[ ] Are training tasks T1-T4 represented?
[ ] Are Slack/HR/Salesforce-style profile tasks represented?
[ ] Are audit logs stored?
[ ] Are error paths handled?
[ ] Do tests pass?
[ ] Is the mock boundary clear?
[ ] Is the production path clear?
[ ] Is the solution clearly different from a basic n8n onboarding template?
```

---

## 33. Final Definition of Done Statement

The HR onboarding agent prototype is done when it can be run locally on Linux without paid services, demonstrates the full role-level onboarding workflow through n8n, uses FastAPI mocked SaaS APIs, persists workflow and audit state in PostgreSQL, generates human-readable messages through local Ollama or deterministic fallback text, blocks IT ticket creation until manager approval, passes the test suite, and clearly documents what is mocked, what is real, and how the prototype would evolve into production integrations.
