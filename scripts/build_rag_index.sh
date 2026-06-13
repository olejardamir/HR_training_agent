#!/usr/bin/env bash
set -euo pipefail

docker compose exec -T api python -m app.rag.index_builder
