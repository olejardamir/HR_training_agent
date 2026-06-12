# HR Onboarding Agent — Development Process Guide

**Candidate exercise:** Enterprise Agent — Solutions Developer  
**Chosen scenario:** HR onboarding agent  
**Document purpose:** Blind, high-level development guide from project setup to final submission  
**Scope:** Planning and execution sequence only; no code implementation  
**Target runtime:** Free local Linux stack  
**Primary stack:** n8n + FastAPI + PostgreSQL + Ollama or deterministic fallback + Docker/Podman Compose + pytest  
**Document version:** v4 — locked 10/10 development process guide  

---

## 0. Rating of Previous Version

**Previous v3 rating:** 9.8/10

The v3 guide was already strong enough to build the prototype. It defined the correct free Linux stack, the right backend-first build order, the mocked-vs-real boundary, milestone gates, no-paid-service rule, anti-overbuild controls, and final evidence checklist.

It was not fully 10/10 because it still needed four refinements:

- a clearer answer to the process question: whether to build a skeletal n8n workflow first, use a CLI, or build the backend smoke path first;
- stronger phase cards showing what to install, what to configure, what to prove, and when to stop;
- a more explicit evaluator-first delivery path so the final package is easy to review;
- a stricter high-level/no-code boundary so the guide cannot accidentally become an implementation spec.

**Updated v4 rating:** 10/10

This v4 document is the locked development-process guide. It gives a blind build path from an empty Linux machine to final submission, while staying high-level and avoiding implementation code.



## 1. Purpose of This Guide

This guide implements the **HR use case** from the provided `Agent_Developer_Case_Study.pdf`.

This guide explains how to build the HR onboarding agent prototype from zero to final submission.

It defines:

- what to install;
- what to configure;
- what to build first;
- when to introduce the database;
- when to introduce n8n;
- when to introduce the LLM;
- what must be mocked;
- what must be real prototype logic;
- what must be tested;
- what must be shown to the evaluator;
- what should not be built.

This document intentionally avoids source code. It is a professional implementation roadmap, not an implementation file.

The guide may name files, folders, commands, services, ports, test categories, and acceptance gates. It should not define Python functions, database migration scripts, n8n node JSON, prompt templates, or endpoint implementation bodies.

---

## 2. Final Build Philosophy

The best professional approach is:

```text
contracts first
→ local runtime skeleton
→ deterministic backend services
→ seeded mock data
→ API/README smoke path
→ approval and ticket gates
→ auditability
→ LLM/fallback messages
→ n8n orchestration
→ tests and failure paths
→ final submission package
```

Do **not** start by building a polished n8n canvas.

The reason is that the differentiating value is not basic onboarding automation. n8n already has public onboarding-style examples. The differentiating value is:

```text
role-level detection
same-role/same-level peer access recommendation
policy validation
manager approval gate
ticket creation only after approval
auditability
local free Linux execution
clear mock boundary
```

Therefore, build the reliable backend workflow first, prove it through API calls or tests, and then use n8n as the visible orchestration layer on top of stable services.

---

## 3. Recommended Execution Strategy

Use a **backend smoke-path first, skeletal n8n second, polished n8n last** approach.

The professional sequence is:

```text
1. Create repository and documentation skeleton.
2. Start local runtime skeleton: PostgreSQL + FastAPI health + n8n UI.
3. Create a tiny skeletal n8n workflow only to prove n8n can call the FastAPI health endpoint.
4. Do not polish n8n yet.
5. Build the deterministic FastAPI services and PostgreSQL state model.
6. Prove the workflow through API smoke steps and pytest.
7. Return to n8n and build the real onboarding workflow on stable endpoints.
8. Export the final n8n JSON.
9. Package README, demo notes, tests, and solution design.
```

This is better than starting with a large n8n canvas because the custom value of the project is not the canvas itself. The custom value is the governed access-recommendation and approval behavior behind the canvas.

### CLI decision

Do **not** build a full CLI.

Use:

```text
README commands
curl/httpie smoke checks
pytest
FastAPI Swagger UI
n8n workflow run
```

A small `make` target or shell smoke command is acceptable, but only as a convenience. The reviewer should not need to learn a custom CLI to understand the prototype.

### Skeletal workflow decision

Create one skeletal n8n workflow early, but keep it minimal:

```text
Manual Trigger → HTTP Request to GET /health → Success marker
```

Purpose:

```text
prove n8n imports/runs locally
prove n8n can reach FastAPI over the Compose network
prove the workflow layer is real, not theoretical
```

After that, pause n8n work until the backend services are stable. The final n8n workflow should be built on tested endpoints, not on unfinished assumptions.

---

## 4. Blind-Start Preflight

Before building anything, verify these assumptions:

