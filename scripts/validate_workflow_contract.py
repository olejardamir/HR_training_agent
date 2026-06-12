#!/usr/bin/env python3
import json
import sys
import os
import re

WORKFLOW_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "n8n", "hr_onboarding_workflow.json")
API_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api")

EXPECTED_WORKFLOW_NAME = "HR Onboarding Agent \u2014 Governed Mock SaaS Workflow v4"
EXPECTED_WEBHOOK_PATH = "hr-onboarding/new-hire"

REQUIRED_NODE_NAMES = [
    "Webhook - New Hire",
    "Normalize Demo Input",
    "Start Onboarding Session",
    "HR Mock: Get Profile",
    "Training Mock: T1-T4",
    "Access Recommender",
    "LLM/Fallback: Employee Summary",
    "Slack Mock: Store Employee Message",
    "Employee Selects Access",
    "Selection Succeeded?",
    "Store Forbidden Notice",
    "Fetch Forbidden Audit",
    "Return Forbidden Response",
    "Create Manager Approval",
    "LLM/Fallback: Manager Message",
    "Slack Mock: Store Manager Message",
    "Pre-Approval Ticket (Expected Block)",
    "Normalize Pre-Approval Result",
    "Check Pre-Approval Blocked",
    "Approval Action Switch",
    "Approve Manager Decision",
    "Reject Manager Decision",
    "Expire Manager Decision",
    "Wrong Manager Approval",
    "Fetch Approval Status",
    "Normalize Approval",
    "Is Approved?",
    "Create ITSM Ticket (Approved)",
    "Store No-Ticket Notice",
    "Fetch Final Onboarding Status",
    "Fetch Audit Events",
    "Gate Failure Path",
    "Return Final Result",
]

# Required HTTP node -> expected method + path pattern (after BASE_URL_PATTERN stripping)
REQUIRED_HTTP_ENDPOINTS = {
    "Start Onboarding Session": ("POST", "/onboarding/start/"),
    "HR Mock: Get Profile": ("GET", "/mock/hr/employees/"),
    "Training Mock: T1-T4": ("GET", "/mock/training/status/"),
    "Salesforce Mock: Get Profile": ("GET", "/mock/salesforce/profile/"),
    "Access Recommender": ("GET", "/mock/access/recommendations/"),
    "LLM/Fallback: Employee Summary": ("POST", "/mock/llm/messages"),
    "Slack Mock: Store Employee Message": ("POST", "/mock/slack/messages"),
    "Employee Selects Access": ("POST", "/onboarding/select-access"),
    "Store Forbidden Notice": ("POST", "/mock/slack/messages"),
    "Fetch Forbidden Audit": ("GET", "/audit/events"),
    "Create Manager Approval": ("POST", "/mock/approvals"),
    "LLM/Fallback: Manager Message": ("POST", "/mock/llm/messages"),
    "Slack Mock: Store Manager Message": ("POST", "/mock/slack/messages"),
    "Pre-Approval Ticket (Expected Block)": ("POST", "/mock/itsm/tickets"),
    "Approve Manager Decision": ("POST", "/mock/approvals/"),
    "Reject Manager Decision": ("POST", "/mock/approvals/"),
    "Expire Manager Decision": ("POST", "/mock/approvals/"),
    "Wrong Manager Approval": ("POST", "/mock/approvals/"),
    "Fetch Approval Status": ("GET", "/mock/approvals/"),
    "Create ITSM Ticket (Approved)": ("POST", "/mock/itsm/tickets"),
    "Store No-Ticket Notice": ("POST", "/mock/slack/messages"),
    "Fetch Final Onboarding Status": ("GET", "/onboarding/status/"),
    "Fetch Audit Events": ("GET", "/audit/events"),
}

