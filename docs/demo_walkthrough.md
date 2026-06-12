# HR Onboarding Agent – Demo Walkthrough

**Duration:** ~5 minutes  
**Assumptions:** Local stack running (`docker compose up --build`), n8n accessible at `http://localhost:5678`, FastAPI at `http://localhost:8000`.

---

## Path A – Happy Path (Ticket Created)

1. **Trigger onboarding**  
   Open terminal and run:
   ```bash
   curl -X POST http://localhost:5678/webhook/hr-onboarding \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","selected_systems":["Salesforce","Gong","Sales Slack Channels"],"auto_approve_manager":true}'
   ```
2. **Observe the workflow in n8n**  
   - HR profile loaded (role: Account Executive, level: L2, manager: mgr_101)  
   - Training T1‑T4 status loaded  
   - Access recommendations generated (required: Slack, HR Platform; recommended: Salesforce, Gong, Outreach, Sales Slack Channels)  
   - Employee summary created (LLM or fallback) and stored in Slack mock  
   - Employee selection stored and validated (no forbidden systems)  
   - Manager approval request created (PENDING)  
   - Manager approval message generated and stored  
   - **Pre‑approval ticket attempt → blocked** (expected, proves gate)  
   - Auto‑approve triggers manager approval  
   - Approval status becomes APPROVED  
   - ITSM ticket created (returns `ticket_id`)  
   - Final status and audit events retrieved  

3. **Verify outcome**  
   - The workflow returns a `ticket_id`.  
   - FastAPI endpoint `GET /audit/events?correlation_id=...` shows the full chain.

---

## Path B – Negative Path (No Ticket)

1. **Trigger with auto-approve disabled**  
   ```bash
   curl -X POST http://localhost:5678/webhook/hr-onboarding \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","selected_systems":["Salesforce"],"auto_approve_manager":false}'
   ```
2. **Observe**  
   - Pre‑approval ticket attempt is still blocked.  
   - Because `auto_approve_manager=false`, the workflow does **not** call the approve endpoint; approval remains PENDING.  
   - The `Is Approved?` branch goes to "Store No‑Ticket Notice".  
   - No ITSM ticket is created.  

3. **Verify** – The final response contains no `ticket_id`, and `audit_events` show the approval state as PENDING.

---

## Path C – Forbidden System Blocked

1. **Trigger with a forbidden system (e.g., Payroll Admin)**  
   ```bash
   curl -X POST http://localhost:5678/webhook/hr-onboarding \
     -H "Content-Type: application/json" \
     -d '{"employee_id":"emp_001","selected_systems":["Salesforce","Payroll Admin"],"auto_approve_manager":true}'
   ```
2. **Expected** – The selection endpoint (`/onboarding/select-access`) returns HTTP 403 with error `FORBIDDEN_SYSTEM_SELECTED`. The n8n workflow will show a failure at that node (or you can inspect the logs). The workflow does not proceed to approval or ticket creation.

---

## Inspecting Evidence

- **FastAPI Swagger UI** – `http://localhost:8000/docs` – test each mock endpoint manually.  
- **Audit events** – `GET /audit/events?employee_id=emp_001` returns all events.  
- **n8n execution log** – Shows each node's input/output, including blocked pre‑approval call.  
- **PostgreSQL** – Connect with `psql -h localhost -U hr_agent -d hr_onboarding` and query `audit_events`, `itsm_tickets`, etc.

---

## What the Evaluator Should See

- [ ] No real SaaS credentials required.  
- [ ] Role and level come from HR mock, not from user input.  
- [ ] Recommendations include reason codes (ROLE_LEVEL_POLICY, PEER_COMMON_ACCESS, DEPARTMENT_STANDARD).  
- [ ] Forbidden systems are blocked.  
- [ ] Pre‑approval ticket attempt fails with 403.  
- [ ] After approval, ticket is created and idempotent.  
- [ ] Audit trail shows correlation ID across all steps.  
- [ ] LLM/fallback generates human‑readable messages but never authorizes access.

---

## Troubleshooting

- **n8n cannot reach FastAPI** – Ensure `API_BASE_URL` environment variable is set correctly in n8n container or workflow.  
- **Ollama not running** – Fallback text is used automatically; demo still works.  
- **Database not seeded** – Run `docker compose exec api python -m app.seed` or call `POST /demo/reset`.