```text
[ ] The chosen scenario is HR onboarding agent.
[ ] The prototype must run locally on Linux.
[ ] No paid SaaS accounts are allowed for the runnable demo.
[ ] n8n is the visible workflow/orchestration layer.
[ ] FastAPI provides mocked SaaS APIs.
[ ] PostgreSQL stores state and audit logs.
[ ] Ollama is preferred for local LLM messages, but deterministic fallback is required.
[ ] The LLM may generate messages but may not approve, authorize, or provision access.
[ ] The prototype creates mocked IT tickets only; it does not grant real access.
```

Stop if any of these assumptions are not true.

---

## 5. Technology Inventory and Install Timing

All technologies must be free and usable on Linux.

| Layer | Technology | Install timing | Role |
|---|---|---:|---|
| Version control | Git | First | Repository history and submission control |
| Container runtime | Docker Engine or Podman | First | Local service runtime |
| Compose runner | Docker Compose or Podman Compose | First | Multi-service startup |
| Language runtime | Python 3.11+ | First | FastAPI service and tests |
| Backend API | FastAPI | Backend phase | Mock SaaS APIs and local agent services |
| API server | Uvicorn | Backend phase | Run FastAPI |
| Data validation | Pydantic | Backend phase | Request/response contracts |
| Database | PostgreSQL | Runtime phase | State, approvals, tickets, audit logs |
| DB access | SQLAlchemy + psycopg | Backend phase | Persistence layer |
| Workflow | n8n self-hosted | Orchestration phase | Visual workflow and branching |
| LLM runtime | Ollama | LLM phase | Local message generation |
| LLM fallback | Deterministic text templates | LLM phase | Required when Ollama is unavailable |
| Tests | pytest | Testing phase | Verification |
| Manual checks | curl or httpie | Smoke-test phase | API verification |
| Documentation | Markdown | Whole project | README and deliverables |

Required local runtime:

```text
Docker/Podman Compose
FastAPI
PostgreSQL
n8n
Ollama or deterministic fallback
pytest
```

---

## 6. Install and Runtime Boundary

### Install directly on the Linux host

Install or verify:

```text
Git
Docker Engine or Podman
Docker Compose or Podman Compose
Python 3.11+
curl or httpie
Make or shell task support, optional
```

### Run through Compose

Run these as local services:

```text
PostgreSQL
FastAPI API service
n8n self-hosted
optional Ollama service or host-connected Ollama
```

### Keep optional

These are useful but must not be required:

```text
VS Code
DBeaver or pgAdmin
Postman or Insomnia
Mermaid preview
host-installed Ollama
```

### Never require

The prototype must not require:

```text
n8n Cloud
Slack workspace
Salesforce org
Jira or ServiceNow account
Workday/BambooHR/HiBob account
Okta or Microsoft Entra tenant
OpenAI/Gemini/Anthropic API key
cloud database
Kubernetes
paid SaaS subscription
```

---

## 7. Phase Cards: What to Install, Do, Prove, and Stop On

Use these cards as the blind execution guide.

### Phase 0 — Machine and repository readiness

| Item | Decision |
|---|---|
| Install/verify | Git, Docker or Podman, Compose runner, Python 3.11+, curl/httpie |
| Do | Create repository, README shell, docs folder, `.env.example`, compose placeholder |
| Prove | Repository opens cleanly; README states free Linux boundary |
| Stop/go gate | Do not continue until the runtime choice is fixed: Docker Compose primary or Podman Compose primary |

### Phase 1 — Local runtime skeleton

| Item | Decision |
|---|---|
| Install/verify | PostgreSQL container, FastAPI container, n8n container |
| Do | Start services locally; expose default ports; confirm health endpoint and n8n UI |
| Prove | `GET /health` works; n8n UI opens; PostgreSQL accepts connections |
| Stop/go gate | Do not build business logic until local services start from one documented command |

### Phase 2 — Skeletal n8n connectivity

| Item | Decision |
|---|---|
| Install/verify | n8n can call FastAPI inside the local network |
| Do | Create minimal n8n workflow: manual trigger → health-check HTTP request |
| Prove | Workflow runs successfully and can be exported |
| Stop/go gate | Do not expand the n8n canvas until the backend API contracts are stable |

### Phase 3 — Contracts and seed data

| Item | Decision |
|---|---|
| Install/verify | Pydantic, SQLAlchemy/psycopg, pytest |
| Do | Define endpoint list, fixture names, state tables, and seed/reset behavior at a planning level |
| Prove | Demo employee, manager, role-level policy, peer access pattern, and training records are defined |
| Stop/go gate | Do not start recommendation logic until role, level, manager, policy, and peer-pattern data are available |