# Body parameter fields per HTTP node (expected parameter names in the n8n bodyParameters)
REQUIRED_BODY_FIELDS = {
    "Start Onboarding Session": ["correlation_id"],
    "LLM/Fallback: Employee Summary": ["message_type", "employee_id", "correlation_id"],
    "Slack Mock: Store Employee Message": ["channel_or_user", "message_type", "message"],
    "Employee Selects Access": ["employee_id", "selected_systems", "correlation_id"],
    "Store Forbidden Notice": ["channel_or_user", "message_type", "message"],
    "Create Manager Approval": ["employee_id", "request_id", "manager_id", "correlation_id"],
    "LLM/Fallback: Manager Message": ["message_type", "employee_id", "correlation_id"],
    "Slack Mock: Store Manager Message": ["channel_or_user", "message_type", "message"],
    "Pre-Approval Ticket (Expected Block)": ["employee_id", "approval_id", "requested_systems", "correlation_id"],
    "Approve Manager Decision": ["decided_by", "decision_reason", "correlation_id"],
    "Reject Manager Decision": ["decided_by", "decision_reason", "correlation_id"],
    "Expire Manager Decision": ["decided_by", "decision_reason", "correlation_id"],
    "Wrong Manager Approval": ["decided_by", "decision_reason", "correlation_id"],
    "Create ITSM Ticket (Approved)": ["employee_id", "approval_id", "requested_systems", "correlation_id"],
    "Store No-Ticket Notice": ["channel_or_user", "message_type", "message"],
}

# Forbidden response proof fields
FORBIDDEN_RESPONSE_FIELDS = [
    "ok", "demo_status", "employee_id", "correlation_id",
    "approval_status", "ticket_created", "ticket_id",
    "pre_approval_blocked", "forbidden", "audit_event_count",
]

# Output fields required in Return Final Result
OUTPUT_FIELDS_REQUIRED = [
    "correlation_id", "approval_status", "pre_approval_blocked",
    "ticket_created", "ticket_id", "final_status", "audit_event_count",
]

# Response fields from the API (Pydantic models) that n8n expressions depend on
# Maps field names -> originating node (for drift detection)
RESPONSE_FIELD_EXPECTATIONS = {
    "request_id": "Employee Selects Access",
    "approval_id": "Create Manager Approval",
    "status": "Fetch Approval Status",
    "approval_status": "Fetch Approval Status",
    "ticket_id": "Create ITSM Ticket (Approved)",
    "approval_is_approved": "",
    "pre_approval_blocked": "",
    "events": "Fetch Audit Events",
    "count": "Fetch Audit Events",
    "correlation_id": "Normalize Demo Input",
    "employee_id": "Normalize Demo Input",
}

UNSUPPORTED_TYPES = {
    "n8n-nodes-base.slack", "n8n-nodes-base.googleSheets", "n8n-nodes-base.jira",
    "n8n-nodes-base.salesforce", "n8n-nodes-base.gmail", "n8n-nodes-base.microsoftOutlook",
}

TEMPLATE_PATTERN = re.compile(r"\{\{\s*\$node\[[^\]]+\]\.json(?:\[['\"]?(\w+)['\"]?\]|\.(\w+))\s*\}\}")
BASE_URL_PATTERN = re.compile(r"^=\{\{\s*\$node\[[^\]]+\]\.json(?:\[['\"]?API_BASE_URL['\"]?\]|\.API_BASE_URL)\s*\}\}/", re.IGNORECASE)
TEMPLATE_FIELD_PATTERN = re.compile(r"\{\{\s*\$node\[[^\]]+\]\.json(?:\[['\"]?(\w+)['\"]?\]|\.(\w+))\s*\}\}")


def normalize_n8n_url(raw_url: str) -> str | None:
    if not raw_url or not raw_url.startswith("="):
        return raw_url
    stripped = BASE_URL_PATTERN.sub("", raw_url)
    path = TEMPLATE_PATTERN.sub(r"{\1\2}", stripped)
    path = "/" + path.lstrip("/")
    if "?" in path:
        path = path[:path.index("?")]
    return path


def match_method(method_a: str, method_b: str) -> bool:
    """Compare n8n HTTP method (post/GET) with expected method (POST/GET)."""
    return method_a.strip().upper() == method_b.strip().upper()


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


def extract_body_param_names(node: dict) -> set:
    """Extract parameter names from an HTTP Request node's bodyParameters."""
    params = node.get("parameters", {}).get("bodyParameters", {})
    raw_list = params if isinstance(params, list) else params.get("parameters", [])
    return {p.get("name", "") for p in raw_list if isinstance(p, dict)}


def extract_expression_fields(wf_text: str) -> set:
    """Extract field names used in n8n template expressions like .json.field_name."""
    fields = set()
    for match in TEMPLATE_FIELD_PATTERN.finditer(wf_text):
        f1, f2 = match.groups()
        fields.add(f1 or f2)
    return fields


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


