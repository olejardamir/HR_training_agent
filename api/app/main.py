from contextlib import asynccontextmanager
from fastapi import FastAPI
from .config import settings
from .database import engine
from .models import Base
from .routers import health, onboarding, hr, training, access, approvals, itsm, slack, llm, audit, salesforce


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="HR Onboarding Agent API", lifespan=lifespan)

app.include_router(health.router)
app.include_router(onboarding.router)
app.include_router(hr.router)
app.include_router(training.router)
app.include_router(access.router)
app.include_router(approvals.router)
app.include_router(itsm.router)
app.include_router(slack.router)
app.include_router(llm.router)
app.include_router(audit.router)
app.include_router(salesforce.router)


@app.post("/demo/reset")
def reset_demo():
    from .seed import reset_and_seed
    from .database import SessionLocal
    from .services.audit_service import log_event
    from .models import Employee, Manager, TrainingStatusTable, SalesforceProfile, RoleAccessPolicy, ITSMTicket
    reset_and_seed()
    db = SessionLocal()
    try:
        log_event(db, "demo_reset", None, "system", "demo",
                  "demo_reset", "database", None, "RESET", None)
        db.commit()
        counts = {
            "employees": db.query(Employee).count(),
            "managers": db.query(Manager).count(),
            "training_statuses": db.query(TrainingStatusTable).count(),
            "salesforce_profiles": db.query(SalesforceProfile).count(),
            "role_access_policies": db.query(RoleAccessPolicy).count(),
            "itsm_tickets": db.query(ITSMTicket).count(),
        }
    finally:
        db.close()
    return {
        "ok": True,
        "status": "reset_complete",
        "message": "Database reseeded successfully.",
        **counts,
    }