### Phase 4 — Deterministic onboarding logic

| Item | Decision |
|---|---|
| Install/verify | FastAPI service dependencies and database access |
| Do | Build HR lookup, training lookup, access recommendation, forbidden-system validation |
| Prove | Recommendations include reason codes and do not depend on LLM output |
| Stop/go gate | Do not add LLM or n8n complexity until recommendation and policy checks work deterministically |

### Phase 5 — Approval, ticket, and audit behavior

| Item | Decision |
|---|---|
| Install/verify | PostgreSQL state persistence and test runner |
| Do | Add selection state, manager approval state, ITSM ticket mock, idempotency, audit events |
| Prove | Ticket creation is impossible before approval and exactly one ticket is created after approval |
| Stop/go gate | Do not call the workflow complete unless pending, approved, rejected, expired, forbidden, and duplicate paths are covered |

### Phase 6 — LLM/fallback message layer

| Item | Decision |
|---|---|
| Install/verify | Ollama local runtime or deterministic fallback mode |
| Do | Add employee summary and manager approval-message generation |
| Prove | The demo works when Ollama is available and still works through fallback when it is unavailable |
| Stop/go gate | Do not let LLM output authorize access, change approval state, or create tickets |

### Phase 7 — Full n8n workflow

| Item | Decision |
|---|---|
| Install/verify | Stable API endpoints and demo fixtures |
| Do | Build the real n8n workflow on top of tested backend services |
| Prove | n8n shows role/level lookup, recommendations, selection, approval wait, ticket creation, and audit path |
| Stop/go gate | Do not polish screenshots before the workflow runs end-to-end |

### Phase 8 — Final evaluator package

| Item | Decision |
|---|---|
| Install/verify | README run path, tests, workflow export, docs |
| Do | Prepare concise solution design, demo walkthrough, standards alignment, mock boundary, and final evidence screenshots if needed |
| Prove | A reviewer can run or understand the project without the original conversation |
| Stop/go gate | Do not submit the full planning archive as the main deliverable |

## 8. Core Development Decisions

### 6.1 Docker or Podman

Use Docker Compose as the primary path unless the developer’s Linux environment prefers Podman.

Document both only if easy:

```text
Primary: docker compose up --build
Alternative: podman compose up --build
```

Do not spend time optimizing for both if the deadline is tight. One working free Linux path is enough, but the no-paid-service boundary must remain true.

### 6.2 Ollama or fallback

Use this rule:

```text
Try Ollama for local message generation.
Always implement deterministic fallback text.
Never require a paid hosted LLM key.
```

If hardware is weak, fallback text is acceptable for the demo as long as the LLM boundary is documented.

### 6.3 CLI or no CLI

Use this rule:

```text
Do not build a large CLI.
Use README curl/httpie smoke steps and pytest integration tests.
Create a tiny CLI only if time remains and it reduces demo friction.
```

The evaluator will care more about:

```text
local stack starts
FastAPI docs open
n8n workflow runs
tests pass
approval gate works
audit log is visible
```

A CLI is optional, not a core deliverable.

### 6.4 n8n first or backend first

Use this rule:

```text
Build backend contracts and smoke path first.
Then build n8n orchestration.
Do not build n8n first.
```

This avoids creating a nice-looking workflow that lacks reliable business logic.

---

## 9. Development Principles

Use these principles throughout the build.

### 7.1 Mock external systems, not core logic

Mock these systems:

```text
HR platform
Slack
Training/LMS
Salesforce
ITSM/ticketing
identity provider placeholder
manager approval interface
```

Do **not** mock these behaviors:

```text
access recommendation
policy validation
approval state machine
ticket gate
audit logging
idempotency
test suite
n8n orchestration
LLM/fallback message generation behavior
```

### 7.2 Keep the LLM bounded

The LLM may generate:

```text
employee onboarding summaries
manager approval request messages
recommendation explanations
safe onboarding question responses
reminder text
```

The LLM must not:

```text
approve access
grant access
invent policy
override manager approval
create tickets without approval
change employee role or level
change manager identity
make legal or compliance claims
```

### 7.3 Build evidence as you go

Every major phase must leave evidence:

```text
a running service
a documented endpoint
seeded demo data
a passing test
an audit event
a README/demo note
```

Do not defer all proof to the end.

---

## 10. Professional Milestone Gates

Stop at each gate until the required evidence exists.

