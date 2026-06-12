from sqlalchemy.orm import Session
from ..models import RoleAccessPolicy, PeerAccessPattern, DepartmentStandard


def get_policy(db: Session, role: str, level: str):
    return db.query(RoleAccessPolicy).filter(
        RoleAccessPolicy.role == role,
        RoleAccessPolicy.level == level,
    ).first()


def get_peer_pattern(db: Session, role: str, level: str):
    return db.query(PeerAccessPattern).filter(
        PeerAccessPattern.role == role,
        PeerAccessPattern.level == level,
    ).first()


def get_department_standard(db: Session, department: str):
    return db.query(DepartmentStandard).filter(
        DepartmentStandard.department == department
    ).first()
