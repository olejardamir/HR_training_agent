from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import SalesforceProfile, SalesforceProfileOut, SalesforceProfilePatchRequest
from ..services.salesforce_service import get_profile, update_profile
from ..services.audit_service import log_event

router = APIRouter()


@router.get("/mock/salesforce/profile/{employee_id}",
            response_model=SalesforceProfile)
def get_salesforce_profile(employee_id: str, db: Session = Depends(get_db)):
    profile = get_profile(db, employee_id)
    if not profile:
        return SalesforceProfile(
            employee_id=employee_id,
            profile_complete=False,
            setup_status="no_profile",
            assigned_licenses=[],
        )
    return SalesforceProfile(
        employee_id=profile.employee_id,
        profile_complete=profile.profile_complete,
        setup_status=profile.setup_status,
        assigned_licenses=profile.assigned_licenses or [],
        last_updated=str(profile.last_updated) if profile.last_updated else None,
    )


@router.patch("/mock/salesforce/profile/{employee_id}")
def patch_salesforce_profile(employee_id: str,
                             request: SalesforceProfilePatchRequest,
                             db: Session = Depends(get_db)):
    result = update_profile(db, employee_id,
                            request.salesforce_profile_complete,
                            request.role_profile)
    if isinstance(result, dict) and result.get("error") == "PROFILE_NOT_FOUND":
        return JSONResponse(status_code=404, content={
            "ok": False, "status": "ERROR", "error_code": "PROFILE_NOT_FOUND",
            "message": "Salesforce profile not found",
        })

    log_event(db, request.correlation_id, employee_id,
              "system", "salesforce-mock",
              "salesforce_profile_updated", "salesforce", employee_id,
              "UPDATED", None)

    return {
        "ok": True, "status": "UPDATED",
        "employee_id": employee_id,
        "setup_status": result["setup_status"],
        "profile_complete": result["profile_complete"],
        "correlation_id": request.correlation_id,
    }