| Gate | Name | Required evidence before moving on |
|---:|---|---|
| G0 | Project foundation | Repo structure, README skeleton, `.env.example`, docs folder |
| G1 | Runtime starts | PostgreSQL, FastAPI health, and n8n local UI available |
| G2 | Contracts locked | Mock boundary, endpoint list, data contracts, and Definition of Done documented |
| G3 | Seed data works | Demo reset and seeded employee/training/policy data available |
| G4 | Core logic works | Recommendation, selection validation, approval gate, and ticket gate work through API/smoke path |
| G5 | Governance works | Audit events, reason codes, idempotency, and blocked states visible |
| G6 | LLM boundary works | Ollama or fallback generates messages; authorization does not depend on LLM output |
| G7 | n8n orchestration works | Workflow imports, calls local endpoints, and branches on approval and error states |
| G8 | Tests pass | pytest covers happy path and critical failure paths |
| G9 | Submission ready | README, solution design, demo notes, standards alignment, workflow export, and run commands complete |

A gate is complete only when the evidence can be run or inspected.

---

## 11. Recommended Repository Structure

Create this structure early:

```text
hr-onboarding-agent/
  README.md
  docker-compose.yml
  .env.example
  Makefile or task-notes.md

  docs/
    solution_design.md
    definition_of_done.md
    development_process.md
    mock_boundary.md
    standards_alignment.md
    demo_walkthrough.md
    deliverable_mapping.md
    traceability_matrix.md

  n8n/
    hr_onboarding_workflow.json
    screenshots/

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
      logic/
      fixtures/
    tests/
```

Keep names simple. The reviewer should immediately understand where to look.

---

## 12. Phase 0 — Project Setup

### Goal

Create the project foundation.

### Install or verify

```text
Git
Docker or Podman
Compose runner
Python 3.11+
curl/httpie
```

### Create

```text
repository folder
README.md placeholder
docs/ folder
api/ folder
n8n/ folder
.env.example
docker-compose.yml placeholder
```

### Lock decisions

Document:

```text
primary runtime: Docker Compose or Podman Compose
default ports
API base URL
n8n base URL
database name
Ollama container or host mode
fallback behavior if Ollama is unavailable
```

### Exit gate

```text
[ ] repo exists
[ ] folder structure exists
[ ] README names the scenario and stack
[ ] .env.example exists
[ ] no real credentials are present
```

---

## 13. Phase 1 — Contracts and Mock Boundary

### Goal

Define the system before implementation.

### Create documents

```text
docs/mock_boundary.md
docs/definition_of_done.md
docs/development_process.md
docs/traceability_matrix.md
docs/standards_alignment.md
```

### Classify mocked systems

| Mocked system | Required behavior |
|---|---|
| HR Platform | employee role, level, department, manager, profile state |
| Training/LMS | T1-T4 completion status |
| Slack | stored employee and manager messages |
| Salesforce | role-relevant profile/access target |
| Approval | pending, approved, rejected, expired |
| ITSM | ticket creation after approval only |
| Audit | workflow events and correlation IDs |

### Classify real prototype logic

```text
access recommender
policy engine
approval state machine
ticket gate
audit logger
LLM/fallback message service
test suite
n8n orchestration
```

### Lock high-level data contracts

Document shapes for:

```text
employee profile
training status
role-level access policy
peer access pattern
access recommendation
employee selection
approval request
ticket request
audit event
```

### Exit gate

```text
[ ] every external system is classified as mocked or production-only
[ ] every internal decision component is classified as real prototype logic
[ ] endpoint list is documented
[ ] data contracts are documented
[ ] Definition of Done is clear
```

---

## 14. Phase 2 — Compose Runtime Skeleton

### Goal

Create a local runtime shell before business logic.

### Add services

```text
PostgreSQL
FastAPI API service
n8n
Ollama or documented fallback/host connection
```

### Default ports

```text
FastAPI: 8000
n8n: 5678
PostgreSQL: 5432
Ollama: 11434
```

### Environment placeholders

`.env.example` should include placeholders for:

```text
DATABASE_URL
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
API_BASE_URL
N8N_HOST
N8N_PORT
LLM_PROVIDER
OLLAMA_BASE_URL
OLLAMA_MODEL
LLM_FALLBACK_ENABLED
```

### Exit gate

```text
[ ] compose file exists
[ ] services start locally
[ ] n8n opens locally
[ ] FastAPI container is ready for health endpoint
[ ] PostgreSQL starts
[ ] no paid service is required
```

---

## 15. Phase 3 — FastAPI Skeleton

### Goal

Create the backend shell.

### Build at a high level

```text
FastAPI app entrypoint
configuration loader
health endpoint
database connection placeholder
Swagger/OpenAPI docs
structured error format
```

### First visible endpoints

```text
GET /health
POST /demo/reset
GET /audit/events
```

### Exit gate

```text
[ ] GET /health returns healthy
[ ] /docs opens
[ ] API starts through Compose
[ ] pytest can run a smoke test
[ ] README includes local API URL
```

---

