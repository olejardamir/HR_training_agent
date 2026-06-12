import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "postgres_data", "node_modules", "1_PREPARATION_STEP", "screenshots", "private"}
EXCLUDE_FILES = {"validate_no_secrets.py", ".env.example", ".env"}

SECRET_PATTERNS = [
    (re.compile(r'(?i)(api[_-]?key\s*=\s*["\']?[a-zA-Z0-9_\-]{16,})', re.IGNORECASE), "API key"),
    (re.compile(r'(?i)(secret\s*=\s*["\']?[a-zA-Z0-9_\-]{16,})', re.IGNORECASE), "Secret"),
    (re.compile(r'(?i)(password\s*=\s*["\']?[a-zA-Z0-9_\-]{8,})', re.IGNORECASE), "Password"),
    (re.compile(r'(?i)(token\s*=\s*["\']?[a-zA-Z0-9_\-]{16,})', re.IGNORECASE), "Token"),
    (re.compile(r'(?i)(sk-[a-zA-Z0-9_\-]{20,})'), "OpenAI-style key"),
]

errors = []

for root, dirs, files in os.walk(PROJECT_ROOT):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, PROJECT_ROOT)

        if f in EXCLUDE_FILES:
            continue

        try:
            with open(fp, "r", errors="ignore") as fh:
                content = fh.read()
        except Exception:
            continue

        for pattern, name in SECRET_PATTERNS:
            matches = pattern.findall(content)
            if matches:
                errors.append(f"{rel}: possible {name} found")

if errors:
    print("FAIL: Secrets found:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("OK: No secrets detected")
    sys.exit(0)
