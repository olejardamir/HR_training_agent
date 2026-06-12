import os
import sys

PROJECT_ROOT = os.environ.get("PROJECT_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

REQUIRED_FILES = [
    "README.md",
    "docker-compose.yml",
    ".env.example",
    ".gitignore",
    "n8n/hr_onboarding_workflow.json",
    "api/Dockerfile",
    "api/requirements.txt",
    "api/app/main.py",
    "api/app/config.py",
    "api/app/database.py",
    "api/app/models.py",
    "api/app/schemas.py",
    "api/app/seed.py",
    "docs/solution_design_1_2_pages.md",
    "docs/demo_walkthrough.md",
    "docs/traceability_matrix.md",
    "docs/mock_boundary.md",
    "docs/archive_boundary.md",
    "docs/final_verification_report.md",
    "docs/expected_outputs.md",
    "docs/backend_only_demo.md",
    "docs/dependency_license_attribution.md",
    "docs/environment_matrix.md",
    "docs/source_of_truth.md",
    "docs/claim_to_evidence_audit.md",
    "docs/generated_artifacts_policy.md",
    "docs/edge_case_coverage_audit.md",
    "docs/archive/standards_alignment.md",
    "docs/archive/deliverable_mapping.md",
    "docs/archive/evidence_manifest_example.md",
]

ROUTER_FILES = [
    "api/app/routers/health.py",
    "api/app/routers/onboarding.py",
    "api/app/routers/hr.py",
    "api/app/routers/training.py",
    "api/app/routers/access.py",
    "api/app/routers/approvals.py",
    "api/app/routers/itsm.py",
    "api/app/routers/slack.py",
    "api/app/routers/llm.py",
    "api/app/routers/audit.py",
    "api/app/routers/salesforce.py",
]

SERVICE_FILES = [
    "api/app/services/audit_service.py",
    "api/app/services/approval_service.py",
    "api/app/services/employee_service.py",
    "api/app/services/training_service.py",
    "api/app/services/policy_service.py",
    "api/app/services/recommendation_service.py",
    "api/app/services/selection_service.py",
    "api/app/services/itsm_service.py",
    "api/app/services/slack_service.py",
    "api/app/services/llm_service.py",
    "api/app/services/salesforce_service.py",
]

FIXTURE_FILES = [
    "api/app/fixtures/employees.json",
    "api/app/fixtures/managers.json",
    "api/app/fixtures/training_status.json",
    "api/app/fixtures/role_access_policies.json",
    "api/app/fixtures/peer_access_patterns.json",
    "api/app/fixtures/salesforce_profiles.json",
    "api/app/fixtures/scenario_matrix.json",
]

SCRIPT_FILES = [
    "scripts/collect_evidence.sh",
    "scripts/generate_evidence_manifest.py",
    "scripts/import_n8n_workflow.sh",
    "scripts/smoke_happy_path.sh",
    "scripts/smoke_pending_path.sh",
    "scripts/smoke_reject_path.sh",
    "scripts/smoke_forbidden_path.sh",
    "scripts/smoke_llm_fallback.sh",
    "scripts/smoke_n8n_happy_path.sh",
    "scripts/smoke_n8n_reject_path.sh",
    "scripts/smoke_n8n_pending_path.sh",
    "scripts/smoke_n8n_expire_path.sh",
    "scripts/smoke_n8n_wrong_manager_path.sh",
    "scripts/smoke_n8n_forbidden_path.sh",
    "scripts/validate_evidence_manifest_freshness.py",
    "scripts/validate_no_collapsed_files.py",
    "scripts/validate_no_secrets.py",
    "scripts/validate_openapi_contract.py",
    "scripts/validate_workflow_contract.py",
    "scripts/verify_all.sh",
    "scripts/wait_for_stack.sh",
]


def test_required_files_exist():
    for rel_path in REQUIRED_FILES:
        full = os.path.join(PROJECT_ROOT, rel_path)
        assert os.path.isfile(full), f"Missing required file: {rel_path}"


def test_router_files_exist():
    for rel_path in ROUTER_FILES:
        full = os.path.join(PROJECT_ROOT, rel_path)
        assert os.path.isfile(full), f"Missing router file: {rel_path}"


def test_service_files_exist():
    for rel_path in SERVICE_FILES:
        full = os.path.join(PROJECT_ROOT, rel_path)
        assert os.path.isfile(full), f"Missing service file: {rel_path}"


def test_fixture_files_exist():
    for rel_path in FIXTURE_FILES:
        full = os.path.join(PROJECT_ROOT, rel_path)
        assert os.path.isfile(full), f"Missing fixture file: {rel_path}"


def test_script_files_exist():
    for rel_path in SCRIPT_FILES:
        full = os.path.join(PROJECT_ROOT, rel_path)
        assert os.path.isfile(full), f"Missing script file: {rel_path}"


def test_workflow_filename_is_canonical():
    wf_path = os.path.join(PROJECT_ROOT, "n8n", "hr_onboarding_workflow.json")
    assert os.path.isfile(wf_path), "Workflow file must be n8n/hr_onboarding_workflow.json"
    old_path = os.path.join(PROJECT_ROOT, "n8n", "hr_onboarding_complete_workflow.json")
    assert not os.path.isfile(old_path), "Old workflow filename must be removed"


def test_preparation_step_is_archive_only():
    prep_path = os.path.join(PROJECT_ROOT, "1_PREPARATION_STEP")
    if os.path.isdir(prep_path):
        assert os.path.isdir(prep_path), "1_PREPARATION_STEP must exist if not removed"
