#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Enforce clean worktree: verified_commit must match a clean committed revision
status = subprocess.run(["git", "status", "--short"], cwd=PROJECT_ROOT,
                        capture_output=True, text=True, timeout=10)
if status.stdout.strip():
    print("ERROR: Worktree is dirty — cannot generate evidence manifest for uncommitted changes.")
    print("Commit or stash changes first, then re-run.")
    sys.exit(1)

CHECKS = {
    "docker_compose_config": ["docker", "compose", "config", "-q"],
    "api_health": ["curl", "-fsS", "http://localhost:8000/health"],
    "api_ready": ["curl", "-fsS", "http://localhost:8000/ready"],
    "pytest": ["docker", "compose", "exec", "-T", "api", "pytest", "-q"],
    "n8n_workflow_static_validation": [sys.executable, "scripts/validate_workflow_contract.py"],
    "n8n_workflow_negative_validation": [sys.executable, "scripts/validate_workflow_contract.py", "--negative"],
    "no_collapsed_files": [sys.executable, "scripts/validate_no_collapsed_files.py"],
    "no_secrets": [sys.executable, "scripts/validate_no_secrets.py"],
    "openapi_contract": [sys.executable, "scripts/validate_openapi_contract.py"],
    "happy_path_smoke": ["bash", "scripts/smoke_happy_path.sh"],
    "pending_path_smoke": ["bash", "scripts/smoke_pending_path.sh"],
    "reject_path_smoke": ["bash", "scripts/smoke_reject_path.sh"],
    "forbidden_path_smoke": ["bash", "scripts/smoke_forbidden_path.sh"],
    "llm_fallback_smoke": ["bash", "scripts/smoke_llm_fallback.sh"],
    "n8n_webhook_smoke": ["bash", "scripts/smoke_n8n_happy_path.sh"],
    "n8n_reject_path_smoke": ["bash", "scripts/smoke_n8n_reject_path.sh"],
    "n8n_pending_path_smoke": ["bash", "scripts/smoke_n8n_pending_path.sh"],
    "n8n_expire_path_smoke": ["bash", "scripts/smoke_n8n_expire_path.sh"],
    "n8n_wrong_manager_path_smoke": ["bash", "scripts/smoke_n8n_wrong_manager_path.sh"],
    "n8n_forbidden_path_smoke": ["bash", "scripts/smoke_n8n_forbidden_path.sh"],
}

results = {}
all_pass = True

for name, cmd in CHECKS.items():
    try:
        r = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=180)
        if r.returncode == 0:
            results[name] = "pass"
        else:
            results[name] = "fail"
            all_pass = False
        print(f"  {name}: {results[name]}")
        if r.returncode != 0:
            print(f"    stdout: {r.stdout[:200]}")
            print(f"    stderr: {r.stderr[:200]}")
    except Exception as e:
        results[name] = "error"
        all_pass = False
        print(f"  {name}: error - {e}")

manifest_path = os.path.join(PROJECT_ROOT, "evidence_manifest.json")

if all_pass:
    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verified_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT,
            capture_output=True, text=True, timeout=10
        ).stdout.strip() or "local",
        "checks": results,
        "artifacts": {
            "workflow": "n8n/hr_onboarding_workflow.json",
            "solution_design": "docs/solution_design_1_2_pages.md",
            "demo_walkthrough": "docs/demo_walkthrough.md",
            "traceability": "docs/traceability_matrix.md",
        },
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nAll checks passed. Manifest written to {manifest_path}")
    sys.exit(0)
else:
    print(f"\nSome checks failed. Manifest not written.")
    sys.exit(1)
