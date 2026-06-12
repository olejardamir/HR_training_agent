import json
import os
import subprocess
import sys
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHECKS = {
    "docker_compose_config": ["docker", "compose", "config", "-q"],
    "api_health": ["curl", "-fsS", "http://localhost:8000/health"],
    "api_ready": ["curl", "-fsS", "http://localhost:8000/ready"],
    "pytest": ["docker", "compose", "exec", "api", "pytest", "-q"],
    "n8n_workflow_static_validation": [sys.executable, "scripts/validate_workflow_contract.py"],
    "no_collapsed_files": [sys.executable, "scripts/validate_no_collapsed_files.py"],
    "no_secrets": [sys.executable, "scripts/validate_no_secrets.py"],
    "happy_path_smoke": ["bash", "scripts/smoke_happy_path.sh"],
    "pending_path_smoke": ["bash", "scripts/smoke_pending_path.sh"],
    "reject_path_smoke": ["bash", "scripts/smoke_reject_path.sh"],
    "forbidden_path_smoke": ["bash", "scripts/smoke_forbidden_path.sh"],
    "llm_fallback_smoke": ["bash", "scripts/smoke_llm_fallback.sh"],
}

results = {}
all_pass = True

for name, cmd in CHECKS.items():
    try:
        r = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60)
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
        "repo_commit": "local",
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
