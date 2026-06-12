# Standards Alignment

## Framework Alignment (Directional, Not Certified)

| Framework | Relevance | Implementation Status |
|---|---|---|
| NIST AI RMF | Govern, Map, Measure, Manage | Gaps documented in `archive_boundary.md` |
| OWASP LLM Top 10 | LLM01 (Prompt Injection), LLM02 (Insecure Output) | Q&A endpoint blocks forbidden questions; LLM boundary is communication-only |
| ISO/IEC 42001 | AI management system direction | Not implemented; noted as production path |
| SOC 2 | Security, Availability, Confidentiality | Audit trail covers all state changes; no real data stored |
| SCIM / OIDC / SAML | Identity provisioning | Mocked; real integration deferred |
| RBAC / ABAC | Access control model | Role-level policy engine implements RBAC; manager approval adds ABAC-style check |
| ITIL-style ITSM | Ticket lifecycle | ITSM mock covers create, readback, idempotency, blocked states |

## Privacy Principles
- PII allowlist controls audit metadata (see `logic/pii.py`)
- No real employee data in repository
- No secrets or tokens stored

## Production Path
- Replace mock services with real API adapters
- Add OAuth2/OIDC for authentication
- Add formal RBAC/ABAC with real identity provider
- Replace LLM fallback with governed model endpoint
- Add SCIM provisioning for real HRIS/LMS
