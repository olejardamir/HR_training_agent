from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ITSMTicket
from ..schemas import CreateTicketRequest, TicketResponse
from ..services.itsm_service import create_ticket
from ..services.audit_service import log_event

router = APIRouter()


@router.post("/mock/itsm/tickets", response_model=TicketResponse)
def create_ticket_endpoint(request: CreateTicketRequest,
                           db: Session = Depends(get_db)):
    log_event(db, request.correlation_id, request.employee_id,
              "system", "itsm-mock",
              "ticket_creation_attempted", "ticket", None,
              "ATTEMPTED", None)

    result = create_ticket(
        db, request.employee_id, request.approval_id,
        request.requested_systems, request.idempotency_key,
        simulate_failure=request.simulate_failure,
    )
    if result.get("error_code") == "ITSM_MOCK_FAILURE":
        log_event(db, request.correlation_id, request.employee_id,
                  "system", "itsm-mock",
                  "itsm_ticket_failed", "ticket", None,
                  "FAILED", "ITSM_MOCK_FAILURE")
        db.commit()
        return JSONResponse(status_code=503, content={
            "ok": False, "status": "FAILED",
            "error_code": "ITSM_MOCK_FAILURE",
            "reason_code": "ITSM_MOCK_FAILURE",
            "ticket_created": False,
            "recoverable": True,
            "next_action": "RETRY_ITSM_TICKET",
            "correlation_id": request.correlation_id,
        })
    if "error_code" in result:
        log_event(db, request.correlation_id, request.employee_id,
                  "system", "itsm-mock",
                  "ticket_blocked", "ticket", None,
                  "BLOCKED", result.get("error_code"))
        db.commit()
        return JSONResponse(status_code=409, content=TicketResponse(
            ok=False, status="BLOCKED",
            error_code=result.get("error_code", "MANAGER_APPROVAL_REQUIRED"),
            reason_code=result.get("reason_code", "MANAGER_APPROVAL_REQUIRED"),
            message="A valid manager approval is required before ticket creation.",
            employee_id=request.employee_id,
            approval_id=request.approval_id,
            ticket_created=False, pre_approval_blocked=True,
            correlation_id=request.correlation_id,
            recoverable=True,
            next_action="WAIT_FOR_MANAGER_APPROVAL",
        ).model_dump())
    if "error" in result:
        error = result["error"]
        status = 409 if error == "APPROVAL_NOT_APPROVED" else 404
        return JSONResponse(status_code=status, content={"error": result.get("error")})

    db.commit()

    is_duplicate = result.get("duplicate", False)
    if is_duplicate:
        log_event(db, request.correlation_id, request.employee_id,
                  "system", "itsm-mock",
                  "duplicate_ticket_returned", "ticket", result.get("ticket_id"),
                  "DUPLICATE", None)
    else:
        log_event(db, request.correlation_id, request.employee_id,
                  "system", "itsm-mock",
                  "ticket_created", "ticket", result.get("ticket_id"),
                  "CREATED", None)
    db.commit()

    return TicketResponse(
        ok=True, status="CREATED",
        ticket_id=result.get("ticket_id"),
        request_id=str(result.get("request_id", "")),
        approval_id=result.get("approval_id", request.approval_id),
        employee_id=result.get("employee_id", request.employee_id),
        requested_systems=result.get("requested_systems", request.requested_systems),
        ticket_created=True,
        duplicate=is_duplicate,
        correlation_id=request.correlation_id,
        next_action="FETCH_FINAL_STATUS",
    )


@router.get("/mock/itsm/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(ITSMTicket).filter(
        ITSMTicket.ticket_id == ticket_id
    ).first()
    if not ticket:
        return JSONResponse(status_code=404, content={
            "ok": False, "status": "ERROR", "error_code": "TICKET_NOT_FOUND",
            "message": "Ticket not found",
        })
    return TicketResponse(
        ok=True, status=ticket.status,
        ticket_id=ticket.ticket_id,
        request_id=str(ticket.request_id),
        approval_id=ticket.approval_id,
        employee_id=ticket.employee_id,
        requested_systems=ticket.selected_systems,
        ticket_created=True,
        correlation_id=None,
    )


@router.get("/mock/itsm/tickets", response_model=list[TicketResponse])
def list_tickets(employee_id: str = Query(None),
                 db: Session = Depends(get_db)):
    q = db.query(ITSMTicket)
    if employee_id:
        q = q.filter(ITSMTicket.employee_id == employee_id)
    tickets = q.order_by(ITSMTicket.created_at).all()
    return [
        TicketResponse(
            ok=True, status=t.status,
            ticket_id=t.ticket_id,
            request_id=str(t.request_id),
            approval_id=t.approval_id,
            employee_id=t.employee_id,
            requested_systems=t.selected_systems,
            ticket_created=True,
        )
        for t in tickets
    ]
