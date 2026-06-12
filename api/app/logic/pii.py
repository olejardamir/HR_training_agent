PII_ALLOWLIST = {
    "employee_id", "role", "level", "department", "manager_id",
    "request_id", "approval_id", "ticket_id", "selected_systems",
    "reason_codes", "status", "error_code", "policy_version",
    "peer_count", "correlation_id",
}

PII_BLOCKLIST = {
    "phone_number", "home_address", "birth_date", "government_id",
    "ssn", "passport", "full_email_body", "secret", "token",
    "raw_prompt", "password", "api_key",
}


def filter_metadata(metadata: dict) -> dict:
    return {k: v for k, v in metadata.items() if k in PII_ALLOWLIST}


def is_metadata_safe(metadata: dict) -> bool:
    for key in metadata:
        if key.lower() in PII_BLOCKLIST:
            return False
        for block in PII_BLOCKLIST:
            if block in key.lower():
                return False
    return True
