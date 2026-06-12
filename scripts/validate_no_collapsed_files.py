#!/usr/bin/env python3
import json
import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "postgres_data", "node_modules", "1_PREPARATION_STEP"}
EXCLUDE_EXTENSIONS = {".pyc", ".pyo", ".db", ".sqlite3"}
ALLOWED_SINGLE_LINE_FILES = {".gitignore", "Dockerfile", "__init__.py"}
EXCLUDE_PATHS = {"n8n/all_wfs.json", "n8n/exported.json"}

errors = []

PY_MULTI_STMT_THRESHOLD = 5
PY_STMT_PATTERNS = [r'^def ', r'^class ', r'^import ', r'^from ']


def _check_file(fp, rel, ext, fname):
    try:
        with open(fp, "r") as fh:
            content = fh.read()
    except Exception:
        return

    lines = content.split("\n")

    if len(lines) <= 1:
        if ext == ".json":
            try:
                json.loads(content)
                return
            except json.JSONDecodeError:
                pass
        errors.append(f"{rel}: {len(lines)} line(s), expected > 1")
        return

    if ext == ".py" and len(lines) < PY_MULTI_STMT_THRESHOLD:
        stmt_count = 0
        for line in lines:
            stripped = line.strip()
            if any(re.match(p, stripped) for p in PY_STMT_PATTERNS):
                stmt_count += 1
        if stmt_count >= 2:
            errors.append(f"{rel}: {len(lines)} lines but {stmt_count} def/class/import statements")

    if ext in (".yml", ".yaml") and len(lines) < 3:
        key_count = content.count(":")
        if key_count >= 3:
            errors.append(f"{rel}: {len(lines)} lines but {key_count} YAML keys")

    if fname == ".env.example" and len(lines) < 2:
        assign_count = content.count("=")
        if assign_count >= 2:
            errors.append(f"{rel}: {len(lines)} lines but {assign_count} env assignments")

    if fname == "requirements.txt" and len(lines) < 2:
        pkg_count = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
        if pkg_count >= 2:
            errors.append(f"{rel}: {len(lines)} lines but {pkg_count} packages")

    if ext == ".json":
        try:
            json.loads(content)
        except json.JSONDecodeError:
            errors.append(f"{rel}: invalid JSON")


for root, dirs, files in os.walk(PROJECT_ROOT):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, PROJECT_ROOT)

        ext = os.path.splitext(f)[1]
        if ext in EXCLUDE_EXTENSIONS:
            continue
        if f in ALLOWED_SINGLE_LINE_FILES:
            continue
        if rel in EXCLUDE_PATHS:
            continue
        _check_file(fp, rel, ext, f)

if errors:
    print("FAIL: Collapsed files found:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("OK: No collapsed files found")
    sys.exit(0)
