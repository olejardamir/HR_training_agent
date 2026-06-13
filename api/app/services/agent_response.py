import os


def build_answer(message, state, matches):
    has_llm = bool(os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY"))
    if has_llm:
        return _build_with_llm(message, state, matches)
    return _build_deterministic(message, state, matches)


def _build_deterministic(message, state, matches):
    lower = message.lower()
    parts = []

    if matches:
        top = matches[0]
        parts.append(f"Based on approved onboarding content: {top['title']}")
        text = top["text"]
        excerpt = text[:300] + "..." if len(text) > 300 else text
        parts.append(excerpt)
    else:
        parts.append("Approved onboarding knowledge was not found for that question.")

    pending = [t for t in state.get("training", []) if t["status"] != "complete"]
    if pending:
        mods = ", ".join(t["module_id"] for t in pending)
        parts.append(f"Your current pending training: {mods}.")
    else:
        complete = [t for t in state.get("training", []) if t["status"] == "complete"]
        if complete:
            parts.append("All assigned training is complete.")

    sf = state.get("salesforce_setup_status", "not_started")
    if sf != "complete":
        parts.append(f"Salesforce setup status: {sf}.")

    return " ".join(parts)


def _build_with_llm(message, state, matches):
    from ..services.llm_service import query_llm

    context_parts = []
    for m in matches[:3]:
        context_parts.append(f"[{m['title']}] {m['text'][:500]}")

    training_str = "; ".join(
        f"{t['module_id']}: {t['status']}" for t in state.get("training", [])
    )

    prompt = (
        "You are an HR onboarding assistant.\n"
        "Answer only using:\n"
        "1. the employee/workflow state provided\n"
        "2. the approved onboarding/training content provided\n\n"
        "Do not invent company policy.\n"
        "Do not invent training completion status.\n"
        "Do not claim a ticket was submitted unless ticket state says so.\n"
        "Do not claim access is allowed unless role/level policy says so.\n"
        "Do not claim approval happened unless approval state says so.\n"
        "If the approved content is insufficient, say so briefly.\n"
        "Give a concise answer and one next action when possible.\n\n"
        f"Employee question: {message}\n\n"
        f"Employee state: role={state['role']}, level={state['level']}, "
        f"training=[{training_str}], "
        f"salesforce_setup={state['salesforce_setup_status']}\n\n"
        f"Approved content:\n" + "\n".join(context_parts)
    )

    return query_llm(prompt, max_tokens=300)
