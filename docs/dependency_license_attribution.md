# Dependency, License, and Attribution

## Python Dependencies

Listed in `api/requirements.txt`. Key packages:

| Package | License (SPDX) | Purpose |
|---|---|---|
| FastAPI | MIT | API framework |
| SQLAlchemy | MIT | ORM |
| Pydantic | MIT | Schema validation |
| uvicorn | BSD-3-Clause | ASGI server |
| httpx | BSD-3-Clause | HTTP client (Ollama) |
| psycopg2-binary | LGPL-3.0-only | PostgreSQL driver |
| pytest | MIT | Test framework |

## Infrastructure

| Component | License/Status | Note |
|---|---|---|
| n8n (self-hosted) | Sustainable Use License / Fair-code | Not OSI-open-source. This project uses self-hosted n8n for local prototype orchestration only. No n8n Cloud required. |
| PostgreSQL | PostgreSQL License (OSI approved) | Open-source relational database |
| Docker | Apache 2.0 | Container runtime |

## Local Model

The `.env.example` defaults to `LLM_PROVIDER=fallback` (deterministic template text). `LLM_PROVIDER=ollama` and `gemma2:2b` (Gemma license) are **not required** — the demo works without any LLM model. No hosted API keys are needed.

## Template Attribution

This workflow was adapted from a generic employee-provisioning n8n template. All direct credential-based SaaS provisioning nodes have been removed and replaced with local FastAPI mock endpoints. The sticky notes in the workflow explain this differentiation.

## Important Notes

- License status should be verified before production use.
- This project does not claim that n8n is OSI-open-source.
- This project does not require n8n Cloud.
- This project does not require OpenAI, Gemini, or any hosted LLM API key.
