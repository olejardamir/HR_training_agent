# HR Onboarding Agent – Governed Access Request Orchestration

**Candidate exercise:** Enterprise Agent – Solutions Developer (HR scenario)  
**Stack:** n8n + FastAPI + PostgreSQL + Ollama/fallback + Docker Compose  
**Runtime:** Free Linux, no paid SaaS credentials

---

## What This Is

A governance‑first HR onboarding agent that:
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

# Import n8n workflow (automated via CLI)
bash scripts/import_n8n_workflow.sh

# Run demo — happy path
curl -X POST http://localhost:5678/webhook/hr-onboarding/new-hire \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"emp_001","selected_systems":["Salesforce","Gong"],"approval_action":"approve"}'
```

---

## Services

| Service | URL | Credentials |
|---------|-----|-------------|
| n8n workflow UI | http://localhost:5678 | Authentication disabled for local demo |
| FastAPI Swagger | http://localhost:8000/docs | none |
| PostgreSQL | localhost:5432 | `hr_agent` / `hr_agent_dev_password` |

---

## Webhook Input Contract

Trigger at `POST /webhook/hr-onboarding/new-hire`:

```json
{
  "employee_id": "emp_001",
  "selected_systems": ["Salesforce", "Gong"],
  "approval_action": "approve"
}
```

Supported `approval_action` values:

| Value | Behavior |
|-------|----------|
| `approve` | Manager approves → ticket created |
| `reject` | Manager rejects → no ticket |
| `expire` | Approval expired → no ticket |
| `pending` | No decision made → no ticket |
| `wrong_manager` | Wrong manager attempts → blocked |

Backward compatible: `auto_approve_manager=true` maps to `approve`, `false` to `pending`.

---

## Demo Scenarios

See `docs/demo_walkthrough.md` for 7 guided scenarios (happy, pending, reject, expire,
forbidden, wrong-manager, LLM fallback).

---

## Testing

```bash
# One-command verification (infra, tests, contracts, smokes)
bash scripts/verify_all.sh

# Or run individual checks:

# Backend tests (84 tests)
docker compose exec api pytest -v

# Direct FastAPI smoke scripts
bash scripts/smoke_happy_path.sh
bash scripts/smoke_pending_path.sh
bash scripts/smoke_reject_path.sh
bash scripts/smoke_forbidden_path.sh
bash scripts/smoke_llm_fallback.sh

# n8n webhook smoke scripts (after workflow import)
bash scripts/smoke_n8n_happy_path.sh
bash scripts/smoke_n8n_reject_path.sh
bash scripts/smoke_n8n_pending_path.sh
bash scripts/smoke_n8n_expire_path.sh
bash scripts/smoke_n8n_wrong_manager_path.sh
bash scripts/smoke_n8n_forbidden_path.sh

# Workflow contract validator (static + 24 negative tests)
python3 scripts/validate_workflow_contract.py
python3 scripts/validate_workflow_contract.py --negative

# OpenAPI endpoint contract check
python3 scripts/validate_openapi_contract.py

# Regenerate evidence manifest
python3 scripts/generate_evidence_manifest.py
```

---

## What Is Mocked vs Real

| Component | Implementation | Production path |
|-----------|----------------|-----------------|
| HR platform | FastAPI + PostgreSQL fixture | Workday, BambooHR |
| Slack | FastAPI + `slack_messages` table | Real Slack API |
| Training | FastAPI + fixture | LMS API |
| ITSM | FastAPI + `itsm_tickets` table | ServiceNow, Jira SM |
| LLM | Ollama (gemma2:2b) with deterministic template fallback | Enterprise LLM gateway |
| Salesforce | FastAPI + `salesforce_profiles` table | Real Salesforce API |

All mocks are **stateful** (PostgreSQL) and handle edge cases (unknown employee,
missing manager, forbidden systems, wrong manager).

---

## Key Differentiators from Basic n8n Templates

| Basic n8n onboarding | This agent |
|----------------------|-------------|
| Creates accounts / sends notifications | Recommends access based on role, level, peer patterns |
| Simple task list | Policy validation + async manager approval |
| May create IT task directly | Ticket creation blocked until **approved** |
| Minimal logging | Full audit trail with correlation ID |
| LLM for free‑form chat | LLM only for summaries, no authorization |

---

## Project Structure

```
hr-onboarding-agent/
├── docker-compose.yml
├── .env.example
├── evidence_manifest.json
├── README.md
├── docs/
│   ├── solution_design_1_2_pages.md
│   ├── demo_walkthrough.md
│   ├── traceability_matrix.md
│   ├── final_verification_report.md
│   ├── expected_outputs.md
│   ├── backend_only_demo.md
│   ├── dependency_license_attribution.md
│   ├── environment_matrix.md
│   ├── source_of_truth.md
│   ├── claim_to_evidence_audit.md
│   ├── generated_artifacts_policy.md
│   ├── archive_boundary.md
│   ├── demo_outputs/  (live-captured evidence)
│   └── archive/       (historical planning docs)
├── scripts/
│   ├── verify_all.sh
│   ├── wait_for_stack.sh
│   ├── import_n8n_workflow.sh
│   ├── collect_evidence.sh
│   ├── generate_evidence_manifest.py
│   ├── validate_workflow_contract.py
│   ├── validate_openapi_contract.py
│   ├── validate_no_collapsed_files.py
│   ├── validate_no_secrets.py
│   ├── smoke_happy_path.sh
│   ├── smoke_pending_path.sh
│   ├── smoke_reject_path.sh
│   ├── smoke_forbidden_path.sh
│   ├── smoke_llm_fallback.sh
│   ├── smoke_n8n_happy_path.sh
│   ├── smoke_n8n_reject_path.sh
│   ├── smoke_n8n_pending_path.sh
│   ├── smoke_n8n_expire_path.sh
│   ├── smoke_n8n_wrong_manager_path.sh
│   └── smoke_n8n_forbidden_path.sh
├── n8n/
│   └── hr_onboarding_workflow.json
└── api/
    ├── app/ (FastAPI)
    │   ├── routers/ (endpoints)
    │   ├── services/ (business logic)
    │   ├── logic/ (recommender)
    │   ├── models.py, schemas.py, seed.py
    │   └── fixtures/ (seed data)
    └── tests/ (pytest)
