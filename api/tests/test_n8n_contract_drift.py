import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CANONICAL_WORKFLOW_NAMES = [
    "hr_onboarding_workflow",
    "hr_training_update_workflow",
    "hr_profile_update_workflow",
    "hr_salesforce_profile_update_workflow",
    "hr_approval_timeout_workflow",
    "HR Onboarding Agent - Complete v1",
]


def get_wf_path():
    return os.path.join(PROJECT_ROOT, "n8n", "hr_onboarding_workflow.json")


def test_canonical_workflow_exists():
    with open(get_wf_path()) as f:
        data = json.load(f)
    wf_name = data.get("name", "")
    assert wf_name in CANONICAL_WORKFLOW_NAMES, f"Workflow name '{wf_name}' not in canonical list"


def test_workflow_endpoint_contract():
    with open(get_wf_path()) as f:
        data = json.load(f)
    nodes = data.get("nodes", [])
    urls = []
    for n in nodes:
        url = n.get("parameters", {}).get("url", "")
        if url:
            urls.append(url)
    mock_calls = [u for u in urls if "mock" in u]
    assert len(mock_calls) > 0, "No mock API calls found in workflow"
