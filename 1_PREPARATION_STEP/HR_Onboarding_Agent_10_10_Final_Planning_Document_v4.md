# HR Onboarding Agent — 10/10 Final Planning Document v4

**Candidate Exercise:** Enterprise Agent — Solutions Developer  
**Chosen Scenario:** Task 2 — HR use case  
**Target runtime:** Linux  
**Final prototype stack:** n8n + FastAPI + PostgreSQL + Ollama/Gemini/OpenAI switch + Docker Compose  
**Document purpose:** Consolidated design, prototype plan, implementation approach, standards alignment, governance controls, testing plan, demo notes, differentiation from existing n8n onboarding templates, final submission strategy, and evaluator-facing originality defense.

---

## 1. Rating of Previous Version

**Previous Markdown v3 rating:** 9.8/10

The previous Markdown v3 was already strong and covered the architecture, stack, agent behavior, mocked SaaS integrations, standards alignment, n8n template-risk concern, prototype plan, test plan, demo plan, and final submission strategy. It was not fully 10/10 because it still had a few presentation and evaluator-facing gaps:

- A minor section-numbering issue inside the demo walkthrough.
- The originality defense needed to be stated even more directly as a reusable README / demo statement.
- The build sequence needed a clearer minimal implementation order so the project can be implemented quickly without overbuilding.
- The final package boundary needed to be explicit: submit the concise deliverables and prototype, not the entire planning archive.

**Updated version rating:** 10/10

This version is the final master planning document for the candidate exercise. It is not meant to be submitted in full as the 1–2 page solution design. It is the source document used to produce the actual deliverables: concise solution design, README, n8n workflow export, FastAPI mock services, tests, demo notes, and standards-alignment notes.

---

## 2. Exercise Interpretation

The selected scenario is the **HR onboarding agent**.

The system should be an autonomous/chat-based HR onboarding agent for new employees. It must identify the employee’s role and level, guide them through predefined onboarding tasks, recommend needed access based on employees with the same role and level, wait for manager approval, and create an IT ticket only after approval.

The strongest framing is:

> This is not just a chatbot. It is a controlled workflow agent with bounded autonomy, deterministic policy gates, asynchronous manager approval, audit logging, mocked SaaS integrations, and LLM-assisted communication.

The LLM should improve human-readable communication. It should not be responsible for security-sensitive decisions such as approving access or granting permissions.

---

## 3. Final Technology Stack

### 3.1 Prototype Stack

| Layer | Technology | Purpose |
|---|---|---|
| Workflow / agent orchestration | **n8n** | Main AI workflow platform, webhook flows, branching, retries, approval workflow |
| Mock SaaS APIs | **FastAPI** | HR Platform, Slack, Training Platform, ITSM/Ticketing, Salesforce mock |
| Database | **PostgreSQL** | Workflow state, approval state, audit logs, access requests |
| LLM provider | **Ollama local LLM** | Free local message generation on Linux |
| Optional cloud LLM | **Gemini API or OpenAI API** | Better-quality fallback through environment variable |
| Runtime | **Docker Compose** | Easy Linux setup and reproducible demo |
| Testing | **pytest** | Validate recommendations, approval gate, ticket creation, and error paths |
| Logging | **Python logging + PostgreSQL audit table** | Trace decisions, errors, and actions |
| Config/secrets for prototype | **.env** | Keeps runtime configuration outside code |

### 3.2 Why This Stack Is 10/10 for the Requirement

The assignment explicitly mentions examples such as **n8n, Workato, Gemini/ChatGPT Agent**, and asks for an agent platform or AI workflow. Therefore, the strongest free Linux-friendly choice is **n8n** as the visible orchestration layer.

Pure FastAPI would be technically valid, but it would look more like a custom backend than an AI workflow/agent platform. n8n better demonstrates event-driven orchestration, API calls, branching, retries, and asynchronous approval.

FastAPI remains useful as the mocked SaaS/API layer because it allows clean, testable mock services without real credentials.

PostgreSQL is used instead of SQLite because it looks more production-minded and supports audit/state tables more credibly.

Ollama keeps the prototype free and local. Gemini/OpenAI can be optional through environment variables to show enterprise/cloud LLM flexibility.

### 3.3 Final Rating of Stack

**Final stack rating:** 10/10

It satisfies:

- Agent workflow platform requirement: yes, n8n.
- At least two SaaS integrations: yes, several mocked SaaS services.
- LLM usage: yes, Ollama with optional Gemini/OpenAI.
- Orchestration: yes, webhook-driven n8n workflow.
- Reliability: yes, retries, error branches, logs, idempotency.
- Security: yes, approval gate, least privilege, policy validation.
- Governance: yes, role-level policy, audit trail, human approval.
- Linux-friendly: yes, Docker Compose.
- Free prototype: yes, self-hosted n8n, FastAPI, PostgreSQL, Ollama.
- Production path: yes, real SaaS APIs, RBAC/ABAC, secrets manager, enterprise LLM, monitoring.

---

## 3.4 Existing n8n Onboarding Templates and Differentiation

A key concern is that n8n already has public employee-onboarding and IT Ops workflow templates. That should be treated as a strength of the platform choice, not as a weakness of the candidate solution. It proves that onboarding is a natural fit for workflow automation and that n8n is a recognizable tool for this scenario.

However, the candidate exercise should not be positioned as if basic onboarding automation is novel. The solution must clearly explain what is different from a standard n8n onboarding template.

