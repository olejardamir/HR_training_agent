# Evidence Manifest Example

The evidence manifest is a generated file (`evidence_manifest.json`) produced during final verification. Do not commit it — generate it only after all checks pass.

## Schema

```json
{
  "generated_at": "2026-06-11T00:00:00Z",
  "repo_commit": "local-or-git-sha",
  "checks": {
    "docker_compose_config": "pass",
    "api_health": "pass",
    "api_ready": "pass",
    "pytest": "pass",
    "n8n_workflow_static_validation": "pass",
    "no_collapsed_files": "pass",
    "no_secrets": "pass",
    "happy_path_smoke": "pass",
    "pending_path_smoke": "pass",
    "reject_path_smoke": "pass",
    "forbidden_path_smoke": "pass",
    "llm_fallback_smoke": "pass"
  },
  "artifacts": {
    "workflow": "n8n/hr_onboarding_workflow.json",
    "solution_design": "docs/solution_design_1_2_pages.md",
    "demo_walkthrough": "docs/demo_walkthrough.md",
    "traceability": "docs/traceability_matrix.md"
  }
}
```

## Required Checks

| Check | Command | Expected |
|---|---|---|
| Docker Compose config | `docker compose config` | No errors |
| API health | `curl -fsS http://localhost:8000/health` | `{"status":"healthy"}` |
| API ready | `curl -fsS http://localhost:8000/ready` | `{"status":"ready"}` |
| Pytest | `docker compose exec api pytest -q` | All tests pass |
| n8n workflow validation | `python scripts/validate_workflow_contract.py` | Exit 0 |
| No collapsed files | `python scripts/validate_no_collapsed_files.py` | Exit 0 |
| No secrets | `python scripts/validate_no_secrets.py` | Exit 0 |
| Happy path smoke | `bash scripts/smoke_happy_path.sh` | Exit 0 |
| Pending path smoke | `bash scripts/smoke_pending_path.sh` | Exit 0 |
| Reject path smoke | `bash scripts/smoke_reject_path.sh` | Exit 0 |
| Forbidden path smoke | `bash scripts/smoke_forbidden_path.sh` | Exit 0 |
| LLM fallback smoke | `bash scripts/smoke_llm_fallback.sh` | Exit 0 |

## Generation Command

```bash
python scripts/generate_evidence_manifest.py
```

This script runs all checks and produces `evidence_manifest.json` only when all pass.
