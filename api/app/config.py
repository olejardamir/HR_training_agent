import os
from functools import lru_cache


class Settings:
    postgres_db: str = os.getenv("POSTGRES_DB", "hr_onboarding")
    postgres_user: str = os.getenv("POSTGRES_USER", "hr_agent")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "hr_agent_dev_password")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://hr_agent:hr_agent_dev_password@postgres:5432/hr_onboarding",
    )

    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_base_url: str = os.getenv("API_BASE_URL", "http://api:8000")
    public_api_base_url: str = os.getenv("PUBLIC_API_BASE_URL", "http://localhost:8000")

    n8n_host: str = os.getenv("N8N_HOST", "localhost")
    n8n_port: int = int(os.getenv("N8N_PORT", "5678"))
    n8n_protocol: str = os.getenv("N8N_PROTOCOL", "http")
    n8n_secure_cookie: bool = os.getenv("N8N_SECURE_COOKIE", "false").lower() == "true"

    llm_provider: str = os.getenv("LLM_PROVIDER", "fallback")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma2:2b")
    llm_fallback_enabled: bool = os.getenv("LLM_FALLBACK_ENABLED", "true").lower() == "true"
    llm_timeout_seconds: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "3"))

    demo_reset_enabled: bool = os.getenv("DEMO_RESET_ENABLED", "true").lower() == "true"
    app_version: str = os.getenv("APP_VERSION", "0.1.0")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