### 3.4.1 What Existing Templates Usually Cover

Existing n8n onboarding templates commonly cover workflows such as:

- receiving a new-hire form or webhook;
- creating or provisioning basic user accounts;
- inviting employees to Slack or channels;
- creating Jira or IT tasks;
- creating Google Workspace or other SaaS accounts;
- generating welcome messages or onboarding documents;
- logging simple completion status.

Those are useful automations, but they do not fully satisfy the exercise’s strongest interpretation unless they are extended with role-level reasoning, access recommendation, approval-state management, and governance controls.

### 3.4.2 What This Candidate Solution Adds

This solution should be positioned as a governed, role-aware HR onboarding agent rather than a generic onboarding automation.

| Existing n8n onboarding automation | This candidate solution |
|---|---|
| Creates or updates users after a form submission | Interprets HR source-of-truth role, level, department, and manager |
| Sends Slack/Jira/Google Workspace actions | Coordinates HR, Training, Slack, Salesforce, Approval, ITSM, and Audit mocks |
| Adds users to predefined tools or channels | Recommends access from approved role-level policy plus same-role/same-level peer patterns |
| May use AI to draft messages | Restricts LLM to summaries and explanations only |
| Often creates tasks directly | Blocks IT ticket creation until manager approval is valid |
| Basic workflow logging | Structured audit trail for recommendation, selection, approval, rejection, ticket, and error events |
| Template-style automation | Production-minded agent design with least privilege, idempotency, retry/error handling, and policy gates |

### 3.4.3 Safe Evaluator-Facing Positioning

Use this positioning in the README, demo, and solution design:

> n8n already demonstrates that employee onboarding is a natural workflow-automation use case. This prototype builds on that pattern but adds role-level reasoning, peer-based access recommendations, asynchronous manager approval, deterministic policy validation, audit logging, and controlled LLM usage. The goal is not to show that onboarding automation is new; the goal is to show how a standard onboarding workflow can become a governed enterprise onboarding agent.

### 3.4.4 Prototype Implication

The demo should make these differences visible. Do not stop at “form submitted → Slack/Jira action.” The demo must show:

1. HR mock returns role, level, department, and manager.
2. Training mock returns T1–T4 status.
3. Access recommender uses role-level matrix and peer access patterns.
4. Employee chooses systems from recommendations.
5. Manager approval remains pending until explicitly approved.
6. ITSM ticket creation is blocked before approval.
7. ITSM ticket creation succeeds after approval.
8. Audit log shows every major decision and action.

This distinction is now part of the 10/10 version because it addresses the main risk that the reviewer may see a similar n8n example and assume the prototype is only a template.

### 3.4.5 How to Avoid Looking Like a Reused n8n Template

The prototype should not be submitted as a generic n8n workflow export with cosmetic changes. It should include custom business logic and evidence that the design was built for the exercise requirements.

Visible differences to include:

- A custom FastAPI access-recommendation endpoint that combines role-level policy with peer access patterns.
- A manager approval state machine that blocks ticket creation until approval is valid.
- A restricted-systems policy that prevents sensitive systems from being recommended or selected.
- A correlation ID carried across HR lookup, recommendation, selection, approval, ticket creation, and audit events.
- A pytest test proving that IT ticket creation fails before manager approval and succeeds after approval.
- A README section explicitly stating that existing n8n templates solve simple onboarding automation, while this prototype solves governed role-aware access orchestration.

Reviewer-facing distinction:

```text
I used n8n because the exercise explicitly allows workflow/agent platforms and because onboarding is naturally event-driven. The differentiating work is not the presence of an onboarding workflow; it is the policy-backed access recommendation, asynchronous approval gate, deterministic safety checks, and audit trail around the workflow.
```

### 3.4.6 Final Originality Statement

Use this exact positioning in the README and demo notes:

```text
This prototype intentionally uses n8n because the exercise asks for an agent platform or AI workflow and because employee onboarding is a known workflow-automation use case. The contribution is not a generic onboarding template. The contribution is a governed HR onboarding agent that identifies role and level, recommends access from role-level policy and same-role peer patterns, requires employee selection and asynchronous manager approval, blocks IT ticket creation until approval is valid, and records an audit trail for every recommendation, decision, and action.
```

This prevents the evaluator from interpreting the work as a copied onboarding template. It also shows practical judgment: the prototype reuses the right workflow platform while putting the custom intelligence, governance, and reliability logic in the policy/API layer.

---

## 4. High-Level Architecture

```text
New employee onboarding trigger
        |
        v
n8n HR onboarding workflow
        |
        |-- FastAPI HR mock: employee profile, role, level, manager
        |-- FastAPI Training mock: T1/T2/T3/T4 completion status
        |-- FastAPI Access recommender: role-level + peer-pattern recommendation
        |-- Ollama/Gemini/OpenAI adapter: human-readable summaries only
        |-- FastAPI Slack mock: employee and manager messages
        |-- PostgreSQL: state, selections, approvals, audit logs
        |-- FastAPI ITSM mock: ticket creation after manager approval
        v
Controlled completion with correlation_id and audit trail
```

The agent receives an employee onboarding trigger, retrieves employee information from the HR mock API, checks training status, recommends systems based on approved role-level policy and peer access patterns, sends guidance to the employee, waits for selected systems, sends manager approval request, and creates an ITSM ticket only after approval.

---

## 5. What the AI Agent Does

