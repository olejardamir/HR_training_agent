#!/usr/bin/env python3
"""Validate that the running OpenAPI export contains all required endpoints."""

import json
import os
import sys
import urllib.request

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")

REQUIRED_ENDPOINTS = [
    ("GET", "/health"),
    ("GET", "/ready"),
    ("GET", "/version"),
    ("POST", "/demo/reset"),
    ("POST", "/onboarding/start/{employee_id}"),
    ("GET", "/onboarding/status/{employee_id}"),
    ("POST", "/onboarding/select-access"),
    ("POST", "/onboarding/questions"),
    ("GET", "/mock/hr/employees/{employee_id}"),
    ("PATCH", "/mock/hr/employees/{employee_id}/profile"),
    ("GET", "/mock/training/status/{employee_id}"),
    ("PATCH", "/mock/training/status/{employee_id}/modules/{module_id}"),
    ("GET", "/mock/access/recommendations/{employee_id}"),
    ("POST", "/mock/llm/messages"),
    ("POST", "/mock/slack/messages"),
    ("POST", "/mock/approvals"),
    ("GET", "/mock/approvals/{approval_id}"),
    ("POST", "/mock/approvals/{approval_id}/approve"),
    ("POST", "/mock/approvals/{approval_id}/reject"),
    ("POST", "/mock/approvals/{approval_id}/expire"),
    ("POST", "/mock/itsm/tickets"),
    ("GET", "/mock/itsm/tickets/{ticket_id}"),
    ("GET", "/audit/events"),
    ("GET", "/mock/salesforce/profile/{employee_id}"),
    ("PATCH", "/mock/salesforce/profile/{employee_id}"),
]

errors = []

try:
    req = urllib.request.Request(f"{API_BASE}/openapi.json")
    resp = urllib.request.urlopen(req, timeout=10)
    spec = json.loads(resp.read())
except Exception as e:
    print(f"ERROR: Cannot fetch OpenAPI from {API_BASE}/openapi.json: {e}")
    sys.exit(1)

paths = spec.get("paths", {})

for method, path in REQUIRED_ENDPOINTS:
    method_lower = method.lower()
    if path not in paths:
        errors.append(f"Missing path: {path}")
        continue
    if method_lower not in paths[path]:
        errors.append(f"Missing method {method} for {path}")

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
else:
    print(f"OpenAPI contract validation passed ({len(REQUIRED_ENDPOINTS)} endpoints)")
    sys.exit(0)