## 16. Phase 4 — Database Schema and Seed Data

### Goal

Make the prototype stateful.

### Required tables or equivalent models

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

### Required seed scenarios

```text
emp_001: happy path employee
emp_002: pending/rejection path employee
emp_003: missing manager path
emp_004: unsupported role-level path
```

### Required role-level examples

```text
Account Executive L2
Software Engineer L2
HR Coordinator L1
Manager L3
```

### Required restricted systems

```text
Payroll Admin
Production Database Admin
Security Admin
Finance Admin
```

### Exit gate

```text
[ ] database schema exists
[ ] seed data loads
[ ] demo reset works
[ ] data persists across restart unless reset is called
[ ] no external data source is needed
```

---

## 17. Phase 5 — HR and Training Mocks

### Goal

Build the first SaaS-style integrations.

### HR mock behavior

```text
return employee profile
return role and level
return department
return manager
return profile-completion state
return structured error for unknown employee
return blocked status for inactive employee
```

### Training mock behavior

```text
return T1-T4 status
support fixture update if needed
handle missing training record
```

### Exit gate

```text
[ ] HR endpoint returns emp_001 profile
[ ] training endpoint returns T1-T4 status
[ ] unknown employee returns structured error
[ ] tests cover known and unknown employee lookup
```

---

## 18. Phase 6 — Access Policy and Peer Recommendation

### Goal

Build the main differentiating logic.

### Inputs

```text
employee role
employee level
department
role-level access policy
same-role/same-level peer access pattern
restricted systems list
```

### Outputs

```text
required systems
recommended systems
optional systems
blocked systems
reason codes
peer frequency where applicable
policy version
```

### Required reason codes

```text
BASE_ONBOARDING_REQUIRED
ROLE_LEVEL_POLICY
PEER_COMMON_ACCESS
DEPARTMENT_STANDARD
FORBIDDEN_FOR_ROLE_LEVEL
UNKNOWN_ROLE_LEVEL
```

### Exit gate

```text
[ ] recommendations do not depend on LLM output
[ ] same-role/same-level peers influence recommendations
[ ] restricted systems are blocked or excluded
[ ] unknown role-level is handled conservatively
[ ] tests prove recommendation behavior
```

---

## 19. Phase 7 — Employee Selection

### Goal

Allow the employee to choose systems from recommendations.

### Required behavior

```text
employee selects systems
selection is persisted
selection is validated against policy
forbidden systems are rejected
unknown systems are rejected or marked for manual review
valid selection creates access request state
```

### Exit gate

```text
[ ] selected systems are stored
[ ] forbidden selection is blocked before approval
[ ] valid selection moves workflow state forward
[ ] tests cover valid and invalid selection
```

---

## 20. Phase 8 — Approval State Machine

### Goal

Implement asynchronous manager approval.

### Required states

```text
PENDING
APPROVED
REJECTED
EXPIRED
CLOSED_NO_TICKET
TICKET_CREATED
```

### Required behavior

```text
create approval request only for valid selected systems
store manager ID
allow approve
allow reject
allow expire
block ticket while pending
block ticket after rejection
block ticket after expiry
allow ticket after approval
```

### Exit gate

```text
[ ] approval starts as pending
[ ] pending approval blocks ticket creation
[ ] rejected approval blocks ticket creation
[ ] expired approval blocks ticket creation
[ ] approved approval allows ticket creation
[ ] tests prove all approval paths
```

---

## 21. Phase 9 — ITSM Ticket Mock

### Goal

Simulate IT ticket creation without real Jira or ServiceNow.

### Required behavior

```text
create ticket only after approval
persist ticket record
include selected systems
include employee ID
include manager approval ID
include status
prevent duplicate tickets
return existing ticket or duplicate-blocked status for repeated requests
```

### Exit gate

```text
[ ] ticket cannot be created before approval
[ ] ticket is created after approval
[ ] duplicate ticket creation is prevented
[ ] ITSM failure scenario is testable
[ ] tests cover ticket gate and idempotency
```

---

## 22. Phase 10 — Slack and Message Mocks

### Goal

Simulate employee and manager communication.

### Required message types

```text
employee_onboarding_summary
employee_access_selection_prompt
manager_approval_request
manager_decision_confirmation
employee_ticket_created_notice
employee_blocked_or_rejected_notice
```

### Required behavior

```text
store recipient
store message type
store message body
store metadata
store status
simulate failure case
```

### Exit gate

```text
[ ] employee message is stored
[ ] manager message is stored
[ ] message metadata includes employee/request/correlation ID
[ ] Slack mock failure does not corrupt approval or ticket state
```

---

## 23. Phase 11 — Audit Logging

### Goal

Make the workflow inspectable.

### Audit these events