The AI agent should:

- Identify employee role and level from HR source-of-truth data.
- Build an onboarding checklist.
- Check T1, T2, T3, and T4 training completion.
- Recommend access from role-level policy and peer access patterns.
- Explain recommendations in human-readable language.
- Ask the employee to select systems.
- Request manager approval asynchronously.
- Create an IT ticket only after approval.
- Answer onboarding questions using approved policy and current workflow state.
- Log recommendations, selections, approvals, tickets, and failures.

The AI agent should not:

- Grant access directly.
- Bypass manager approval.
- Invent systems outside the policy matrix.
- Change employee role, level, manager, or approval state based on chat input.
- Put unnecessary PII or secrets into prompts.
- Treat LLM output as authoritative policy.

---

## 6. LLM Usage Boundary

The LLM is used for:

- Employee-facing onboarding summaries.
- Manager approval request messages.
- Explanation of recommended access.
- Clear status messages.
- Answers to safe onboarding questions.

Deterministic services are used for:

- Role/level detection.
- Access recommendation eligibility.
- Approval-state validation.
- ITSM ticket creation permission.
- Idempotency.
- Audit logging.
- Error handling.

This is an important design choice. It shows that the system uses AI where it adds value, but keeps business-critical decisions controlled and auditable.

---

## 7. Mocked SaaS Platforms

The prototype should mock at least two SaaS platforms, but the best version mocks five:

| Mock platform | Prototype role |
|---|---|
| HR Platform | Employee profile, role, level, department, manager, start date |
| Slack | Employee messages, manager approval prompts |
| Training Platform | T1/T2/T3/T4 onboarding completion |
| Salesforce | Example role-specific access target |
| ITSM / Ticketing | Access request ticket after manager approval |

Mocking several systems makes the prototype feel enterprise-ready while avoiding real credentials.

---

## 8. n8n Workflow Plan

### 8.1 Main n8n Nodes

1. **Webhook Trigger**
   - Receives `employee_id`.
   - Creates `correlation_id`.

2. **Get Employee Profile**
   - Calls FastAPI HR mock.
   - Fails cleanly if employee is unknown or inactive.

3. **Check Training Status**
   - Calls FastAPI Training mock.
   - Returns T1–T4 completion state.

4. **Recommend Access**
   - Calls FastAPI access recommender.
   - Uses role-level matrix and peer patterns.

5. **Generate Employee Message**
   - Calls LLM adapter.
   - Converts structured state into a readable onboarding summary.

6. **Send Slack Message**
   - Calls Slack mock endpoint.
   - Records message result.

7. **Wait for Employee Selection**
   - Demo can simulate this through an API call.
   - Stores selected systems.

8. **Validate Selection**
   - Blocks systems outside allowed/recommended policy.

9. **Request Manager Approval**
   - Sends manager-facing message.
   - Stores approval state as pending.

10. **Wait for Manager Approval**
   - Demo can simulate approval through endpoint.

11. **Create ITSM Ticket**
   - Creates ticket only if approval is manager_approved.
   - Uses idempotency key.

12. **Final Status + Audit Log**
   - Returns completed state, ticket ID, and audit trail reference.

### 8.2 Workflow State Machine

```text
DRAFT
  -> RECOMMENDED
  -> EMPLOYEE_SELECTED
  -> MANAGER_APPROVAL_PENDING
  -> MANAGER_APPROVED
  -> TICKET_CREATED
  -> COMPLETED

Alternate/failure states:
  EMPLOYEE_NOT_FOUND
  UNKNOWN_ROLE_LEVEL
  POLICY_NOT_FOUND
  EMPLOYEE_SELECTION_INVALID
  MANAGER_REJECTED
  APPROVAL_EXPIRED
  ITSM_TICKET_FAILED
  COMPLETED_WITH_NOTIFICATION_WARNING
```

### 8.3 Workflow Invariants

- `TICKET_CREATED` is unreachable unless the previous valid state is `MANAGER_APPROVED`.
- Selected systems must be allowed by role-level policy.
- IT ticket creation must be idempotent by `employee_id + request_id + selected_systems_hash`.
- Employee chat input cannot change role, level, policy, manager identity, or approval state.
- Audit events must include `correlation_id`, actor, action, target entity, result, and timestamp.

---

## 9. FastAPI Mock API Surface

### 9.1 HR API

```text
GET /mock/hr/employees/{employee_id}
```

Returns employee profile, role, level, department, manager, start date, and status.

### 9.2 Training API

```text
GET /mock/training/status/{employee_id}
```

Returns T1, T2, T3, T4 completion status.

### 9.3 Access Recommendation API

```text
GET /mock/access/recommendations/{employee_id}
```

Returns recommended systems, optional systems, restricted systems, and rationale.

### 9.4 Slack Mock API

```text
POST /mock/slack/messages
```

Simulates sending employee and manager messages.

### 9.5 Approval API

```text
POST /mock/approvals
POST /mock/approvals/{approval_id}/approve
POST /mock/approvals/{approval_id}/reject
POST /mock/approvals/{approval_id}/expire
GET /mock/approvals/{approval_id}
```

Supports asynchronous manager approval simulation.

### 9.6 ITSM API

```text
POST /mock/itsm/tickets
GET /mock/itsm/tickets/{ticket_id}
```

Creates access ticket only when manager approval is valid.

### 9.7 Audit API

```text
POST /mock/audit/events
GET /mock/audit/workflows/{correlation_id}
```

