import hashlib


def compute_idempotency_key(employee_id: str, request_id, approval_id: str, systems: list) -> str:
    raw = f"{employee_id}|{request_id}|{approval_id}|{','.join(sorted(systems))}"
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_idempotency_key(key: str, employee_id: str, request_id, approval_id: str, systems: list) -> bool:
    expected = compute_idempotency_key(employee_id, request_id, approval_id, systems)
    return key == expected
