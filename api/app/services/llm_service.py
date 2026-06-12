import os
import json
from typing import Dict, Any

FALLBACK_TEMPLATES = {
    "employee_onboarding_summary": """
Hello {employee_name},

Welcome to the team! Based on your role as {role} (level {level}), here is your onboarding summary:

- **Required tasks**: Please complete your HR profile, Slack setup, and T1 training.
- **Training status**: {training_summary}
- **Recommended access**: {recommended_systems_list}
- **Optional access**: {optional_systems_list}

Please review the recommended access and select the systems you need via the employee portal.

Your manager, {manager_name}, will be asked to approve your access requests.

We're glad to have you on board!
""",
    "manager_approval_request": """
Hello {manager_name},

{employee_name} ({role}, Level {level}) has requested access to the following systems:

{selected_systems_list}

Please review this request and **approve** or **reject** it using the approval dashboard.

Correlation ID: {correlation_id}
Request ID: {request_id}

Thank you.
"""
}

def get_fallback_message(message_type: str, context: Dict[str, Any]) -> str:
    template = FALLBACK_TEMPLATES.get(message_type)
    if not template:
        return f"Message type '{message_type}' not supported."
    try:
        return template.format(**context)
    except KeyError as e:
        return f"Missing context key: {e}."

async def generate_with_ollama(prompt: str, model: str, base_url: str) -> str | None:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2}
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
    except Exception:
        pass
    return None

async def generate_message(
    message_type: str,
    context: Dict[str, Any],
    provider: str = None,
    model: str = None,
    base_url: str = None,
    fallback_enabled: bool = True
) -> str:
    provider = provider or os.getenv("LLM_PROVIDER", "fallback")
    model = model or os.getenv("OLLAMA_MODEL", "gemma2:2b")
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    fallback_env = os.getenv("LLM_FALLBACK_ENABLED", "true")
    fallback_enabled = fallback_enabled or fallback_env.lower() == "true"

    prompt = f"""You are an HR onboarding assistant. Generate a {message_type.replace('_', ' ')} using the following information. Keep it professional and concise.

Context: {json.dumps(context, indent=2)}

Output only the message, no extra text."""

    if provider == "ollama":
        llm_output = await generate_with_ollama(prompt, model, base_url)
        if llm_output:
            return llm_output.strip()

    if fallback_enabled:
        return get_fallback_message(message_type, context)

    return f"[Message generation failed] Unable to generate {message_type}."
