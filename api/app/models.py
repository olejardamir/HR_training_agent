from sqlalchemy import (
    Column, String, Integer, JSON, DateTime, Enum, Text, Boolean,
    UniqueConstraint, Index
)
from sqlalchemy.sql import func
from .database import Base
import enum


class EmploymentStatus(str, enum.Enum):
    NEW_HIRE = "new_hire"
    ACTIVE = "active"
    INACTIVE = "inactive"


class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class Employee(Base):
    __tablename__ = "employees"
    employee_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    role = Column(String)
    level = Column(String)
    department = Column(String)
    manager_id = Column(String, nullable=True)
    start_date = Column(String)
    employment_status = Column(Enum(EmploymentStatus), default=EmploymentStatus.NEW_HIRE)
    profile_status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

Index("ix_employees_role_level", Employee.role, Employee.level)


class Manager(Base):
    __tablename__ = "managers"
    manager_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    is_active = Column(Boolean, default=True)
    has_contact = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TrainingStatusTable(Base):
    __tablename__ = "training_status"
    __table_args__ = (
        UniqueConstraint("employee_id", "module_id", name="uq_training_employee_module"),
    )
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String)
    module_id = Column(String)
    status = Column(String)
Index("ix_training_employee_modules", TrainingStatusTable.employee_id, TrainingStatusTable.module_id)


class SalesforceProfile(Base):
    __tablename__ = "salesforce_profiles"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String, unique=True, index=True)
    profile_complete = Column(Boolean, default=False)
    setup_status = Column(String, default="not_started")
    assigned_licenses = Column(JSON, default=[])
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RoleAccessPolicy(Base):
    __tablename__ = "role_access_policies"
    __table_args__ = (
        UniqueConstraint("role", "level", "policy_version", name="uq_role_level_policy"),
    )
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role = Column(String)
    level = Column(String)
    required_systems = Column(JSON)
    recommended_systems = Column(JSON)
    optional_systems = Column(JSON, default=[])
    forbidden_systems = Column(JSON)
    policy_version = Column(String)


class PeerAccessPattern(Base):
    __tablename__ = "peer_access_patterns"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role = Column(String)
    level = Column(String)
    peer_count = Column(Integer)
    common_access = Column(JSON)

Index("ix_peer_role_level", PeerAccessPattern.role, PeerAccessPattern.level)


class DepartmentStandard(Base):
    __tablename__ = "department_standards"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    department = Column(String, unique=True)
    standard_systems = Column(JSON)


class OnboardingSession(Base):
    __tablename__ = "onboarding_sessions"
    session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String, unique=True)
    correlation_id = Column(String)

Index("ix_onboarding_correlation", OnboardingSession.correlation_id)


class SelectedAccessRequest(Base):
    __tablename__ = "selected_access_requests"
    __table_args__ = (
        Index("ix_selection_employee", "employee_id"),
        UniqueConstraint("employee_id", "idempotency_key", name="uq_selection_employee_idempotency"),
    )
    request_id = Column(String, primary_key=True, index=True)
    employee_id = Column(String)
    selected_systems = Column(JSON)
    status = Column(String)
    approval_id = Column(String, nullable=True)
    ticket_id = Column(String, nullable=True)
    idempotency_key = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ManagerApproval(Base):
    __tablename__ = "manager_approvals"
    __table_args__ = (
        UniqueConstraint("request_id", name="uq_active_approval_per_request"),
        Index("ix_approval_employee", "employee_id"),
    )
    approval_id = Column(String, primary_key=True, index=True)
    request_id = Column(String)
    employee_id = Column(String)
    manager_id = Column(String)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    decision_reason = Column(String, nullable=True)
    decided_by = Column(String, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    expired_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ITSMTicket(Base):
    __tablename__ = "itsm_tickets"
    ticket_id = Column(String, primary_key=True, index=True)
    request_id = Column(String)
    employee_id = Column(String)
    approval_id = Column(String)
    selected_systems = Column(JSON)
    status = Column(String)
    idempotency_key = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Index("ix_ticket_request", ITSMTicket.request_id)
Index("ix_ticket_approval", ITSMTicket.approval_id)
Index("ix_ticket_employee", ITSMTicket.employee_id)


class SlackMessage(Base):
    __tablename__ = "slack_messages"
    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    channel_or_user = Column(String)
    message_type = Column(String)
    message = Column(String)
    metadata_json = Column(JSON, nullable=True)
    simulate_failure = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Index("ix_slack_employee", SlackMessage.channel_or_user)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    correlation_id = Column(String)
    employee_id = Column(String, nullable=True)
    actor_type = Column(String)
    actor_id = Column(String, nullable=True)
    action = Column(String)
    target_type = Column(String, nullable=True)
    target_id = Column(String, nullable=True)
    status = Column(String)
    reason_code = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Index("ix_audit_employee", AuditEvent.employee_id)
Index("ix_audit_correlation", AuditEvent.correlation_id)
Index("ix_audit_created", AuditEvent.created_at)
