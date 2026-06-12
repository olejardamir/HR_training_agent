import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def get_wf_path():
    return os.path.join(PROJECT_ROOT, "n8n", "hr_onboarding_workflow.json")


def test_workflow_json_exists():
    assert os.path.isfile(get_wf_path())


def test_workflow_valid_json():
    with open(get_wf_path()) as f:
        data = json.load(f)
    assert "nodes" in data
    assert "connections" in data
    assert len(data["nodes"]) > 0


def test_workflow_no_empty_nodes():
    with open(get_wf_path()) as f:
        data = json.load(f)
    for node in data["nodes"]:
        assert node.get("name"), f"Node without name found"
        assert node.get("type"), f"Node {node.get('name')} without type"


def test_workflow_has_start():
    with open(get_wf_path()) as f:
        data = json.load(f)
    types = [n["type"] for n in data["nodes"]]
    assert "n8n-nodes-base.manualTrigger" in types or "n8n-nodes-base.webhook" in types
