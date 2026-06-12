# Environment Matrix

## Tested Environment

| Component | Value |
|---|---|
| Tested OS | Linux (Ubuntu 22.04 / kernel 6.x) |
| Docker version | 24+ |
| Docker Compose version | 2.x (v2 plugin) |
| Python (api container) | 3.11.15 |
| PostgreSQL image | postgres:15 |
| n8n image | n8nio/n8n:1.121.0 |
| FastAPI | 0.115.x |
| SQLAlchemy | 2.0.x |
| Pydantic | 2.x |
| pytest | 8.4.2 |
| Known working browser | Chromium-based (for n8n UI if manual import needed) |

## Not Tested

- Windows / macOS native (Docker Desktop should work but not verified)
- Podman
- Native Python (outside Docker)
- n8n versions other than 1.121.0
- PostgreSQL versions other than 15

## Dependency Capture

Generated from the verified commit. See `docs/demo_outputs/pip_freeze.txt` for full Python dependency list.
