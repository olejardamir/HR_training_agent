from ..services.policy_service import get_policy, get_peer_pattern


def evaluate_policy(db, role: str, level: str):
    policy = get_policy(db, role, level)
    peer = get_peer_pattern(db, role, level)
    return policy, peer


def is_system_forbidden(db, role: str, level: str, system: str) -> bool:
    policy = get_policy(db, role, level)
    if policy and policy.forbidden_systems:
        return system in policy.forbidden_systems
    return False