```

---

## Evidence & Verification

Every commit is verified against 20 checks in `evidence_manifest.json`. See also `docs/generated_artifacts_policy.md` for which files are committed evidence vs local artifacts.

```
docker compose config -q                      # Compose file valid
curl -fsS http://localhost:8000/health         # API healthy
curl -fsS http://localhost:8000/ready          # DB + seed loaded
docker compose exec -T api pytest -q           # 84 tests pass
scripts/validate_workflow_contract.py          # Workflow matches contract
scripts/validate_openapi_contract.py           # OpenAPI endpoint conformance
scripts/validate_no_collapsed_files.py         # No truncated files
scripts/validate_no_secrets.py                 # No credentials leaked
smoke_happy_path.sh                            # Approve → ticket
smoke_pending_path.sh                          # Pending → no ticket
smoke_reject_path.sh                           # Reject → no ticket
smoke_forbidden_path.sh                        # Forbidden → 403
smoke_llm_fallback.sh                          # Ollama or fallback text
bash scripts/smoke_n8n_happy_path.sh           # n8n webhook approve path
bash scripts/smoke_n8n_reject_path.sh          # n8n webhook reject path
bash scripts/smoke_n8n_pending_path.sh         # n8n webhook pending path
bash scripts/smoke_n8n_expire_path.sh          # n8n webhook expire path
bash scripts/smoke_n8n_wrong_manager_path.sh   # n8n webhook wrong-manager path
bash scripts/smoke_n8n_forbidden_path.sh       # n8n webhook forbidden path
scripts/validate_workflow_contract.py --negative    # Negative tests (24 mutants)
scripts/validate_evidence_manifest_freshness.py     # Manifest commit matches HEAD
```

---

## Mini-RAG Onboarding Knowledge

The chatbot uses a small local retrieval layer over approved onboarding/training content from `docs/PREPARATION_DOCS/PROMOTED_RUNTIME/app_content/`. It uses sentence-transformers (with TF-IDF fallback) for embedding and cosine similarity retrieval.

The chatbot is read-only (audit logging only) and retrieves approved onboarding/training guidance only. It does not decide access, approval, ticket creation, training completion, Salesforce setup, or profile updates. Those remain controlled by deterministic workflow/database logic. If approved guidance is missing, the chatbot refuses to invent guidance, while still allowing simple status answers from deterministic employee/workflow state.

The mini-RAG is evaluated with retrieval, grounding, prompt-injection, read-only, and observability tests. It retrieves approved onboarding/training guidance only, logs trace metadata (including latency, match count, retrieval method), refuses unsupported guidance, and does not mutate workflow state through `/agent/chat`.

Build the index (reproducible from committed fixtures):
```bash
bash scripts/build_rag_index.sh
```

Test chat:
```bash
curl -s -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"emp_001","message":"What do I need to do for T2?"}' | jq
```

---

## If n8n import fails on your machine

1. The **backend-only smoke path** (`bash scripts/smoke_happy_path.sh` etc.) still proves the governance logic — see `docs/backend_only_demo.md`.
2. The n8n workflow JSON (`n8n/hr_onboarding_workflow.json`) can be inspected statically.
3. The workflow contract validator (`scripts/validate_workflow_contract.py`) confirms endpoint/field alignment.
4. Golden response snapshots are in `docs/demo_outputs/golden_responses/`.

---

## License & Attribution

This prototype is built for a candidate exercise. All external standards are
referenced for alignment; no compliance claim is made. See `docs/dependency_license_attribution.md` for details.

---

**Ready to demo?** Follow `docs/demo_walkthrough.md` for a guided tour of all 7 paths.
