from sqlalchemy.orm import Session
from ..models import TrainingStatusTable


def get_training_status(db: Session, employee_id: str):
    rows = db.query(TrainingStatusTable).filter(
        TrainingStatusTable.employee_id == employee_id
    ).all()
    modules = [{"module_id": r.module_id, "status": r.status} for r in rows]
    return modules


def update_module(db: Session, employee_id: str, module_id: str, status: str):
    row = db.query(TrainingStatusTable).filter(
        TrainingStatusTable.employee_id == employee_id,
        TrainingStatusTable.module_id == module_id,
    ).first()
    if row:
        row.status = status
    else:
        row = TrainingStatusTable(
            employee_id=employee_id, module_id=module_id, status=status
        )
        db.add(row)
    db.flush()
    return {"module_id": module_id, "status": status}
