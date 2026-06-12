import httpx
from ..config import settings


def _build_employee_summary(context: dict) -> str:
    name = context.get("employee_name", "the new employee")
    role = context.get("role", "Unknown")
    level = context.get("level", "Unknown")
    training = context.get("training_summary", "No training data")
    recommended = context.get("recommended_systems_list", "None")
    optional = context.get("optional_systems_list", "None")
    manager = context.get("manager_name", "your manager")
    return (
        f"Hello {name}! Welcome as {role} (Level {level}). "
        f"Training summary: {training}. "
        f"Recommended systems: {recommended}. "
        f"Optional systems: {optional}. "
        f"Your manager is {manager}."
    )


def _build_manager_request(context: dict) -> str:
    name = context.get("employee_name", "an employee")
    role = context.get("role", "Unknown")
    level = context.get("level", "Unknown")
    systems = context.get("selected_systems_list", "No systems selected")
    cid = context.get("correlation_id", "unknown")
    rid = context.get("request_id", "unknown")
    return (
        f"Approval request for {name} ({role} L{level}). "
        f"Requested systems: {systems}. "
        f"Correlation ID: {cid}, Request ID: {rid}."
    )


FALLBACK_TEMPLATES = {
    "employee_onboarding_summary": _build_employee_summary,
    "manager_approval_request": _build_manager_request,
    "recommendation_explanation": lambda ctx: (
        f"Recommendations based on role-level policy and peer patterns."
    ),
    "status_update": lambda ctx: (
        f"Onboarding status: {ctx.get('status', 'in progress')}."
    ),
    "onboarding_question_answer": lambda ctx: (
        ctx.get("answer", "Please contact your HR representative.")
    ),
}


async def generate_message(message_type: str, context: dict,
                           fallback_enabled: bool = True) -> tuple:
    if settings.llm_provider == "ollama" and not fallback_enabled:
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                resp = await client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={
                        "model": settings.ollama_model,
                        "prompt": f"Generate a {message_type} message: {context}",
                        "stream": False,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("response", ""), "ollama"
        except Exception:
            pass

    template_fn = FALLBACK_TEMPLATES.get(message_type)
    if template_fn:
        return template_fn(context), "fallback"
    return f"[{message_type}] No template available.", "fallback"
