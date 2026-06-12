# HR Onboarding Agent – Solution Design

**Candidate exercise:** Enterprise Agent – Solutions Developer  
**Scenario:** HR onboarding agent  
**Stack:** n8n + FastAPI + PostgreSQL + Ollama/fallback + Docker Compose  
**Runtime:** Free Linux, no paid services

---

## Overview

The system is a governed HR onboarding agent that automates new employee access requests. It uses n8n as the visible orchestration layer, FastAPI to mock enterprise SaaS systems (HR, Slack, Training, ITSM), PostgreSQL for state and audit, and Ollama (or deterministic fallback) for human‑friendly messages.

Key differentiator: this is **not** a generic onboarding template. It adds role‑level reasoning, peer‑pattern access recommendations, asynchronous manager approval, policy validation, and a full audit trail.

---

## Agent Behavior

The agent receives an employee ID and then:

1. Fetches the employee's role, level, department, and manager from the HR mock.
2. Checks T1–T4 training completion status.
3. Recommends required and optional systems based on:
   - Role‑level access policy (required, recommended, forbidden)
   - Peer patterns (same role/level common access)
   - Department standards
4. Generates an employee onboarding summary (LLM or fallback).
5. Stores the summary as a Slack‑style message.
6. Accepts the employee's selected systems (validated against forbidden list).
7. Creates a manager approval request (state = PENDING).
8. Generates a manager approval message (LLM or fallback) and stores it.
9. **Attempts to create an ITSM ticket before approval – this is intentionally blocked, proving the approval gate.**
10. Waits for manager approval (demo can auto‑approve or stay pending).
11. Only after `APPROVED` status does it create an ITSM ticket (idempotent).
12. Returns final status and retrieves audit events.

The LLM is used **only** for messages; deterministic policy and state machines control all authorization decisions.

---

## Architecture

```
[New hire webhook] → n8n → FastAPI mocks (HR, Training, Slack, Approval, ITSM, Audit)
                           ↓
                     PostgreSQL (state, approvals, tickets, audit)
                           ↑
                     Ollama / fallback (messages only)
```

All external SaaS interactions are mocked; the prototype requires no real credentials.

---

## Key Governance Controls

| Control | Implementation |
|---------|----------------|
| Role/level source of truth | HR mock (employee_id → role, level) – not user‑supplied |
| Peer‑pattern recommendation | Fixture of same‑role/level common access, frequency threshold |
| Forbidden system blocking | Policy engine rejects selection of restricted systems |
| Manager approval gate | Ticket creation endpoint checks approval status; returns 403 if not APPROVED |
| Idempotency | Each ticket request uses `idempotency_key`; duplicate requests return existing ticket |
| Audit trail | Every major action logged with `correlation_id` |
| LLM boundary | LLM generates text only; never decides approval or access |

---

## Production Evolution Path

| Prototype | Production |
|-----------|------------|
| FastAPI HR mock | Workday, BambooHR, SuccessFactors API |
| Slack mock | Real Slack API with bot scopes |
| Training mock | LMS API (Docebo, Cornerstone, etc.) |
| ITSM mock | ServiceNow, Jira Service Management |
| Local Ollama | Enterprise LLM endpoint or self‑hosted model |
| Manual manager approval | Slack interactive approval or ITSM approval workflow |
| Local PostgreSQL | Managed database + SIEM export |

---

## Why This Is Not Just an n8n Template

Standard n8n onboarding templates provision accounts and send notifications. This solution adds:

- Role‑level + peer‑pattern **access recommendation**
- **Deterministic policy validation** independent of LLM
- **Asynchronous manager approval** that **blocks** ticket creation
- **Idempotent ticket creation** only after approval
- **Full audit trail** with correlation IDs

The n8n workflow orchestrates these custom backend services; the governance logic resides in FastAPI and PostgreSQL, not in the workflow canvas.

---

## Conclusion

The HR onboarding agent demonstrates bounded autonomy, enterprise‑grade controls, and a free‑Linux runnable prototype. It satisfies all candidate exercise requirements while remaining production‑shaped and evaluator‑friendly.
