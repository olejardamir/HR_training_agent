from fastapi import APIRouter
from ..config import settings
from ..schemas import HealthResponse, ReadyResponse, VersionResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        ok=True, status="healthy",
        service="hr-onboarding-api", version=settings.app_version,
    )


@router.get("/ready", response_model=ReadyResponse)
def ready():
    from ..database import SessionLocal
    from sqlalchemy import text
    from ..models import Employee
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        emp_count = db.query(Employee).count()
        db.close()
        has_seed = emp_count > 0
        return ReadyResponse(
            ok=True, status="ready", database="ready",
            seed_data="loaded" if has_seed else "empty",
            llm="fallback_available",
            version=settings.app_version,
        )
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail={
            "ok": False, "status": "not_ready",
            "error_code": "DATABASE_UNAVAILABLE",
            "message": "Database connection failed.",
            "recoverable": True,
        })


@router.get("/version", response_model=VersionResponse)
def version():
    return VersionResponse(
        service="hr-onboarding-api",
        version=settings.app_version,
        runtime="local-demo",
        mock_boundary=True,
    )
