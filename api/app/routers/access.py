from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import AccessRecommendationResponse
from ..services.recommendation_service import get_recommendations
from ..services.audit_service import log_event

router = APIRouter()


@router.get("/mock/access/recommendations/{employee_id}",
            response_model=AccessRecommendationResponse)
def access_recommendations(employee_id: str, db: Session = Depends(get_db)):
    result, error = get_recommendations(db, employee_id)
    if error == "EMPLOYEE_NOT_FOUND":
        raise HTTPException(status_code=404, detail={
            "error_code": "EMPLOYEE_NOT_FOUND", "message": "Employee not found",
        })
    if error == "EMPLOYEE_NOT_ACTIVE":
        raise HTTPException(status_code=403, detail={
            "error_code": "EMPLOYEE_NOT_ACTIVE", "message": "Employee is not active",
        })
    if error == "UNKNOWN_ROLE_LEVEL":
        raise HTTPException(status_code=409, detail={
            "error_code": "UNKNOWN_ROLE_LEVEL",
            "message": "Employee role or level is missing",
        })
    if error == "POLICY_NOT_FOUND":
        raise HTTPException(status_code=404, detail={
            "error_code": "POLICY_NOT_FOUND",
            "message": "No policy for this role/level",
        })
    log_event(db, None, employee_id, "system", "access-recommender",
              "recommendations_generated", "recommendation", employee_id,
              "GENERATED", None)
    return result
