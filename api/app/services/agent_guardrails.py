HR_TOPIC_KEYWORDS = [
    "training", "t1", "t2", "t3", "t4", "module",
    "salesforce", "crm", "setup",
    "profile", "personal info", "update",
    "access", "permission", "entitlement", "system",
    "approval", "manager", "pending", "approve",
    "ticket", "it", "itsm",
    "onboarding", "new hire", "orientation",
    "role", "level", "department",
    "slack",
    "status", "progress",
    "policy", "guideline",
    "hr",
]


def is_on_topic(message: str) -> bool:
    lower = message.lower()
    return any(kw in lower for kw in HR_TOPIC_KEYWORDS)


STATE_KEYWORDS = [
    "status", "am i done", "have i completed", "is my",
    "what is my", "tell me my", "show my",
    "training", "salesforce", "profile", "role",
    "level", "department",
]

NO_CONTEXT_ANSWER = (
    "I do not have enough approved onboarding guidance to answer that. "
    "Please check with HR or your manager."
)


def filter_approved_matches(matches):
    return [m for m in matches if m.get("runtime_approved") is True]


def has_approved_context(matches):
    return any(m.get("runtime_approved") for m in matches)


def is_state_only_question(message):
    lower = message.lower()
    state_indicators = [
        "status", "am i done", "have i completed", "is my",
        "what is my", "tell me my", "show my",
    ]
    for kw in state_indicators:
        if kw in lower:
            return True
    return False


def build_no_context_answer():
    return NO_CONTEXT_ANSWER


def summarize_retrieval(matches, retrieval=None):
    return {
        "used_content_ids": list(set(m["content_id"] for m in matches)),
        "used_chunk_ids": list(set(m["chunk_id"] for m in matches)),
        "source_ids": list(set(
            sid for m in matches for sid in m.get("source_ids", [])
        )),
        "retrieval_scores": [m.get("score") for m in matches],
        "retrieval_method": (retrieval or {}).get("retrieval_method", "unknown"),
        "fallback_used": len(matches) == 0,
        "llm_used": False,
    }