Records and retrieves workflow audit events.

### 9.8 Salesforce Mock API

```text
GET /mock/salesforce/profile/{employee_id}
PATCH /mock/salesforce/profile/{employee_id}
```

Represents role-specific access configuration for the Salesforce platform.

---

## 10. Example Payloads

### 10.1 Employee Profile

```json
{
  "employee_id": "emp_001",
  "name": "Maya Chen",
  "role": "Account Executive",
  "level": "L2",
  "department": "Sales",
  "manager_id": "mgr_101",
  "manager_name": "Jordan Lee",
  "start_date": "2026-06-17",
  "status": "new_hire"
}
```

### 10.2 Recommendation Response

```json
{
  "employee_id": "emp_001",
  "role": "Account Executive",
  "level": "L2",
  "recommended_systems": ["Salesforce", "Gong", "Slack #sales-team", "Outreach"],
  "optional_systems": ["Miro", "Looker Viewer"],
  "restricted_systems": ["Payroll Admin", "Production Database Admin"],
  "rationale": [
    "Salesforce is required by approved role-level matrix for Account Executive L2.",
    "Gong and Outreach appear in 80%+ of same role-level peer profiles.",
    "Slack #sales-team is standard department onboarding access."
  ],
  "policy_version": "role-access-v1"
}
```

### 10.3 ITSM Ticket Request

```json
{
  "request_id": "req_5001",
  "employee_id": "emp_001",
  "manager_approval_id": "appr_9001",
  "selected_systems": ["Salesforce", "Gong", "Slack #sales-team"],
  "idempotency_key": "emp_001:req_5001:7ac43d",
  "correlation_id": "corr_20260611_001"
}
```

---

## 11. PostgreSQL Data Model

Minimum tables:

```text
employees
  employee_id
  name
  role
  level
  department
  manager_id
  status

training_status
  employee_id
  t1_status
  t2_status
  t3_status
  t4_status

role_access_matrix
  role
  level
  required_systems
  optional_systems
  restricted_systems
  policy_version

selected_access_requests
  request_id
  employee_id
  selected_systems
  status
  approval_id
  ticket_id
  idempotency_key
  created_at
  updated_at

manager_approvals
  approval_id
  request_id
  manager_id
  status
  approved_at
  rejected_at
  decision_reason

itsm_tickets
  ticket_id
  request_id
  employee_id
  selected_systems
  status
  created_at

audit_events
  event_id
  correlation_id
  actor
  action
  target_type
  target_id
  result
  details_json
  created_at
```

---

## 12. Fixture Files

```text
fixtures/
  employees.json
  training_status.json
  role_access_matrix.json
  peer_access_patterns.json
  approval_scenarios.json
  error_scenarios.json
```

These fixtures keep the demo deterministic and allow reliable tests without real SaaS credentials.

---

## 13. Repository Structure

```text
hr-onboarding-agent/
  README.md
  docker-compose.yml
  .env.example
  requirements.txt

  docs/
    solution_design_1_2_pages.md
    demo_walkthrough.md
    standards_alignment.md
    tradeoffs_and_assumptions.md
    traceability_matrix.md
    prototype_acceptance_checklist.md
    fic/
      FIC-access-recommender.md
      FIC-approval-gate.md
      FIC-itsm-ticket-creator.md
      FIC-audit-logger.md

  n8n/
    hr_onboarding_workflow.json
    screenshots/
      workflow_canvas.png

  api/
    app/
      main.py
      config.py
      database.py
      models.py
      services/
        hr_service.py
        training_service.py
        slack_service.py
        approval_service.py
        itsm_service.py
        llm_service.py
      logic/
        access_recommender.py
        policy_engine.py
        idempotency.py
      fixtures/
        employees.json
        training_status.json
        role_access_matrix.json
        peer_access_patterns.json
    tests/
      test_access_recommender.py
      test_approval_gate.py
      test_ticket_idempotency.py
      test_error_paths.py
      test_audit_logging.py
```

---

## 14. Linux Setup and Run Commands

```bash
# 1. Start services
cp .env.example .env
docker compose up -d

# 2. Pull a local LLM model
ollama pull llama3.1:8b

# Hardware-constrained fallback:
ollama pull gemma2:2b

# 3. Run FastAPI locally if not containerized
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Run tests
pytest -q

# 5. Open interfaces
# FastAPI Swagger: http://localhost:8000/docs
# n8n: http://localhost:5678
```

---

## 15. Minimal Build Sequence

Build the prototype in this order to avoid overengineering:

1. **FastAPI fixtures and models** — employees, training status, role access matrix, peer access patterns.
2. **Access recommender** — deterministic recommendations from role-level policy plus peer-pattern evidence.
3. **Approval gate** — pending, approved, rejected, expired states.
4. **ITSM ticket creator** — ticket creation blocked until approval; idempotency key required.
5. **Audit logger** — correlation ID and event log for each major step.
6. **LLM adapter** — generate employee and manager messages from structured state only.
7. **n8n workflow** — webhook/manual trigger, API calls, branches, wait/approval simulation, final status.
8. **pytest tests** — recommendation, approval gate, idempotency, error paths, audit logging.
9. **README/demo notes** — setup, run commands, architecture, known-template differentiation, production path.

This order ensures the differentiating logic exists before the visual n8n workflow is polished. The n8n canvas should demonstrate orchestration, but the policy-sensitive behavior should live in deterministic API services and tests.

