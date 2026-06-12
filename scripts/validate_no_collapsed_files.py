import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "postgres_data", "node_modules", "1_PREPARATION_STEP"}
EXCLUDE_EXTENSIONS = {".pyc", ".pyo", ".db", ".sqlite3"}
ALLOWED_SINGLE_LINE_FILES = {".gitignore", ".env", ".env.example", "Dockerfile", "__init__.py"}

SKIP_EXTENSIONS_SINGLE_LINE_CHECK = {".key", ".pem", ".pub", ".cert"}

errors = []

for root, dirs, files in os.walk(PROJECT_ROOT):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, PROJECT_ROOT)

        ext = os.path.splitext(f)[1]
        if ext in EXCLUDE_EXTENSIONS or ext in SKIP_EXTENSIONS_SINGLE_LINE_CHECK:
            continue
        if f in ALLOWED_SINGLE_LINE_FILES:
            continue

        try:
            with open(fp, "r") as fh:
                lines = fh.readlines()
        except Exception:
            continue

        if len(lines) <= 1:
            errors.append(f"{rel}: {len(lines)} lines, expected > 1")

if errors:
    print("FAIL: Collapsed files found:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("OK: No collapsed files found")
    sys.exit(0)
