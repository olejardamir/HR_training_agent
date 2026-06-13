# HR Onboarding Agent – Demo Walkthrough

**Duration:** ~5 minutes  
**Assumptions:** Local stack running (`docker compose up --build`), n8n accessible at `http://localhost:5678`, FastAPI at `http://localhost:8000`.

---

## Path A – Happy Path (Ticket Created)

1. **Trigger onboarding**
   ```bash
   curl -X POST http://localhost:5678/webhook/hr-onboarding/new-hire \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","selected_systems":["Salesforce","Gong","Sales Slack Channels"],"approval_action":"approve"}'
   ```

2. **Expected response fields:**
   - `correlation_id` – traceable across all steps
   - `approval_status` – `APPROVED`
   - `pre_approval_blocked` – `true`
   - `ticket_created` – `true`
   - `ticket_id` – present (e.g. `itsm_<uuid>`)
   - `audit_event_count` – > 0

3. **Verify** – `GET /audit/events?correlation_id=...` shows the full chain including approval, ticket creation.

---

## Path B – Pending Path (No Ticket)

1. **Trigger with approval_action = pending**
   ```bash
   curl -X POST http://localhost:5678/webhook/hr-onboarding/new-hire \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","selected_systems":["Salesforce"],"approval_action":"pending"}'
   ```

2. **Expected:** Approval remains PENDING, no approval decision call is made, no ITSM ticket is created.

3. **Response fields:**
   - `correlation_id` – traceable across all steps
   - `approval_status` – `PENDING`
   - `pre_approval_blocked` – `true`
   - `ticket_created` – `false`
   - `ticket_id` – absent
   - `audit_event_count` – > 0

---

## Path C – Reject Path (No Ticket)

1. **Trigger with approval_action = reject**
   ```bash
   curl -X POST http://localhost:5678/webhook/hr-onboarding/new-hire \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","selected_systems":["Salesforce"],"approval_action":"reject"}'
   ```

2. **Expected:** Approval is rejected, no ITSM ticket is created.

3. **Response fields:**
   - `correlation_id` – traceable across all steps
   - `approval_status` – `REJECTED`
   - `pre_approval_blocked` – `true`
   - `ticket_created` – `false`
   - `ticket_id` – absent
   - `audit_event_count` – > 0

---

## Path D – Expire Path (No Ticket)

1. **Trigger with approval_action = expire**
   ```bash
   curl -X POST http://localhost:5678/webhook/hr-onboarding/new-hire \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","selected_systems":["Salesforce"],"approval_action":"expire"}'
   ```

2. **Expected:** Approval is expired, no ITSM ticket is created.

3. **Response fields:**
   - `correlation_id` – traceable across all steps
   - `approval_status` – `EXPIRED`
   - `pre_approval_blocked` – `true`
   - `ticket_created` – `false`
   - `ticket_id` – absent
   - `audit_event_count` – > 0

---

## Path E – Forbidden System Blocked

1. **Trigger with a forbidden system (e.g., Payroll Admin)**
   ```bash
   curl -X POST http://localhost:5678/webhook/hr-onboarding/new-hire \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","selected_systems":["Salesforce","Payroll Admin"],"approval_action":"approve"}'
   ```

2. **Expected:** The selection endpoint returns HTTP 403 with `FORBIDDEN_SYSTEM_SELECTED`. Workflow stops at selection node; no approval or ticket created.

3. **Response fields:**
   - `correlation_id` – traceable across all steps
   - `approval_status` – `FORBIDDEN`
   - `ticket_created` – `false`
   - `forbidden` – `true`
   - `pre_approval_blocked` – `false`
   - `ticket_id` – absent
   - `audit_event_count` – > 0 (includes `selection_blocked`)

---

## Path F – Wrong Manager Path (Decision Blocked)