---

## 16. Test Plan

### 16.1 Required Tests

| Test | Purpose |
|---|---|
| `test_access_recommender.py` | Role-level policy and peer-pattern recommendations are correct |
| `test_approval_gate.py` | IT ticket cannot be created before manager approval |
| `test_ticket_idempotency.py` | Duplicate requests do not create duplicate tickets |
| `test_error_paths.py` | Unknown employee, unknown role-level, invalid system, and manager rejection behave correctly |
| `test_audit_logging.py` | Every major action emits audit events with correlation_id |

### 16.2 Acceptance Criteria

The prototype is complete when:

- n8n workflow can start onboarding from an employee ID.
- FastAPI mock services return employee, training, access, approval, and ticket data.
- LLM generates at least one employee-facing and one manager-facing message.
- Employee selected systems are validated against policy.
- Manager approval is required before IT ticket creation.
- Ticket creation is idempotent.
- Audit logs show the full workflow.
- Tests pass.
- README explains setup, run commands, architecture, assumptions, and production path.

### 16.3 Prototype Definition of Done

The prototype should be considered complete only when these evaluator-visible outcomes are true:

- The n8n workflow can be imported and run locally.
- The FastAPI Swagger UI exposes all mocked SaaS endpoints.
- A demo employee can move through recommendation, selection, approval, ticket creation, and audit-log review.
- A pre-approval ticket attempt fails with a clear policy/approval error.
- A post-approval ticket attempt succeeds and returns one ticket ID.
- Repeating the post-approval request returns the same ticket result or blocks duplication through idempotency.
- At least one LLM-generated employee message and one manager message are produced from structured state.
- pytest demonstrates the policy-sensitive behavior.
- The README explicitly distinguishes the work from generic n8n onboarding templates.

---

## 17. Recognized Industry Standards and Frameworks

These are actual known external standards/frameworks or protocols. They should be used as **alignment references**, not as certification claims.

### 16.1 Core AI and Security References

| Standard/framework | Use in this solution |
|---|---|
| **NIST AI Risk Management Framework (AI RMF)** | AI risk governance: govern, map, measure, manage risks around AI-assisted decisions and human oversight. |
| **OWASP Top 10 for LLM Applications** | LLM security: prompt injection, insecure output handling, sensitive information disclosure, excessive agency, supply-chain risks. |
| **ISO/IEC 42001:2023** | AI management-system direction: structured governance, risk ownership, lifecycle controls, continuous improvement. |
| **SOC 2 Trust Services Criteria** | Enterprise control alignment: security, availability, processing integrity, confidentiality, privacy, and auditability. |

### 16.2 Identity, Access, and Enterprise Integration Standards

| Standard/protocol | Use in production path |
|---|---|
| **SCIM 2.0** | User provisioning/deprovisioning into SaaS systems. |
| **OAuth 2.0** | API authorization between services. |
| **OpenID Connect (OIDC)** | Identity layer for authentication and user identity claims. |
| **SAML 2.0** | Enterprise SSO/federation with identity providers. |
| **RBAC** | Role-based access policy. |
| **ABAC** | Attribute-based policy using role, level, department, manager, location, employment status. |

### 16.3 Service Management and Privacy References

| Standard/framework/principle | Use in solution |
|---|---|
| **ITIL-style ITSM workflow** | Access request, approval, ticket creation, escalation, rejection, and operational workflow language. |
| **GDPR-style privacy principles** | Data minimization, purpose limitation, auditability, retention discipline, access controls. |
| **PIPEDA-style privacy framing** | Useful if presenting Canadian privacy awareness, but avoid claiming compliance unless implemented. |

### 16.4 Optional Security References

These are real but optional. Mention only if the design needs a stronger production-security section:

- ISO/IEC 27001
- NIST Cybersecurity Framework
- CIS Controls
- CSA Cloud Controls Matrix
- OWASP ASVS
- OWASP API Security Top 10

For this candidate exercise, the best final set is:

```text
NIST AI RMF
OWASP Top 10 for LLM Applications
ISO/IEC 42001:2023
SOC 2 Trust Services Criteria
SCIM 2.0
OAuth 2.0 / OpenID Connect
SAML 2.0
RBAC / ABAC
ITIL-style ITSM workflow
GDPR-style privacy principles
```

---

## 18. Standards-to-Control Mapping

| Control area | Standard/framework alignment | Prototype control |
|---|---|---|
| AI risk governance | NIST AI RMF, ISO/IEC 42001 | LLM is limited to communication; policy remains deterministic |
| Prompt/security risk | OWASP LLM Top 10 | Treat chat input as untrusted; validate all action-driving data |
| Access governance | RBAC/ABAC, SCIM production path | Role-level matrix, peer-pattern evidence, restricted systems list |
| Identity/auth production path | OAuth 2.0, OIDC, SAML | Mentioned as production integration path, not needed in mock prototype |
| Ticketing process | ITIL-style ITSM | Manager approval before IT ticket creation |
| Enterprise controls | SOC 2 Trust Services Criteria | Audit logs, idempotency, confidentiality, processing integrity |
| Privacy | GDPR-style principles | Minimize PII in prompts/logs; record purpose-bound audit events |

---

## 19. Internal Agent_X / EQC-Inspired Methods

These are **not external industry standards**. They are internal methods or design discipline. They should not be presented as recognized standards.

