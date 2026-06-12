# HR Onboarding Agent – Governed Access Request Orchestration

**Candidate exercise:** Enterprise Agent – Solutions Developer (HR scenario)  
**Stack:** n8n + FastAPI + PostgreSQL + Ollama/fallback + Docker Compose  
**Runtime:** Free Linux, no paid SaaS credentials

---

## What This Is

A production‑shaped HR onboarding agent that:
- Identifies new employee role, level, department, manager from HR source of truth.
- Recommends access using role‑level policy + same‑role peer patterns.
- Requires employee selection and asynchronous manager approval.
- **Blocks IT ticket creation until approval is granted.**
- Logs every decision with a correlation ID.

This is **not** a generic n8n onboarding template. It adds deterministic governance, auditability, and a safe LLM boundary.

---

## Quick Start (Linux)

```bash
git clone <repo> hr-onboarding-agent
cd hr-onboarding-agent
cp .env.example .env
docker compose up --build
```

Then in another terminal:
```bash
# Check health
curl http://localhost:8000/health

# Import n8n workflow (open http://localhost:5678, import from file n8n/hr_onboarding_workflow.json)

# Run demo happy path
curl -X POST http://localhost:5678/webhook/hr-onboarding \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"emp_001","selected_systems":["Salesforce","Gong"],"auto_approve_manager":true}'
```

---

## Services

| Service | URL | Credentials |
|---------|-----|--------------|
| n8n workflow UI | http://localhost:5678 | none (self‑hosted) |
| FastAPI Swagger | http://localhost:8000/docs | none |
| PostgreSQL | localhost:5432 | `hr_agent` / `hr_agent_dev_password` |

---

## What Is Mocked vs Real

| Component | Implementation | Production path |
|-----------|----------------|-----------------|
| HR platform | FastAPI + PostgreSQL fixture | Workday, BambooHR, etc. |
| Slack | FastAPI + `slack_messages` table | Real Slack API |
| Training | FastAPI + fixture | LMS API |
| ITSM | FastAPI + `itsm_tickets` table | ServiceNow, Jira SM |
| LLM | Ollama or deterministic fallback | Enterprise LLM gateway |

All mock services are **stateful** (PostgreSQL) and support failure cases (unknown employee, missing manager, etc.).

---

## Testing

Run the test suite:
```bash
docker compose exec api pytest -v
```

Critical tests:
- `test_recommendations_for_emp_001` – checks role/level and peer patterns
- `test_ticket_blocked_before_approval` – proves approval gate
- `test_employee_summary_fallback` – LLM/fallback works without Ollama

---

## Key Differentiators from Basic n8n Templates

| Basic n8n onboarding | This agent |
|----------------------|-------------|
| Creates accounts / sends notifications | Recommends access based on role, level, and peer patterns |
| Simple task list | Policy validation + asynchronous manager approval |
| May create IT task directly | Ticket creation blocked until **approved** |
| Minimal logging | Full audit trail with correlation ID |
| LLM used for free‑form chat | LLM only for summaries, no authorization |

---

## Project Structure

```
hr-onboarding-agent/
├── docker-compose.yml
├── .env.example
├── evidence_manifest.json        # generated after full verification
├── README.md
├── docs/
│   ├── solution_design_1_2_pages.md
│   ├── demo_walkthrough.md
│   ├── standards_alignment.md
│   ├── traceability_matrix.md
│   └── evidence_manifest_example.md
├── scripts/
│   ├── validate_no_collapsed_files.py
│   ├── validate_no_secrets.py
│   ├── validate_workflow_contract.py
│   ├── generate_evidence_manifest.py
│   ├── smoke_happy_path.sh
│   ├── smoke_pending_path.sh
│   ├── smoke_reject_path.sh
│   ├── smoke_forbidden_path.sh
│   └── smoke_llm_fallback.sh
├── n8n/
│   └── hr_onboarding_workflow.json
├── api/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── seed.py
│   │   ├── schemas.py
│   │   ├── fixtures/
│   │   │   ├── employees.json
│   │   │   ├── training_status.json
│   │   │   ├── role_access_policies.json
│   │   │   ├── peer_access_patterns.json
│   │   │   ├── department_standards.json
│   │   │   └── salesforce_profiles.json
│   │   ├── logic/
│   │   │   └── access_recommender.py
│   │   └── services/
│   │       ├── approval_service.py
│   │       ├── itsm_service.py
│   │       ├── audit_service.py
│   │       └── llm_service.py
│   └── tests/
│       ├── test_access_recommender.py
│       ├── test_approval_gate.py
│       └── test_llm_fallback.py
└── private/                     # implementation guides (not needed at runtime)
```

---

## Production Evolution

See `docs/solution_design_1_2_pages.md` for the production path. In summary:
- Replace mocks with real SaaS APIs (Workday, Slack, ServiceNow, etc.)
- Add OIDC/OAuth2 authentication
- Use a secrets manager
- Replace local Ollama with enterprise LLM endpoint
- Export audit logs to SIEM

---

## License & Attribution

This prototype is built for a candidate exercise. All external standards are referenced for alignment; no compliance claim is made. The n8n workflow is original but inspired by public patterns; the value is the custom backend governance.

---

## Evaluation Checklist

The evaluator can verify:
- [ ] Runs on Linux without paid services
- [ ] Role/level sourced from HR mock, not user input
- [ ] Recommendations include peer‑pattern reason codes
- [ ] Forbidden systems rejected
- [ ] Pre‑approval ticket attempt blocked (403)
- [ ] Post‑approval ticket created (idempotent)
- [ ] Audit trail shows correlation ID
- [ ] LLM/fallback works without external keys
- [ ] Differentiators from basic templates are documented

---

**Ready to demo?** Follow `docs/demo_walkthrough.md` for a 5‑minute guided tour.
