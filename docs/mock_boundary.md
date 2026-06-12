# Mock Boundary

Defines what is mocked and how each mock behaves.

## Mocked Services

| Service | Mock Behavior | Deterministic? |
|---|---|---|
| HR/Employee | In-memory DB, PATCH updates `preferred_name` | Yes |
| Training | In-memory DB, PATCH updates module status | Yes |
| Salesforce | In-memory DB, PATCH updates salesforce fields | Yes |
| Approvals | Creation uses `request_id`, approval/rejection sets status | Yes |
| ITSM | Creates tickets with `itsm_<uuid>` IDs, idempotent via SHA-256 keys | Yes |
| Slack | Stores messages in DB, returns `slack_<uuid>` IDs | Yes |
| LLM | Returns template-based or Ollama-generated messages per `LLM_PROVIDER` setting | Yes |

## Key Mock Rules
- All IDs are prefixed: `req_`, `apr_`, `itsm_`, `corr_`, `slack_`
- `select_access` requires an active onboarding session (409 if missing)
- Forbidden systems return 403 during selection
- Ticket creation blocked before approval returns 409 with `pre_approval_blocked=true`
- Duplicate idempotency keys return existing ticket (not 409)
- `log_event` uses `db.flush()`; callers must `db.commit()` after
- No real network calls are made

## PII Protection
- Audit metadata is filtered per allowlist defined in `logic/pii.py`
- Blocked keys: phone, address, birth date, SSN, tokens, raw prompts