| Internal method | How to use it |
|---|---|
| Agent_X governance-first pattern | Use as internal architecture discipline: bounded autonomy, validation gates, audit trail. |
| EQC-style operator thinking | Keep deterministic policy operators separate from workflow control flow. |
| EQC-FIC-style implementation contracts | Use compact implementation contracts for key modules. |
| SIB-style traceability | Maintain a lightweight requirement-to-code-to-test table. |
| Pseudocode-to-FIC-to-Code workflow | Use privately to build from system goal to bounded modules and tests. |

Safe wording:

> The prototype uses internal implementation discipline inspired by Agent_X-style governance: bounded actions, deterministic validation gates, audit logs, and document-to-code traceability. These are internal project methods, while the external alignment references are NIST AI RMF, OWASP LLM Top 10, ISO/IEC 42001, SOC 2 Trust Services Criteria, SCIM/OIDC/SAML, RBAC/ABAC, ITIL-style ITSM, and privacy principles.

---

## 20. Compact FIC Targets

Use compact implementation contracts only for key risk-bearing modules.

### 19.1 FIC-access-recommender

Defines:

- Inputs: employee role, level, department, peer access data, role access matrix.
- Outputs: recommended, optional, restricted systems with rationale.
- Invariants: restricted systems cannot be recommended; unknown role-level returns policy error.
- Tests: normal recommendation, unknown role-level, restricted-system exclusion, deterministic ordering.

### 19.2 FIC-approval-gate

Defines:

- Inputs: access request, manager identity, approval decision.
- Outputs: approval state.
- Invariants: ticket creation is blocked unless approval is manager_approved.
- Tests: pending blocks ticket, approved allows ticket, rejected blocks ticket, expired approval blocks ticket.

### 19.3 FIC-itsm-ticket-creator

Defines:

- Inputs: approved access request, selected systems, idempotency key.
- Outputs: ticket ID and ticket status.
- Invariants: no duplicate ticket for same idempotency key.
- Tests: creates ticket after approval, rejects without approval, idempotent duplicate request.

### 19.4 FIC-audit-logger

Defines:

- Inputs: actor, action, target, result, correlation ID.
- Outputs: audit event record.
- Invariants: every major action has an audit event; audit event does not include secrets.
- Tests: records event, rejects missing correlation ID, masks sensitive fields.

---

## 21. Requirement-to-Design Traceability Matrix

| Exercise requirement | Design response |
|---|---|
| Identify employee level and role | HR mock API is source of truth; workflow retrieves role/level before recommendations |
| Guide predefined corporate practice tasks | Training/profile checklist includes Slack, HR profile, Salesforce/profile update, T1–T4 |
| Update personal information on Slack, HR platform, Salesforce | Mock services simulate status checks and messages for these systems |
| Complete onboarding training T1–T4 | Training mock API returns completion status and missing modules |
| Request needed accesses for job role-level | Access recommender uses role-level matrix and peer access patterns |
| Assess same role and level employees | Peer access fixture contributes to recommendations and rationale |
| Let employee choose necessary systems | Employee selection endpoint/state step stores selected systems |
| Require manager approval before IT | Approval gate blocks ticket creation until manager approval |
| Approval is asynchronous | n8n wait/approval simulation and approval API support pending state |
| Answer questions while waiting | Agent can answer from workflow state and approved policy data |
| Integrate at least two SaaS platforms | HR, Slack, Training, Salesforce, and ITSM are mocked |
| Use LLM or rules fixtures | Ollama/Gemini/OpenAI for messages; deterministic fixtures for policy |
| Demonstrate orchestration | n8n workflow with webhook, API calls, branches, retries, waits |
| Demonstrate reliability | retries, idempotency, error states, audit logs, tests |
| Demonstrate security | least privilege, approval gate, no direct provisioning, PII minimization |
| Explain MCP/API collaboration | Specialized HR, Slack, Training, ITSM, Policy, Audit tools exposed through APIs or MCP servers |

---

## 22. Deliverable Compliance Matrix

| Required deliverable | What to submit or show | Coverage status |
|---|---|---|
| 1–2 page solution design | `docs/solution_design_1_2_pages.md` using Section 30 as the compressed source | Covered |
| Architecture description | n8n orchestrator, FastAPI mocks, PostgreSQL state/audit, LLM adapter, approval gate | Covered |
| How AI agent is applied | LLM summaries/explanations only; deterministic services handle policy/action decisions | Covered |
| Orchestration explanation | Webhook/manual trigger, API calls, branch nodes, wait states, retries, approval flow | Covered |
| Trade-offs and assumptions | Mock SaaS, local LLM, PostgreSQL prototype, no direct provisioning, production path defined | Covered |
| MCP/API collaboration | Specialized APIs/MCP servers for HR, Training, Slack, Policy, Approval, ITSM, Audit | Covered |
| Lightweight prototype | Docker Compose + n8n workflow export + FastAPI mock services + PostgreSQL + Ollama | Covered |
| Mock service calls | HR, Training, Slack, Salesforce/access, Approval, ITSM, Audit endpoints | Covered |
| LLM-generated message | Employee summary and manager approval message via Ollama/Gemini/OpenAI adapter | Covered |
| Logging/error handling | PostgreSQL audit table, correlation IDs, error states, retries, idempotency tests | Covered |
| Demo notes | Five-minute walkthrough with before-approval and after-approval ticket behavior | Covered |