```text
workflow started
employee profile loaded
training loaded
recommendations generated
employee selection received
selection validated
approval requested
approval approved/rejected/expired
ticket creation attempted
ticket created
ticket blocked
message generated
message sent or stored
error occurred
```

### Required audit fields

```text
event_id
created_at
correlation_id
employee_id
actor_type
actor_id
action
target_type
target_id
status
reason_code
metadata_json
```

### Exit gate

```text
[ ] audit log records happy path
[ ] audit log records blocked paths
[ ] audit log records errors
[ ] audit log excludes secrets
[ ] demo can show audit events by correlation ID
```

---

## 24. Phase 12 — LLM Adapter and Fallback

### Goal

Add AI-generated communication without making the LLM responsible for decisions.

### Recommended options

```text
gemma2:2b for constrained hardware
llama3.1:8b or mistral:7b where hardware allows
deterministic fallback text if Ollama is unavailable
```

### Required behavior

```text
LLM receives structured context only
LLM generates employee-facing summary
LLM generates manager approval message
fallback text works if Ollama is down
LLM output is not used to authorize access
```

### Exit gate

```text
[ ] message generation works with Ollama or fallback
[ ] fallback is automatic or clearly documented
[ ] tests cover fallback behavior
[ ] prompts avoid unnecessary PII
[ ] README states LLM boundary clearly
```

---

## 25. Phase 13 — API Smoke Path Before n8n

### Goal

Prove the workflow before relying on the visual orchestration layer.

### Smoke path sequence

```text
reset demo data
start onboarding for emp_001
load employee profile
load training status
generate access recommendations
select approved systems
create approval request
attempt ticket before approval and confirm blocked
approve as manager
create ticket after approval
retrieve audit log
```

### Preferred form

Use:

```text
README curl/httpie sequence
pytest integration test
```

Avoid building a large CLI unless time remains.

### Exit gate

```text
[ ] happy path works without n8n
[ ] pre-approval ticket attempt is blocked
[ ] post-approval ticket creation works
[ ] audit log is visible
[ ] README explains smoke path
```

---

## 26. Phase 14 — n8n Workflow

### Goal

Add the visible workflow/agent orchestration layer.

### Required n8n workflow steps

```text
manual trigger or webhook
fetch employee profile
fetch training status
fetch recommendations
generate employee summary
send Slack-style employee message
receive or simulate employee selection
validate selection
create manager approval request
check approval state
branch: pending / approved / rejected
create ITSM ticket only on approved branch
write or retrieve audit event
error branch
```

### Important rule

n8n orchestrates. It should not contain the core policy logic.

Core policy logic belongs in deterministic API services that can be tested.

### Exit gate

```text
[ ] n8n workflow imports cleanly
[ ] workflow uses local FastAPI endpoints
[ ] workflow shows approval branch
[ ] workflow shows error path
[ ] workflow creates no ticket before approval
[ ] workflow export is saved under n8n/
```

---

## 27. Phase 15 — Failure Paths

### Goal

Show reliability and security, not only happy path behavior.

### Required failure paths

```text
unknown employee
missing manager
unknown role-level
forbidden system selected
approval pending
approval rejected
approval expired
duplicate ticket request
ITSM mock failure
Slack mock failure
LLM unavailable
database unavailable or service error
```

### Exit gate

```text
[ ] failure paths are documented
[ ] critical failure paths have tests
[ ] demo includes at least one blocked action
[ ] audit log records failed/blocked paths
```

---

## 28. Phase 16 — Test Suite

### Goal

Create evaluator-visible confidence.

### Required tests

```text
known employee profile loads
unknown employee returns structured error
missing manager blocks workflow
training status loads
role-level recommendations are correct
peer-pattern reason codes appear
forbidden access is blocked
employee selection creates pending approval
ticket not created without approval
ticket created after approval
rejected approval blocks ticket
expired approval blocks ticket
duplicate ticket is prevented
audit log records major events
LLM fallback works when Ollama is unavailable
Slack mock records messages
demo reset reseeds database
```

### Exit gate

```text
[ ] pytest passes
[ ] tests avoid paid/external services
[ ] test names clearly show requirement coverage
[ ] README says how to run tests
```

---

## 29. Phase 17 — Documentation Package

### Goal

Prepare submission-ready documentation.

### Required documents

```text
README.md
docs/solution_design.md
docs/demo_walkthrough.md
docs/mock_boundary.md
docs/definition_of_done.md
docs/standards_alignment.md
docs/deliverable_mapping.md
docs/traceability_matrix.md
```

### README must include

```text
project summary
selected scenario
why it is not just an n8n template
architecture
free Linux stack
install prerequisites
run commands
how to import/run n8n workflow
how to run tests
what is mocked
what is real
known limitations
production path
```

