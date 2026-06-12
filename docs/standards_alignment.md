# Standards & Frameworks Alignment

This prototype aligns with the following external standards and frameworks **as design references**, not as certifications.

## AI Governance

- **NIST AI Risk Management Framework (AI RMF)** – Govern, map, measure, manage risks around AI‑assisted decisions. Our agent bounds LLM usage to communication, keeping high‑risk decisions deterministic and auditable.
- **ISO/IEC 42001:2023** – Provides direction for AI management systems. We apply structured governance: human oversight (manager approval), risk ownership (policy engine), and continuous improvement (audit trail).

## LLM Security

- **OWASP Top 10 for LLM Applications** – We mitigate prompt injection by treating all user input as untrusted; the LLM cannot change workflow state, approval status, or policy. Sensitive data is minimized in prompts.

## Enterprise Controls

- **SOC 2 Trust Services Criteria** – The prototype demonstrates security (access control, approval gate), processing integrity (idempotent tickets), and auditability (correlation ID + event log).
- **SCIM 2.0** – Production path for user provisioning; mocked in prototype.
- **OAuth 2.0 / OpenID Connect / SAML 2.0** – Identity and authorization framework for production.
- **RBAC / ABAC** – Role‑level access policy with attributes (role, level, department).

## Privacy

- **GDPR‑style principles** – Data minimization (only necessary employee fields), purpose limitation (onboarding only), auditability, and no unnecessary PII in logs or prompts.

## Service Management

- **ITIL‑style ITSM** – Access request → manager approval → ticket creation workflow aligns with ITIL change/request management.

## How We Use These Standards

We reference them to show awareness of enterprise expectations. The prototype does **not** claim compliance; it is designed to be extended to meet those standards in production.
