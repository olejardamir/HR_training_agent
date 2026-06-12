from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import (
    TrainingStatusResponse, TrainingModuleStatus,
    TrainingModulePatchRequest,
)
from ..services.training_service import get_training_status, update_module
from ..services.audit_service import log_event

router = APIRouter()


@router.get("/mock/training/status/{employee_id}", response_model=TrainingStatusResponse)
def get_training(employee_id: str, db: Session = Depends(get_db)):
    modules = get_training_status(db, employee_id)
    log_event(db, None, employee_id, "system", "training-mock",
              "training_status_loaded", "training", employee_id, "LOADED", None)
    return TrainingStatusResponse(
        employee_id=employee_id,
        modules=[TrainingModuleStatus(**m) for m in modules],
    )


@router.patch("/mock/training/status/{employee_id}/modules/{module_id}")
def patch_training_module(employee_id: str, module_id: str,
                          request: TrainingModulePatchRequest,
                          db: Session = Depends(get_db)):
    allowed_modules = {"T1", "T2", "T3", "T4"}
    if module_id not in allowed_modules:
        return JSONResponse(status_code=400, content={
            "ok": False, "status": "ERROR",
            "error_code": "INVALID_MODULE",
            "message": "Only modules T1-T4 are supported",
        })
    allowed_statuses = {"complete", "incomplete", "not_required_yet", "blocked"}
    if request.status not in allowed_statuses:
        return JSONResponse(status_code=400, content={
            "ok": False, "status": "ERROR",
            "error_code": "INVALID_STATUS",
            "message": f"Invalid status '{request.status}'",
        })

    result = update_module(db, employee_id, module_id, request.status)
    log_event(db, request.correlation_id, employee_id, "employee", employee_id,
              "training_updated", "training", f"{employee_id}/{module_id}",
              "UPDATED", None)

    return {
        "ok": True, "status": "UPDATED",
        "employee_id": employee_id,
        "module_id": module_id,
        "module_status": request.status,
        "correlation_id": request.correlation_id,
    }