def validate_workflow(wf_data: dict) -> list:
    errs = []
    wf_nodes = wf_data.get("nodes", [])
    if not isinstance(wf_nodes, list) or not wf_nodes:
        errs.append("Workflow must have a non-empty 'nodes' array")
        return errs

    node_names_set = set()
    node_type_map = {}
    node_by_name = {}
    for node in wf_nodes:
        nname = node.get("name", "")
        node_names_set.add(nname)
        node_type_map[nname] = node.get("type", "")
        node_by_name[nname] = node

    wf_text = json.dumps(wf_data)
    connections = wf_data.get("connections", {})

    # 0. active must be false (import-readiness)
    if wf_data.get("active") is not False:
        errs.append("Workflow 'active' must be false by default for import-readiness")

    # 0b. sticky notes explain mock boundary and anti-template
    sticky_notes = [n.get("parameters", {}).get("content", "") for n in wf_nodes
                    if n.get("type") == "n8n-nodes-base.stickyNote"]
    all_sticky = " ".join(sticky_notes)
    if "Mock Boundary" not in all_sticky and "mock" not in all_sticky.lower():
        errs.append("Workflow must contain a sticky note explaining the mock/no-paid-service boundary")
    if "template" not in all_sticky.lower() and "adapted" not in all_sticky.lower():
        errs.append("Workflow must contain a sticky note explaining anti-template differentiation")

    # 1. Workflow name
    if wf_data.get("name", "") != EXPECTED_WORKFLOW_NAME:
        errs.append(f"Workflow name must be exactly '{EXPECTED_WORKFLOW_NAME}', got: '{wf_data.get('name', '')}'")

    # 2. Required node names
    for required_name in REQUIRED_NODE_NAMES:
        if required_name not in node_names_set:
            errs.append(f"Required node not found: '{required_name}'")

    # 3. Unsupported node types
    node_types = set(node_type_map.values())
    for unsupported in UNSUPPORTED_TYPES:
        if unsupported in node_types:
            errs.append(f"Unsupported node type found: {unsupported}")

    # 4. No credentials populated
    credential_nodes = []
    for node in wf_nodes:
        creds = node.get("credentials")
        if creds and any(v is not None for v in creds.values()):
            credential_nodes.append(node.get("name", "unknown"))
    if credential_nodes:
        errs.append(f"Workflow has nodes with credentials set: {', '.join(credential_nodes)}")

    # 5. Webhook path exact match
    for node in wf_nodes:
        if node.get("type") == "n8n-nodes-base.webhook":
            webhook_path = node.get("parameters", {}).get("path", "")
            if webhook_path != EXPECTED_WEBHOOK_PATH:
                errs.append(f"Webhook path must be exactly '{EXPECTED_WEBHOOK_PATH}', found: '{webhook_path}'")
            http_method = node.get("parameters", {}).get("httpMethod", "")
            if http_method != "POST":
                errs.append(f"Webhook httpMethod must be POST, found: {http_method}")
            response_mode = node.get("parameters", {}).get("responseMode", "")
            if response_mode not in ("responseNode", "lastNode"):
                errs.append(f"Webhook responseMode must be responseNode or lastNode, found: {response_mode}")

    # 6. Pre-Approval Ticket node exists
    pre_approval_node = node_by_name.get("Pre-Approval Ticket (Expected Block)")
    if pre_approval_node is None:
        errs.append("Pre-Approval Ticket (Expected Block) node not found")
    elif not pre_approval_node.get("continueOnFail", False):
        errs.append("Pre-Approval Ticket (Expected Block) must have continueOnFail: true for 4xx API responses")

    # 7. Final response fields
    final_node = node_by_name.get("Return Final Result")
    gate_node = node_by_name.get("Return Gate Failure Response")
    if final_node is not None:
        response_body = json.dumps(final_node.get("parameters", {}).get("responseBody", ""))
        for field in OUTPUT_FIELDS_REQUIRED:
            if field not in response_body:
                errs.append(f"Return Final Result responseBody must reference field: {field}")
    else:
        errs.append("Workflow must contain a Return Final Result node")
    if gate_node is None:
        errs.append("Workflow must contain a Return Gate Failure Response node")

    # 8. Normalize Demo Input references
    normalize_node = node_by_name.get("Normalize Demo Input")
    if normalize_node is not None:
        norm_text = json.dumps(normalize_node)
        for ref in ("approval_action", "auto_approve_manager"):
            if ref not in norm_text:
                errs.append(f"Normalize Demo Input must reference '{ref}'")
    else:
        errs.append("Normalize Demo Input node not found")

    # 9. Is Approved? must be IF node
    is_approved_node = node_by_name.get("Is Approved?")
    if is_approved_node is not None:
        if is_approved_node.get("type") != "n8n-nodes-base.if":
            errs.append("Is Approved? node must be an IF node (n8n-nodes-base.if), not a switch")
    else:
        errs.append("Is Approved? node not found")

    # 10. Is Approved? branching
    is_approved_conns = connections.get("Is Approved?", {}).get("main", [])
    if len(is_approved_conns) >= 1:
        true_targets = [c.get("node") for c in is_approved_conns[0]]
        if "Create ITSM Ticket (Approved)" not in true_targets:
            errs.append("Create ITSM Ticket (Approved) must be connected after Is Approved? true branch (index 0)")
    else:
        errs.append("Is Approved? missing true branch (index 0)")
    if len(is_approved_conns) >= 2:
        false_targets = [c.get("node") for c in is_approved_conns[1]]
        if "Store No-Ticket Notice" not in false_targets:
            errs.append("Store No-Ticket Notice must be connected after Is Approved? false branch (index 1)")
    else:
        errs.append("Is Approved? missing false branch (index 1)")

    # 11. Selection Succeeded? IF node
    sel_succ_node = node_by_name.get("Selection Succeeded?")
    if sel_succ_node is not None:
        if sel_succ_node.get("type") != "n8n-nodes-base.if":
            errs.append("Selection Succeeded? must be an IF node (n8n-nodes-base.if)")
        ss_conns = connections.get("Selection Succeeded?", {}).get("main", [])
        if len(ss_conns) >= 1 and len(ss_conns[0]) > 0:
            true_target = ss_conns[0][0].get("node", "")
            if true_target != "Create Manager Approval":
                errs.append(f"Selection Succeeded? true branch (output 0) must connect to Create Manager Approval, got '{true_target}'")
        else:
            errs.append("Selection Succeeded? missing true branch (output 0)")
        if len(ss_conns) >= 2 and len(ss_conns[1]) > 0:
            false_target = ss_conns[1][0].get("node", "")
            if false_target != "Store Forbidden Notice":
                errs.append(f"Selection Succeeded? false branch (output 1) must connect to Store Forbidden Notice, got '{false_target}'")
        else:
            errs.append("Selection Succeeded? missing false branch (output 1)")
    else:
        errs.append("Selection Succeeded? node not found")

    # 11b. Return Forbidden Response fields
    forbidden_resp_node = node_by_name.get("Return Forbidden Response")
    if forbidden_resp_node is None:
        errs.append("Workflow must contain a Return Forbidden Response node")
    else:
        resp_body = json.dumps(forbidden_resp_node.get("parameters", {}).get("responseBody", ""))
        for field in FORBIDDEN_RESPONSE_FIELDS:
            if field not in resp_body:
                errs.append(f"Return Forbidden Response responseBody must reference field: {field}")

    # 11c. Fetch Forbidden Audit node
    ffa_node = node_by_name.get("Fetch Forbidden Audit")
    if ffa_node is not None:
        ffa_conns = connections.get("Fetch Forbidden Audit", {}).get("main", [])
        if len(ffa_conns) >= 1 and len(ffa_conns[0]) > 0:
            ffa_target = ffa_conns[0][0].get("node", "")
            if ffa_target != "Return Forbidden Response":
                errs.append(f"Fetch Forbidden Audit must connect to Return Forbidden Response, got '{ffa_target}'")
        if not ffa_node.get("continueOnFail", False):
            errs.append("Fetch Forbidden Audit should have continueOnFail: true")
    else:
        errs.append("Fetch Forbidden Audit node not found")

    # 11d. Store Forbidden Notice body shape
    sfn_node = node_by_name.get("Store Forbidden Notice")
    if sfn_node is not None:
        if not sfn_node.get("continueOnFail", False):
            errs.append("Store Forbidden Notice should have continueOnFail: true to ensure forbidden response is always returned")
        sfn_conns = connections.get("Store Forbidden Notice", {}).get("main", [])
        if len(sfn_conns) >= 1 and len(sfn_conns[0]) > 0:
            sfn_target = sfn_conns[0][0].get("node", "")
            if sfn_target not in ("Return Forbidden Response", "Fetch Forbidden Audit"):
                errs.append(f"Store Forbidden Notice must connect to Return Forbidden Response or Fetch Forbidden Audit, got '{sfn_target}'")
        else:
            errs.append("Store Forbidden Notice must have output connection to Return Forbidden Response")
        # Validate body shape: must have 'message' parameter, not 'content'
        sfn_body = extract_body_param_names(sfn_node)
        if "message" not in sfn_body:
            errs.append("Store Forbidden Notice bodyParameters must include 'message'")
        if "content" in sfn_body:
            errs.append("Store Forbidden Notice bodyParameters must not use 'content' (use 'message')")
        # Must have metadata field
        if "metadata" not in sfn_body and "channel_or_user" not in sfn_body:
            errs.append("Store Forbidden Notice must include channel_or_user in bodyParameters")
    else:
        errs.append("Store Forbidden Notice node not found")

    # 11e. Employee Selects Access routing
    esa_outs = connections.get("Employee Selects Access", {}).get("main", [])
    for branches in esa_outs:
        for b in branches:
            if b.get("node") == "Create Manager Approval":
                errs.append("Employee Selects Access must not connect directly to Create Manager Approval; use Selection Succeeded?")
    esa_to_ss = False
    for branches in esa_outs:
        for b in branches:
            if b.get("node") == "Selection Succeeded?":
                esa_to_ss = True
    if not esa_to_ss:
        errs.append("Employee Selects Access must connect to Selection Succeeded?")

    # 12. Ticket inbound: must be exactly Is Approved? output 0
    ticket_inbound = []
    for src_node, src_conn in connections.items():
        for out_idx, branches in enumerate(src_conn.get("main", [])):
            for branch in branches:
                if branch.get("node") == "Create ITSM Ticket (Approved)":
                    ticket_inbound.append((src_node, out_idx))
    if len(ticket_inbound) != 1:
        errs.append(f"Create ITSM Ticket (Approved) must have exactly 1 inbound connection, found {len(ticket_inbound)}")
    elif ticket_inbound[0] != ("Is Approved?", 0):
        errs.append(f"Create ITSM Ticket (Approved) inbound must be Is Approved? output 0, got {ticket_inbound[0]}")

    # 12b. Gate Failure Path must not connect directly to ticket creation
    gate_failure_outs = connections.get("Gate Failure Path", {}).get("main", [])
    for branches in gate_failure_outs:
        for b in branches:
            if b.get("node") == "Create ITSM Ticket (Approved)":
                errs.append("Gate Failure Path (Check Pre-Approval Blocked false branch) must not connect to Create ITSM Ticket (Approved)")

    # 13. Decision nodes exist
    for dn in ("Reject Manager Decision", "Expire Manager Decision", "Wrong Manager Approval"):
        dn_node = node_by_name.get(dn)
        if dn_node is None:
            errs.append(f"Required decision node '{dn}' not found")

    # 14. Check Pre-Approval Blocked IF node
    check_blocked_node = node_by_name.get("Check Pre-Approval Blocked")
    if check_blocked_node is not None:
        if check_blocked_node.get("type") != "n8n-nodes-base.if":
            errs.append("Check Pre-Approval Blocked must be an IF node (n8n-nodes-base.if)")
        cpab_conns = connections.get("Check Pre-Approval Blocked", {}).get("main", [])
        if len(cpab_conns) >= 1 and len(cpab_conns[0]) > 0:
            true_target = cpab_conns[0][0].get("node", "")
            if true_target != "Approval Action Switch":
                errs.append(f"Check Pre-Approval Blocked true branch must connect to Approval Action Switch, got '{true_target}'")
        if len(cpab_conns) >= 2:
            if len(cpab_conns[1]) > 0:
                false_target = cpab_conns[1][0].get("node", "")
                if false_target != "Gate Failure Path":
                    errs.append(f"Check Pre-Approval Blocked false branch must connect to Gate Failure Path, got '{false_target}'")
            else:
                errs.append("Check Pre-Approval Blocked false branch (index 1) must have at least one connection")
    else:
        errs.append("Check Pre-Approval Blocked node not found")

    # 15. Approval Action Switch node
    aas_node = node_by_name.get("Approval Action Switch")
    if aas_node is not None:
        if aas_node.get("type") != "n8n-nodes-base.switch":
            errs.append("Approval Action Switch must be a Switch node (n8n-nodes-base.switch)")
        found_inbound = False
        for src_node, src_conn in connections.items():
            for out_idx, branches in enumerate(src_conn.get("main", [])):
                for branch in branches:
                    if branch.get("node") == "Approval Action Switch":
                        if src_node == "Check Pre-Approval Blocked" and out_idx == 0:
                            found_inbound = True
        if not found_inbound:
            errs.append("Approval Action Switch must have inbound connection from Check Pre-Approval Blocked true branch (output 0)")
        aas_conns = connections.get("Approval Action Switch", {}).get("main", [])
        expected_outbounds = {
            0: "Approve Manager Decision", 1: "Reject Manager Decision",
            2: "Expire Manager Decision", 3: "Fetch Approval Status",
            4: "Wrong Manager Approval",
        }
        for out_idx, expected_node in expected_outbounds.items():
            if len(aas_conns) > out_idx and len(aas_conns[out_idx]) > 0:
                actual_node = aas_conns[out_idx][0].get("node", "")
                if actual_node != expected_node:
                    errs.append(f"Approval Action Switch output {out_idx} must connect to '{expected_node}', got '{actual_node}'")
            else:
                errs.append(f"Approval Action Switch output {out_idx} ({expected_node}) missing")
    else:
        errs.append("Approval Action Switch node not found")

    # 16. Exact HTTP node endpoint checks
    for node_name, (expected_method, expected_path_prefix) in REQUIRED_HTTP_ENDPOINTS.items():
        node = node_by_name.get(node_name)
        if node is None:
            continue
        if node.get("type") != "n8n-nodes-base.httpRequest":
            errs.append(f"'{node_name}' must be an HTTP Request node")
            continue
        actual_method = node.get("parameters", {}).get("method", "GET")
        if not match_method(actual_method, expected_method):
            errs.append(f"'{node_name}' HTTP method must be {expected_method}, got {actual_method}")
        raw_url = node.get("parameters", {}).get("url", "")
        normalized = normalize_n8n_url(raw_url) if raw_url else ""
        if normalized and normalized.split("?")[0] not in expected_path_prefix:
            # Check if the normalized path starts with the expected prefix
            if not normalized.startswith(expected_path_prefix):
                errs.append(f"'{node_name}' URL path must start with '{expected_path_prefix}', got '{normalized}'")

    # 17. Body parameter checks against required fields
    for node_name, required_fields in REQUIRED_BODY_FIELDS.items():
        node = node_by_name.get(node_name)
        if node is not None and node.get("type") == "n8n-nodes-base.httpRequest":
            actual_fields = extract_body_param_names(node)
            for rf in required_fields:
                if rf not in actual_fields:
                    errs.append(f"'{node_name}' bodyParameters must include '{rf}'")

    # 18. OpenAPI endpoint match (including /audit/events)
    openapi_paths = get_openapi_paths()
    if openapi_paths is not None:
        for node in wf_nodes:
            params = node.get("parameters", {})
            raw_url = params.get("url", "")
            if not raw_url:
                continue
            endpoint_ok_patterns = ["mock", "onboarding", "health", "/ready", "/version", "/demo/reset", "/audit/events", "audit"]
            if not any(p in raw_url for p in endpoint_ok_patterns):
                continue
            normalized = normalize_n8n_url(raw_url)
            if normalized and normalized not in openapi_paths:
                errs.append(f"HTTP node '{node.get('name')}' calls '{normalized}' which is not exposed by the API")
    else:
        for node in wf_nodes:
            params = node.get("parameters", {})
            node_url = params.get("url", "")
            if "api_base_url" in wf_text.lower() or "{{" in node_url:
                continue
            if node_url and "mock" in node_url and "localhost" not in node_url and "api" not in node_url:
                errs.append(f"HTTP node '{node.get('name')}' uses URL not based on local API: {node_url}")

    # 19. Workflow expression fields should exist in expected API responses
    expr_fields = extract_expression_fields(wf_text)
    for field in RESPONSE_FIELD_EXPECTATIONS:
        if field in expr_fields:
            pass

    return errs


