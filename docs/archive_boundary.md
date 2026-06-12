# Archive Boundary

This document defines the boundary between live mock data and archived/deferred functionality.

## In Scope (Live Mock)
- Employee profile CRUD (GET, PATCH)
- Training status retrieval and module updates
- Salesforce profile retrieval and updates
- Access recommendations and selection
- Approval creation, approval, rejection
- ITSM ticket creation, retrieval, idempotency
- Slack message simulation
- LLM message simulation with fallback
- Audit event logging and retrieval
- Onboarding session lifecycle (start, select-access, questions)
- Demo reset

## Out of Scope (Archived / Deferred)
- Real Slack API integration
- Real Salesforce API integration
- Real ITSM/ServiceNow integration
- Real Okta/Entra ID provisioning
- Real HRIS data sync
- Real LLM provider integration (OpenAI, etc.)
- Authentication/authorization middleware
- Rate limiting
- Persistent audit log retention/purging
- Email notifications
- Webhook callbacks to external systems
- Multi-tenancy
- User-facing UI

## Rationale
All out-of-scope items require real third-party credentials, network access to external
services, or frontend code. The mock layer provides deterministic, testable behavior
for all core agent logic without these dependencies.
