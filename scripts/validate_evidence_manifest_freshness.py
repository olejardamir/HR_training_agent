#!/usr/bin/env python3
import json
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "evidence_manifest.json")

EVIDENCE_ONLY_PATHS = [
    "evidence_manifest.json",
    "docs/final_verification_report.md",
    "docs/demo_outputs/",
    "docs/generated_artifacts_policy.md",
]


def git(*args):
    r = subprocess.run(
        ["git"] + list(args),
        cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10
    )
    return r.stdout.strip(), r.stderr.strip()


def main():
    if not os.path.isfile(MANIFEST_PATH):
        print("FAIL: evidence_manifest.json not found")
        sys.exit(1)

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    manifest_commit = manifest.get("verified_commit", "")
    head, _ = git("rev-parse", "HEAD")
    head_parent, _ = git("rev-parse", "HEAD^") if head else (None, None)

    if not manifest_commit:
        print("FAIL: evidence_manifest.json has no verified_commit field")
        sys.exit(1)

    if manifest_commit == head:
        print(f"PASS: evidence_manifest.json references current HEAD ({head[:12]})")
        sys.exit(0)

    if manifest_commit == head_parent:
        diff_files, _ = git("diff", "--name-only", manifest_commit, head)
        changed = [f for f in diff_files.split("\n") if f]

        non_evidence = []
        for f in changed:
            is_evidence = False
            for prefix in EVIDENCE_ONLY_PATHS:
                if f == prefix or f.startswith(prefix):
                    is_evidence = True
                    break
            if not is_evidence:
                non_evidence.append(f)

        if non_evidence:
            print(f"FAIL: evidence_manifest.json references {manifest_commit[:12]} (HEAD^)")
            print(f"      but non-evidence files changed after that commit:")
            for f in non_evidence:
                print(f"        {f}")
            print(f"      Regenerate manifest after verification.")
            sys.exit(1)
        else:
            print(f"PASS: evidence_manifest.json references {manifest_commit[:12]} (HEAD^)")
            print(f"      and only evidence/docs files changed since then.")
            sys.exit(0)

    print(f"FAIL: evidence_manifest.json references {manifest_commit[:12]}")
    print(f"      but HEAD is {head[:12]} (not HEAD or HEAD^)")
    print(f"      Re-run scripts/generate_evidence_manifest.py to refresh.")
    sys.exit(1)


if __name__ == "__main__":
    main()
