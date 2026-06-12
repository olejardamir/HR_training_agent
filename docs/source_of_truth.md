# Canonical Source of Truth

The following files are the canonical evaluator-facing documents. Old planning documents in `docs/archive/` or `private/` are historical and not required for evaluation.

## Primary Entry Point

| Document | Purpose |
|---|---|
| `README.md` | Primary evaluator entry point — start here |
| `docs/solution_design_1_2_pages.md` | Concise architecture/design submission |
| `docs/demo_walkthrough.md` | Official demo script |
| `docs/traceability_matrix.md` | Requirement-to-evidence mapping |
| `docs/final_verification_report.md` | Final tested commit and command results |
| `evidence_manifest.json` | Machine-readable evidence summary |
| `n8n/hr_onboarding_workflow.json` | Official workflow export |
| `scripts/verify_all.sh` | One-command local verification |

## Supporting Documents

| Document | Purpose |
|---|---|
| `docs/expected_outputs.md` | Expected response shapes per demo path |
| `docs/backend_only_demo.md` | Fallback backend-only demo procedure |
| `docs/environment_matrix.md` | Tested runtime environment |
| `docs/dependency_license_attribution.md` | Dependency and licensing notes |
| `docs/claim_to_evidence_audit.md` | Claim-to-evidence mapping |
| `docs/edge_case_coverage_audit.md` | Edge-case coverage mapping |
| `docs/generated_artifacts_policy.md` | Generated evidence classification policy |
| `docs/archive_boundary.md` | Boundary between live mocks and deferred functionality |
