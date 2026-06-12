import subprocess
import sys
import os

PROJECT_ROOT = os.environ.get("PROJECT_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VALIDATOR = os.path.join(PROJECT_ROOT, "scripts", "validate_workflow_contract.py")


def test_workflow_contract_passes():
    result = subprocess.run(
        [sys.executable, VALIDATOR],
        capture_output=True, text=True, timeout=30, cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0, (
        f"Workflow contract validation failed:\n{result.stdout}\n{result.stderr}"
    )


def test_workflow_contract_negative_passes():
    result = subprocess.run(
        [sys.executable, VALIDATOR, "--negative"],
        capture_output=True, text=True, timeout=30, cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0, (
        f"Workflow negative contract validation failed:\n{result.stdout}\n{result.stderr}"
    )


def test_workflow_file_exists():
    wf_path = os.path.join(PROJECT_ROOT, "n8n", "hr_onboarding_workflow.json")
    assert os.path.exists(wf_path), f"Workflow file not found at {wf_path}"