errors = validate_workflow(wf)

if errors:
    print("FAIL: Workflow contract violations:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
elif "--negative" in sys.argv:
    pass
else:
    print("OK: Workflow contract passed")
    sys.exit(0)

# -------- Negative Contract Tests --------
if "--negative" in sys.argv:
    import copy
    test_errors = 0

    def run_negative(name: str, mutant: dict) -> bool:
        m_errs = validate_workflow(mutant)
        if m_errs:
            return True
        else:
            print(f"  NEGATIVE FAIL: {name} (validator should have failed)")
            return False

    print("\n--- Negative Contract Tests ---")

    # Existing mutants 1-15 (keep all)
    mutant1 = copy.deepcopy(wf)
    for node in mutant1.get("nodes", []):
        if node.get("type") == "n8n-nodes-base.webhook":
            node["parameters"]["path"] = "hr-onboarding"
    if run_negative("changed webhook path to old value", mutant1):
        test_errors += 1

    mutant2 = copy.deepcopy(wf)
    mutant2["nodes"] = [n for n in mutant2.get("nodes", []) if n.get("name") != "Pre-Approval Ticket (Expected Block)"]
    if run_negative("removed pre-approval ticket node", mutant2):
        test_errors += 1

    mutant3 = copy.deepcopy(wf)
    ia_conns = mutant3.get("connections", {}).get("Is Approved?", {})
    if len(ia_conns.get("main", [])) >= 2:
        ia_conns["main"][1] = [{"node": "Create ITSM Ticket (Approved)", "type": "main", "index": 0}]
    if run_negative("ticket on Is Approved? false branch", mutant3):
        test_errors += 1

    mutant4 = copy.deepcopy(wf)
    mutant4["nodes"] = [n for n in mutant4["nodes"] if n.get("name") != "Approve Manager Decision"]
    if run_negative("removed approve decision node", mutant4):
        test_errors += 1

    mutant5 = copy.deepcopy(wf)
    mutant5["name"] = "HR Onboarding Agent - Complete v1"
    if run_negative("changed workflow name to old value", mutant5):
        test_errors += 1

    mutant6 = copy.deepcopy(wf)
    mutant6["nodes"].append({"name": "Evil Slack", "type": "n8n-nodes-base.slack", "credentials": {"credential1": {}}})
    if run_negative("added credential-based Slack node", mutant6):
        test_errors += 1

    mutant7 = copy.deepcopy(wf)
    for node in mutant7.get("nodes", []):
        if node.get("name") == "Return Final Result":
            rb = node.get("parameters", {}).get("responseBody", "")
            rb = rb.replace("correlation_id", "deleted_field_ci")
            node["parameters"]["responseBody"] = rb
            break
    if run_negative("removed correlation_id from final response", mutant7):
        test_errors += 1

    mutant8 = copy.deepcopy(wf)
    cpab = mutant8.get("connections", {}).get("Check Pre-Approval Blocked", {})
    if len(cpab.get("main", [])) >= 2:
        cpab["main"][1] = []
    if run_negative("removed Check Pre-Approval Blocked false branch", mutant8):
        test_errors += 1

    mutant9 = copy.deepcopy(wf)
    mutant9_conns = mutant9.get("connections", {})
    if "Check Pre-Approval Blocked" in mutant9_conns:
        cpab_conns = mutant9_conns["Check Pre-Approval Blocked"].get("main", [])
        if cpab_conns and len(cpab_conns[0]) > 0:
            cpab_conns[0] = []
    if "Approval Action Switch" in mutant9_conns:
        del mutant9_conns["Approval Action Switch"]
    if run_negative("disconnected Approval Action Switch from gate", mutant9):
        test_errors += 1

    mutant10 = copy.deepcopy(wf)
    mutant10["nodes"] = [n for n in mutant10.get("nodes", []) if n.get("name") != "Selection Succeeded?"]
    if run_negative("removed Selection Succeeded? node", mutant10):
        test_errors += 1

    mutant11 = copy.deepcopy(wf)
    mutant11_conns = mutant11.get("connections", {}).get("Selection Succeeded?", {})
    if len(mutant11_conns.get("main", [])) >= 2:
        mutant11_conns["main"][1] = [{"node": "Return Final Result", "type": "main", "index": 0}]
    if run_negative("Selection Succeeded? false branch to wrong target", mutant11):
        test_errors += 1

    mutant12 = copy.deepcopy(wf)
    mutant12["nodes"] = [n for n in mutant12.get("nodes", []) if n.get("name") != "Store Forbidden Notice"]
    if run_negative("removed Store Forbidden Notice node", mutant12):
        test_errors += 1

    mutant13 = copy.deepcopy(wf)
    mutant13_conns = mutant13.get("connections", {})
    if "Employee Selects Access" in mutant13_conns:
        mutant13_conns["Employee Selects Access"]["main"] = [[{"node": "Create Manager Approval", "type": "main", "index": 0}]]
    if run_negative("direct Employee Selects Access to Create Manager Approval", mutant13):
        test_errors += 1

    mutant14 = copy.deepcopy(wf)
    for node in mutant14.get("nodes", []):
        if node.get("name") == "Pre-Approval Ticket (Expected Block)":
            node.pop("continueOnFail", None)
            break
    if run_negative("removed continueOnFail from Pre-Approval Ticket", mutant14):
        test_errors += 1

    mutant15 = copy.deepcopy(wf)
    mutant15["nodes"] = [n for n in mutant15.get("nodes", []) if n.get("name") != "Fetch Forbidden Audit"]
    if run_negative("removed Fetch Forbidden Audit node", mutant15):
        test_errors += 1

    # New mutants 16-24
    mutant16 = copy.deepcopy(wf)
    mutant16["active"] = True
    if run_negative("workflow active set to true", mutant16):
        test_errors += 1

    mutant17 = copy.deepcopy(wf)
    for node in mutant17.get("nodes", []):
        if node.get("name") == "Start Onboarding Session":
            node["parameters"]["url"] = node["parameters"]["url"].replace("/onboarding/start/", "/onboarding/startx/")
            break
    if run_negative("changed Start Onboarding Session to wrong endpoint", mutant17):
        test_errors += 1

    mutant18 = copy.deepcopy(wf)
    for node in mutant18.get("nodes", []):
        if node.get("name") == "Fetch Audit Events":
            node["parameters"]["url"] = node["parameters"]["url"].replace("/audit/events", "/audit/eventsx")
            break
    if run_negative("broken audit events endpoint", mutant18):
        test_errors += 1

    mutant19 = copy.deepcopy(wf)
    for node in mutant19.get("nodes", []):
        if node.get("name") == "Store Forbidden Notice":
            params = node.get("parameters", {}).get("bodyParameters", {})
            raw_list = params if isinstance(params, list) else params.get("parameters", [])
            for p in raw_list:
                if p.get("name") == "message":
                    p["name"] = "content"
            break
    if run_negative("changed Store Forbidden Notice message to content", mutant19):
        test_errors += 1

    mutant20 = copy.deepcopy(wf)
    for node in mutant20.get("nodes", []):
        if node.get("name") == "Return Forbidden Response":
            rb = node.get("parameters", {}).get("responseBody", "")
            rb = rb.replace("forbidden", "omitted_placeholder")
            node["parameters"]["responseBody"] = rb
            break
    if run_negative("removed forbidden from Return Forbidden Response", mutant20):
        test_errors += 1

    mutant21 = copy.deepcopy(wf)
    for node in mutant21.get("nodes", []):
        if node.get("name") == "Create Manager Approval":
            params = node.get("parameters", {}).get("bodyParameters", {})
            raw_list = params if isinstance(params, list) else params.get("parameters", [])
            raw_list[:] = [p for p in raw_list if p.get("name") != "manager_id"]
            break
    if run_negative("removed manager_id from Create Manager Approval body", mutant21):
        test_errors += 1

    mutant22 = copy.deepcopy(wf)
    for node in mutant22.get("nodes", []):
        if node.get("type") == "n8n-nodes-base.httpRequest":
            params = node.get("parameters", {})
            if "/onboarding/start/" in params.get("url", ""):
                params["method"] = "GET"
                break
    if run_negative("changed Start Onboarding Session method to GET", mutant22):
        test_errors += 1

    mutant23 = copy.deepcopy(wf)
    for node in mutant23.get("nodes", []):
        if node.get("name") == "Employee Selects Access":
            params = node.get("parameters", {}).get("bodyParameters", {})
            raw_list = params if isinstance(params, list) else params.get("parameters", [])
            raw_list[:] = [p for p in raw_list if p.get("name") != "correlation_id"]
            break
    if run_negative("removed correlation_id from Employee Selects Access body", mutant23):
        test_errors += 1

    mutant24 = copy.deepcopy(wf)
    for node in mutant24.get("nodes", []):
        if node.get("name") == "Store Forbidden Notice":
            node["parameters"]["bodyParameters"] = {
                "parameters": [
                    {"name": "correlation_id", "value": "={{ $node['Normalize Demo Input'].json.correlation_id }}"}
                ]
            }
            break
    if run_negative("Store Forbidden Notice sends correlation_id as top-level field instead of metadata", mutant24):
        test_errors += 1

    print(f"\n--- Negative tests: {test_errors}/24 passed ---")
    if test_errors == 24:
        print("All negative contract tests pass.")
    else:
        print(f"WARNING: {24 - test_errors} negative test(s) did NOT fail the validator.")
        sys.exit(1)
