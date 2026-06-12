import json
import sys
import os
import re

WORKFLOW_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "n8n", "hr_onboarding_workflow.json")
API_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api")

UNSUPPORTED_TYPES = {
    "n8n-nodes-base.slack",
    "n8n-nodes-base.googleSheets",
    "n8n-nodes-base.jira",
    "n8n-nodes-base.salesforce",
    "n8n-nodes-base.gmail",
    "n8n-nodes-base.microsoftOutlook",
}

REQUIRED_NODE_PATTERNS = {
    "webhook": ["n8n-nodes-base.webhook"],
    "http_request": ["n8n-nodes-base.httpRequest"],
    "if_logic": ["n8n-nodes-base.if", "n8n-nodes-base.switch"],
    "respond_to_webhook": ["n8n-nodes-base.respondToWebhook"],
}

OUTPUT_FIELDS_REQUIRED = [
    "pre_approval_blocked",
    "ticket_created",
    "approval_status",
    "ticket_id",
    "correlation_id",
]

# Matches n8n template expressions like {{ $node['Foo'].json['employee_id'] }} or .employee_id
TEMPLATE_PATTERN = re.compile(r"\{\{\s*\$node\[[^\]]+\]\.json(?:\[['\"]?(\w+)['\"]?\]|\.(\w+))\s*\}\}")
# Matches the base URL prefix like ={{ $node['...'].json['api_base_url'] }} or .api_base_url
BASE_URL_PATTERN = re.compile(r"^=\{\{\s*\$node\[[^\]]+\]\.json(?:\[['\"]?api_base_url['\"]?\]|\.api_base_url)\s*\}\}/")


def normalize_n8n_url(raw_url: str) -> str | None:
    if not raw_url or not raw_url.startswith("="):
        return raw_url
    stripped = BASE_URL_PATTERN.sub("", raw_url)
    path = TEMPLATE_PATTERN.sub(r"{\1\2}", stripped)
    path = "/" + path.lstrip("/")
    return path


def get_openapi_paths():
    try:
        sys.path.insert(0, API_DIR)
        from app.main import app
        from app.database import engine
        from app.models import Base
        Base.metadata.create_all(bind=engine)
        paths = set(app.openapi()["paths"].keys())
        return paths
    except Exception as e:
        print(f"WARN: Could not load FastAPI app to get OpenAPI paths: {e}")
        return None


errors = []

try:
    with open(WORKFLOW_PATH) as f:
        wf = json.load(f)
except FileNotFoundError:
    print(f"FAIL: Workflow file not found at {WORKFLOW_PATH}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"FAIL: Workflow file is not valid JSON")
    sys.exit(1)

if "nodes" not in wf or not isinstance(wf["nodes"], list):
    errors.append("Workflow must have a 'nodes' array")

nodes = wf.get("nodes", [])
if not nodes:
    errors.append("Workflow has zero nodes")

node_types = set()
node_names = set()
respond_to_webhook_found = False
pre_approval_ticket_found = False
approval_branch_found = False

for node in nodes:
    nt = node.get("type", "")
    node_types.add(nt)
    node_names.add(node.get("name", ""))

    if "respond" in nt.lower() or "Respond to Webhook" == node.get("name", ""):
        respond_to_webhook_found = True
    if "Pre-Approval" in node.get("name", "") or "pre_approval" in nt.lower():
        pre_approval_ticket_found = True
    if "approval" in node.get("name", "").lower() and "if" in nt.lower():
        approval_branch_found = True

for unsupported in UNSUPPORTED_TYPES:
    if unsupported in node_types:
        errors.append(f"Unsupported node type found: {unsupported}")

credential_nodes = []
for node in nodes:
    if node.get("credentials") and any(v is not None for v in node["credentials"].values()):
        credential_nodes.append(node.get("name", "unknown"))

if credential_nodes:
    names = ", ".join(credential_nodes)
    errors.append(f"Workflow has nodes with credentials set: {names}")

if not respond_to_webhook_found:
    errors.append("Workflow must contain a Respond to Webhook node")

if not pre_approval_ticket_found:
    errors.append("Workflow must contain a pre-approval ticket attempt node")

if not approval_branch_found:
    errors.append("Workflow must contain an approval branch node")

wf_text = json.dumps(wf)

if "n8n/hr_onboarding_complete_workflow.json" in wf_text:
    errors.append("Workflow references old workflow filename 'n8n/hr_onboarding_complete_workflow.json'")

for field in OUTPUT_FIELDS_REQUIRED:
    if field not in wf_text:
        errors.append(f"Workflow must reference output field: {field}")

for node in nodes:
    if node.get("type") == "n8n-nodes-base.webhook":
        webhook_path = node.get("parameters", {}).get("path", "")
        if "hr-onboarding" not in webhook_path:
            errors.append(f"Webhook path should contain 'hr-onboarding' (found: {webhook_path})")

openapi_paths = get_openapi_paths()
if openapi_paths is not None:
    for node in nodes:
        params = node.get("parameters", {})
        raw_url = params.get("url", "")
        if not raw_url:
            continue
        if "mock" not in raw_url and "onboarding" not in raw_url and "health" not in raw_url and "/ready" not in raw_url and "/version" not in raw_url and "/demo/reset" not in raw_url:
            continue
        normalized = normalize_n8n_url(raw_url)
        if normalized and normalized not in openapi_paths:
            errors.append(
                f"HTTP node '{node.get('name')}' calls '{normalized}' "
                f"which is not exposed by the API"
            )
else:
    for node in nodes:
        params = node.get("parameters", {})
        node_url = params.get("url", "")
        if "api_base_url" in wf_text.lower() or "{{" in node_url:
            continue
        if node_url and "mock" in node_url and "localhost" not in node_url and "api" not in node_url:
            errors.append(f"HTTP node '{node.get('name')}' uses URL not based on local API: {node_url}")

if errors:
    print("FAIL: Workflow contract violations:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("OK: Workflow contract passed")
    sys.exit(0)