1. **Trigger with approval_action = wrong_manager**
   ```bash
   curl -X POST http://localhost:5678/webhook/hr-onboarding/new-hire \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","selected_systems":["Salesforce"],"approval_action":"wrong_manager"}'
   ```

2. **Expected:** The approval decision is attempted with a wrong manager ID (`mgr_wrong`), blocked by backend with 403. The approval remains PENDING, no ticket created.

3. **Response fields:**
   - `correlation_id` – traceable across all steps
   - `approval_status` – `PENDING` (wrong manager blocked, original approval unchanged)
   - `pre_approval_blocked` – `true`
   - `ticket_created` – `false`
   - `ticket_id` – absent
   - `audit_event_count` – > 0

---

## Path G – LLM Fallback

1. **Trigger (no Ollama needed)**
   ```bash
   curl -X POST http://localhost:5678/webhook/hr-onboarding/new-hire \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","selected_systems":["Salesforce"],"approval_action":"approve"}'
   ```

2. **Expected:** LLM/fallback generates text messages for employee summary and manager approval request without external keys. Messages are stored in Slack mock.

3. **Response fields:**
   - `correlation_id` – traceable across all steps
   - `approval_status` – `APPROVED`
   - `pre_approval_blocked` – `true`
   - `ticket_created` – `true`
   - `ticket_id` – present (e.g. `itsm_<uuid>`)
   - `audit_event_count` – > 0

---

## Backward Compatibility

The workflow also accepts `auto_approve_manager`:
- `auto_approve_manager=true` maps to `approval_action=approve`
- `auto_approve_manager=false` maps to `approval_action=pending`

---

## Inspecting Evidence

- **FastAPI Swagger UI** – `http://localhost:8000/docs`
- **Audit events** – `GET /audit/events?correlation_id=...`
- **n8n execution log** – Shows each node's input/output
- **PostgreSQL** – `psql -h localhost -U hr_agent -d hr_onboarding`

---

## Mini-RAG Chat Demo

1. **Build the index**
   ```bash
   bash scripts/build_rag_index.sh
   ```

2. **Ask about training**
   ```bash
   curl -s -X POST http://localhost:8000/agent/chat \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","message":"What do I need to do for T2?"}' | jq
   ```
   Expected: answer with T2 guidance, `used_content_ids`, and employee state.

3. **Ask about onboarding**
   ```bash
   curl -s -X POST http://localhost:8000/agent/chat \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","message":"How do I update my profile?"}' | jq
   ```

4. **Ask about Salesforce access**
   ```bash
   curl -s -X POST http://localhost:8000/agent/chat \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","message":"Can I request Salesforce access?"}' | jq
   ```
   Expected: the answer explains Salesforce setup steps but does **not** decide access.

5. **Unknown employee returns 404**
   ```bash
   curl -s -X POST http://localhost:8000/agent/chat \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"UNKNOWN","message":"Test"}' | jq
   ```

---

## What the Evaluator Should See

- [ ] No real SaaS credentials required.
- [ ] Role and level come from HR mock, not from user input.
- [ ] Recommendations include reason codes (`ROLE_LEVEL_POLICY`, `PEER_COMMON_ACCESS`, `DEPARTMENT_STANDARD`).
- [ ] Forbidden systems are blocked (403).
- [ ] Pre-approval ticket attempt fails with 409.
- [ ] After approval, ticket is created and idempotent.
- [ ] Pending/rejected/expired/wrong-manager paths do not create tickets.
- [ ] Audit trail shows correlation ID across all steps.
- [ ] LLM/fallback generates human-readable messages but never authorizes access.
- [ ] Mini-RAG chat returns answers with approved content references.
- [ ] Mini-RAG does not decide access/approval/ticket state.

---

## Troubleshooting

- **n8n cannot reach FastAPI** – Ensure `API_BASE_URL` environment variable is set correctly.
- **Ollama not running** – Fallback text is used automatically; demo still works.
- **Database not seeded** – Call `POST /demo/reset`.
