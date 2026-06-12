# Expected Output Snapshots

All UUIDs/timestamps are dynamic. Assertions are field-level.

## Happy Path (approve)

```json
{
  "ok": true,
  "status": "COMPLETED",
  "approval_status": "APPROVED",
  "pre_approval_blocked": true,
  "ticket_created": true,
  "ticket_id": "present (itsm_<uuid>)",
  "correlation_id": "present",
  "audit_event_count": "> 0"
}
```

## Pending Path

```json
{
  "ok": true,
  "status": "COMPLETED",
  "approval_status": "PENDING",
  "pre_approval_blocked": true,
  "ticket_created": false,
  "ticket_id": "absent",
  "correlation_id": "present",
  "audit_event_count": "> 0"
}
```

## Reject Path

```json
{
  "ok": true,
  "status": "COMPLETED",
  "approval_status": "REJECTED",
  "pre_approval_blocked": true,
  "ticket_created": false,
  "ticket_id": "absent",
  "correlation_id": "present",
  "audit_event_count": "> 0"
}
```

## Expire Path

```json
{
  "ok": true,
  "approval_status": "EXPIRED",
  "ticket_created": false,
  "ticket_id": "absent",
  "correlation_id": "present",
  "audit_event_count": "> 0"
}
```

## Wrong Manager Path

```json
{
  "ok": true,
  "approval_status": "PENDING",
  "pre_approval_blocked": true,
  "ticket_created": false,
  "ticket_id": "absent",
  "correlation_id": "present",
  "audit_event_count": "> 0"
}
```

## Forbidden System Path

```json
{
  "ok": false,
  "status": "BLOCKED",
  "error_code": "FORBIDDEN_SYSTEM_SELECTED",
  "approval_created": false,
  "ticket_created": false,
  "forbidden": true,
  "correlation_id": "present",
  "audit_event_count": "> 0"
}
```

## LLM Fallback Path

```json
{
  "ok": true,
  "status": "COMPLETED",
  "approval_status": "APPROVED",
  "pre_approval_blocked": true,
  "ticket_created": true,
  "ticket_id": "present (itsm_<uuid>)",
  "correlation_id": "present",
  "audit_event_count": "> 0"
}
```

## Duplicate Ticket

```json
{
  "ok": true,
  "status": "CREATED",
  "duplicate": true,
  "ticket_id": "present (same as first)",
  "correlation_id": "present"
}
```