This matrix should appear either in the README or in a short `docs/deliverable_mapping.md` file. It helps the evaluator see that every item in the prompt is intentionally covered.

---

## 23. Demo Walkthrough

### 23.1 Five-Minute Demo Script

1. Show the assignment scope and say Task 2 was selected.
2. Show the architecture diagram: n8n orchestrator, FastAPI mocks, PostgreSQL, Ollama.
3. Trigger onboarding for `emp_001` from n8n or Swagger.
4. Show HR profile retrieved: role, level, manager.
5. Show training status: some modules complete, some incomplete.
6. Show recommended access: Salesforce, Gong, Slack channel, Outreach.
7. Show LLM-generated employee message.
8. Simulate employee choosing systems.
9. Show manager approval pending state.
10. Simulate manager approval.
11. Show ITSM ticket created after approval.
12. Show audit logs and correlation ID.
13. Explain production path: real SaaS APIs, OIDC/OAuth/SAML, SCIM, secrets manager, monitoring.

### 23.2 Demo Message

> This prototype demonstrates the full onboarding workflow without real SaaS credentials. The agent coordinates mocked enterprise systems through APIs, uses the LLM for human-readable communication, and keeps access decisions controlled by deterministic policy and manager approval.

---

## 24. Production Evolution Path

| Prototype component | Production replacement |
|---|---|
| FastAPI HR mock | Workday, BambooHR, SuccessFactors, or internal HRIS API |
| Slack mock | Real Slack API / Slack app |
| Training mock | LMS API |
| Salesforce mock | Salesforce API |
| ITSM mock | ServiceNow, Jira Service Management, Zendesk, Freshservice |
| `.env` secrets | Secrets manager / vault |
| Local Ollama | Enterprise-approved LLM endpoint, Azure OpenAI, Gemini, or private model gateway |
| Mock identity | OIDC/SAML enterprise SSO |
| Mock provisioning | SCIM/Okta/Azure AD provisioning |
| Basic logs | Centralized observability, SIEM, audit warehouse |
| Manual demo approval | Real Slack interactive approval or ITSM approval workflow |

---

## 25. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| LLM suggests unauthorized access | Deterministic policy validates all systems before action |
| Prompt injection from employee chat | Treat chat as untrusted; LLM cannot change workflow state or policy |
| Duplicate ticket creation | Idempotency key and existing-ticket lookup |
| Manager approval bypass | Ticket endpoint requires approved approval_id |
| Sensitive HR data leakage | Minimize prompt fields; avoid secrets/PII in logs; mask sensitive values |
| Unknown role/level | Return policy_not_found and escalate to HR/IT |
| SaaS API failure | n8n retry/error branches and audit failed action |
| Overclaiming prototype maturity | Clearly label mock APIs and production path separately |

---

## 26. What Not to Build

Avoid these unless explicitly required:

- Kubernetes
- LangChain
- CrewAI
- AutoGen
- React frontend
- Redis
- Full Okta/SCIM implementation
- Real Slack/ServiceNow credentials
- Full enterprise auth
- Full compliance implementation
- Full Agent_X framework
- Full EQC/FIC/SIB tooling

These would add complexity without improving the candidate exercise score.

---

## 27. Final Submission Package

The final candidate submission should include:

```text
README.md
solution_design_1_2_pages.md
prototype_instructions.md
demo_walkthrough.md
docker-compose.yml
.env.example
n8n/hr_onboarding_workflow.json
api/app/... FastAPI code
api/tests/... pytest tests
docs/standards_alignment.md
docs/traceability_matrix.md
```

The README should clearly state:

- What scenario was selected.
- What the agent does.
- How to run on Linux.
- Which systems are mocked.
- How the LLM is used.
- How manager approval works.
- How to run tests.
- How to demo end-to-end.
- How the prototype would become production-grade.
- How this differs from public n8n employee-onboarding templates.

Do not submit the entire planning history or long internal standards as the main deliverable. The evaluator should see a concise solution design and a runnable prototype, with this planning document used only as preparation material.

---

## 28. Final Submission Strategy

The final submitted package should be practical and not overloaded.

### Submit

- `README.md`
- `docs/solution_design_1_2_pages.md`
- `docs/demo_walkthrough.md`
- `docs/standards_alignment.md`
- `docs/deliverable_mapping.md`
- `docker-compose.yml`
- `.env.example`
- `n8n/hr_onboarding_workflow.json`
- `api/app/...`
- `api/tests/...`

### Keep as internal planning material

- Full Agent_X/EQC notes
- Long FIC/SIB/EQC standards documents
- Detailed planning iterations
- Resume/ATS documents
- Any unsupported claims about formal compliance

### Mention only briefly

- Internal Agent_X-inspired methodology
- Compact FICs as implementation discipline
- Production identity standards such as SCIM/OIDC/SAML
- ISO/IEC 42001 and SOC 2 as alignment references, not compliance claims

### Do not claim

- That the prototype is production deployed
- That real SaaS credentials are used
- That access is actually provisioned
- That the prototype is ISO/SOC compliant
- That the n8n onboarding concept itself is novel
- That the LLM makes final authorization decisions

---

## 29. Final Demo Differentiation Checklist

The demo should prove the solution is more than a standard n8n onboarding template.

Show these moments explicitly:

1. The HR source-of-truth record includes role, level, department, and manager.
2. The access recommender returns different access for different role-level pairs.
3. The recommendation includes a rationale based on role-level policy and peer patterns.
4. The employee can select a subset of systems.
5. A restricted system is blocked or excluded.
6. The access request enters `MANAGER_APPROVAL_PENDING`.
7. Attempting to create an IT ticket before approval fails.
8. After manager approval, the same request creates exactly one ticket.
9. Repeating the approved ticket request does not create a duplicate ticket.
10. The audit log shows the full chain with a single correlation ID.

These ten points are the strongest defense against the concern that the project is only a reused n8n template.

---

## 30. Final 1–2 Page Solution Design Summary

This is the compressed version to use in the formal deliverable.

### Solution Design

The proposed system is a role-aware HR onboarding agent for new employees. It uses n8n as the workflow/agent orchestration layer, FastAPI as the mocked enterprise SaaS layer, PostgreSQL for workflow state and audit logging, and Ollama as the default local LLM provider. The prototype runs on Linux through Docker Compose.

This is intentionally not presented as a generic n8n onboarding template. Existing onboarding templates prove the workflow category is valid; this solution differentiates itself through role-level reasoning, peer-pattern access recommendation, asynchronous manager approval, policy validation, and auditable enterprise controls.

The agent starts from a new employee onboarding trigger. It retrieves employee role, level, department, and manager from the HR mock API, checks T1–T4 training status from a training mock API, and recommends access based on an approved role-level access matrix plus peer access patterns from employees with the same role and level. It then asks the employee to select systems, requests manager approval asynchronously, and creates an ITSM ticket only after manager approval.

The LLM is intentionally constrained. It generates employee-facing summaries, manager approval messages, and explanations of access recommendations. It does not decide policy, approve access, grant access, or bypass workflow gates. Deterministic services enforce role-level policy, restricted-system checks, approval status, idempotency, and audit logging.

The workflow is event-driven. n8n receives a webhook/manual trigger, calls the mocked SaaS APIs, branches on missing profile/training/policy conditions, waits for employee selection and manager approval, retries recoverable API failures, and records each action with a correlation ID. FastAPI exposes mock endpoints for HR, Slack, Training, Salesforce, Approval, ITSM, and Audit services. PostgreSQL stores onboarding state, access requests, approvals, tickets, and audit events.

Security and governance are handled through least privilege, human approval, deterministic policy checks, and auditability. The agent can recommend and request access, but it cannot directly provision systems. Selected access is validated against role-level policy before manager approval. IT ticket creation is blocked unless approval is valid. Sensitive HR data is minimized in prompts and logs.

The production path replaces mocks with real SaaS integrations such as Workday/BambooHR, Slack, LMS, Salesforce, ServiceNow/Jira Service Management, Okta/Azure AD, and SCIM provisioning. Authentication and authorization would use OIDC/OAuth/SAML, secrets would move to a secrets manager, and logs would move to centralized observability or audit storage. The design aligns with recognized external frameworks such as NIST AI RMF, OWASP LLM Top 10, ISO/IEC 42001 direction, SOC 2 control thinking, RBAC/ABAC, SCIM, and ITIL-style ITSM workflow.

MCP/API collaboration can be introduced by exposing each specialized capability as an MCP server or API endpoint: HR profile lookup, training status, access policy, Slack messaging, IT ticketing, approval state, and audit logging. The HR onboarding agent remains the coordinator, while each system-specific tool owns its own boundary and permissions.

---

## 31. Final Verdict

This plan is 10/10 for the candidate exercise because it directly satisfies the requirements while staying realistic:

- It uses a recognizable AI workflow platform.
- It integrates multiple mocked SaaS systems.
- It uses an LLM in a safe and explainable way.
- It demonstrates orchestration, reliability, logging, error handling, and approval gates.
- It separates prototype implementation from production evolution.
- It references actual industry standards without falsely claiming compliance.
- It uses internal Agent_X/EQC/FIC-style discipline only as private implementation methodology, not as external standard claims.
- It explicitly differentiates the solution from existing n8n onboarding templates instead of pretending basic onboarding automation is novel.
- It provides a submission strategy and demo checklist that make the originality and requirement coverage visible to evaluators.
- It is practical to build and demo on Linux.

---

## 32. Official References for External Standards and Frameworks

- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF resource center: https://airc.nist.gov/airmf-resources/airmf/
- OWASP Top 10 for Large Language Model Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP GenAI / LLM Top 10: https://genai.owasp.org/llm-top-10/
- ISO/IEC 42001:2023: https://www.iso.org/standard/42001
- AICPA SOC 2 overview: https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2
- AICPA Trust Services Criteria: https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022
- SCIM 2.0 RFC 7643: https://www.rfc-editor.org/rfc/rfc7643
- SCIM 2.0 RFC 7644: https://www.rfc-editor.org/rfc/rfc7644
- OAuth 2.0 RFC 6749: https://www.rfc-editor.org/rfc/rfc6749
- OpenID Connect Core: https://openid.net/specs/openid-connect-core-1_0.html
- SAML 2.0 OASIS standard: https://docs.oasis-open.org/security/saml/v2.0/
- n8n employee onboarding template example: https://n8n.io/workflows/3860-automate-employee-onboarding-with-slack-jira-and-google-workspace-integration/
- n8n provisioning new employee accounts template: https://n8n.io/workflows/12090-provision-new-employee-accounts-to-google-workspace-slack-jira-and-salesforce/
- n8n HR workflow templates category: https://n8n.io/workflows/categories/hr/