### Solution design must be concise

The candidate exercise asks for a 1–2 page design. Keep that file short. Do not submit the full planning archive as the main design deliverable.

### Exit gate

```text
[ ] README can be followed by someone new
[ ] solution design is 1–2 pages
[ ] mock boundary is explicit
[ ] standards alignment says alignment, not compliance
[ ] demo walkthrough is under five minutes
```

---

## 30. Phase 18 — Final Verification

### Goal

Confirm the project is runnable and demonstrable.

### Must-run commands to document

```text
cp .env.example .env
docker compose up --build
curl http://localhost:8000/health
pytest -q
```

Alternative if using Podman:

```text
cp .env.example .env
podman compose up --build
curl http://localhost:8000/health
pytest -q
```

### Manual verification

Confirm:

```text
n8n opens locally
FastAPI /docs opens locally
PostgreSQL stores workflow state
demo reset works
emp_001 happy path works
ticket is blocked before approval
ticket is created after approval
duplicate ticket is prevented
forbidden system is blocked
audit log shows the workflow
LLM fallback works
```

### Exit gate

```text
[ ] clean local run succeeds
[ ] tests pass
[ ] demo path works
[ ] all final files are present
[ ] no paid accounts or keys are required
[ ] no false compliance claims are present
```

---

## 31. Phase 19 — Final Submission Assembly

### Submit

```text
README.md
docs/solution_design.md
docs/demo_walkthrough.md
docs/standards_alignment.md
docs/deliverable_mapping.md
docker-compose.yml
.env.example
n8n/hr_onboarding_workflow.json
api/
tests/
```

### Keep as supporting/internal material

```text
long planning history
Agent_X internal standards
EQC/FIC/SIB full documents
resume or ATS material
draft iterations
```

### Do not submit as the main deliverable

```text
large planning archive
unnecessary theory
unsupported compliance claims
overly complex architecture
```

---

## 32. Recommended Exact Build Order

This is the final practical order.

```text
1. Create repo and folders.
2. Add README skeleton and .env.example.
3. Add Compose skeleton for PostgreSQL, FastAPI, n8n, optional Ollama.
4. Start PostgreSQL and FastAPI health endpoint.
5. Add database schema and seed/reset behavior.
6. Add HR mock.
7. Add Training mock.
8. Add role-level access policy fixtures.
9. Add peer access pattern fixtures.
10. Add deterministic access recommender.
11. Add employee selection behavior.
12. Add approval state machine.
13. Add ITSM ticket mock and ticket gate.
14. Add Slack/message mock.
15. Add audit logging.
16. Add LLM adapter with deterministic fallback.
17. Add README curl/httpie smoke path or integration smoke test.
18. Add pytest coverage for core and failure paths.
19. Build n8n workflow on top of stable endpoints.
20. Export n8n workflow JSON.
21. Add demo walkthrough.
22. Add standards alignment.
23. Add deliverable mapping.
24. Run final Linux verification.
25. Package final submission.
```

---

## 33. Time-Boxed Build Strategy

Use this schedule under deadline pressure.

### Day 1 — Foundation and contracts

```text
Create repo, docs, .env.example, compose skeleton.
Start PostgreSQL, FastAPI health endpoint, and n8n locally.
Lock mock boundary and Definition of Done.
```

Done when:

```text
compose starts services
FastAPI health endpoint responds
n8n UI opens
README has stack and run path
```

### Day 2 — Stateful mocks and recommendation

```text
Add schema, seed/reset, HR mock, training mock, role-level policy, peer-pattern data, and recommender.
```

Done when:

```text
emp_001 returns role/level/manager
T1-T4 status returns
recommendations include reason codes
restricted systems are blocked or excluded
```

### Day 3 — Approval, ticket, and audit

```text
Add employee selection, approval state machine, ITSM ticket mock, idempotency, and audit events.
```

Done when:

```text
ticket creation fails before approval
ticket creation succeeds after approval
duplicate ticket is blocked or returns existing ticket
audit log shows the chain
```

### Day 4 — LLM/fallback and tests

```text
Add message-generation adapter, deterministic fallback, failure-path tests, and smoke path.
```

Done when:

```text
Ollama or fallback creates employee/manager messages
pytest passes for core paths
README smoke path works
```

### Day 5 — n8n and final packaging

```text
Build n8n workflow on stable endpoints, export JSON, write demo walkthrough, finalize solution design, and run final verification.
```

Done when:

```text
n8n workflow imports and runs
final demo shows role/level, recommendations, approval, ticket, and audit log
submission package contains only evaluator-needed files
```

---

## 34. Professional Branch and Commit Rhythm

Use a simple reviewable history.

```text
main branch stays runnable
small commits follow milestone gates
backend endpoints stabilize before n8n workflow work
LLM is added after deterministic policy behavior
README is updated after each gate
```

Recommended commit sequence:

```text
01 project skeleton and docs
02 compose runtime skeleton
03 FastAPI health and config
04 database schema and seed/reset
05 HR and training mocks
06 access policy and peer recommendation
07 selection and approval state machine
08 ITSM ticket gate and idempotency
09 Slack/message mock and audit log
10 LLM adapter and fallback
11 smoke path and pytest coverage
12 n8n workflow export
13 final README and demo docs
```

---

## 35. Evaluator-First Delivery Path

The final package should be easy to review in this order:

```text
1. README: what it is, how to run it, what is mocked, what is real.
2. Solution design: 1-2 pages, architecture and trade-offs only.
3. n8n workflow export: visible orchestration proof.
4. FastAPI Swagger UI: mocked SaaS/API proof.
5. pytest output: reliability and gate-proof.
6. Demo walkthrough: five-minute evidence path.
7. Definition of Done / mock-boundary document: supporting evidence, not the main pitch.
```

The evaluator should not have to read every planning document to understand the project. The planning documents support the work; the README, short design, runnable stack, workflow export, and tests are the main evidence.

### Final review order

Use this order when reviewing your own work:

```text
first: can it run locally without paid services?
second: does it visibly satisfy the exercise prompt?
third: does it clearly differ from an n8n template?
fourth: does the approval gate prove controlled autonomy?
fifth: are docs concise enough for an evaluator?
```

## 36. Final Evidence Map

| Claim | Evidence |
|---|---|
| Free Linux stack | README run commands, `.env.example`, compose file |
| Mocked SaaS integrations | FastAPI endpoints and Swagger UI |
| Role/level identification | HR mock response for demo employee |
| T1-T4 onboarding status | Training mock response |
| Access recommendation | Recommender output with reason codes |
| Peer-pattern use | Recommendation includes peer-frequency evidence |
| Policy validation | Forbidden system blocked before approval |
| Asynchronous approval | Pending, approved, rejected, expired states |
| Ticket gate | Ticket creation impossible before approval |
| Idempotency | Duplicate ticket request does not create duplicate ticket |
| Auditability | Audit events with correlation ID |
| LLM boundary | Message output generated, not used for authorization |
| n8n orchestration | Workflow export and visible canvas |
| Reliability | pytest passing and documented failure paths |
| Anti-template originality | README/demo differentiate from basic n8n onboarding templates |

---

## 37. Do-Not-Overbuild Controls

Avoid building anything that does not directly help the candidate exercise.

Do not build:

```text
custom React frontend
Kubernetes
real Slack app
real Salesforce integration
real Workday/BambooHR integration
real Okta/Entra integration
LangChain/CrewAI/AutoGen unless explicitly needed
full MCP layer
full Agent_X framework
full compliance program
complex real provisioning
production secrets manager
large CLI application
```

Mention these only as production extensions when relevant.

The prototype should look production-minded, not production-sized.

---

## 38. Final Review Checklist Before Submission

Before packaging, verify:

```text
[ ] The solution design is concise and not a giant planning archive.
[ ] The README can be followed by someone who has not seen this conversation.
[ ] The prototype does not require paid services or external SaaS credentials.
[ ] n8n visibly orchestrates the workflow.
[ ] Policy-sensitive logic lives in deterministic API services.
[ ] The LLM is bounded to message generation and explanation.
[ ] Ticket creation is blocked until manager approval.
[ ] The audit log proves the chain of actions.
[ ] Tests pass.
[ ] The standards section says alignment, not compliance.
[ ] Internal Agent_X/EQC/FIC ideas are described only as internal implementation discipline if mentioned at all.
[ ] Existing n8n templates are acknowledged and differentiated.
[ ] The final submission includes only evaluator-needed files.
```

---

## 39. Final Definition of Development Complete

Development is complete when a reviewer can follow the README on a clean Linux machine, start the local stack without paid accounts, open FastAPI docs and n8n locally, run the smoke path or demo workflow, see role/level-based recommendations with peer-pattern reason codes, confirm that ticket creation is blocked until manager approval, inspect audit events in PostgreSQL, run pytest successfully, and understand from the documentation exactly what is mocked, what is real, what is production-only, and how the prototype differs from a basic n8n onboarding template.

The final project should feel like a governed enterprise-agent prototype, not a generic automation template and not an overbuilt production platform. This v4 guide is complete when it can be handed to a developer as a blind plan: it tells them what to install, what to configure, what to build first, when to introduce n8n, when to introduce the LLM, what to test, and what evidence to package, without giving implementation code.
