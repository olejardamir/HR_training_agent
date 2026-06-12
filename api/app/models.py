from sqlalchemy import Column, String, Integer, JSON, DateTime, Enum, Text
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

class TrainingStatusTable(Base):
    __tablename__ = "training_status"
    employee_id = Column(String, primary_key=True, index=True)
    modules = Column(JSON)

class RoleAccessPolicy(Base):
    __tablename__ = "role_access_policies"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    level = Column(String)
    required_systems = Column(JSON)
    recommended_systems = Column(JSON)
    forbidden_systems = Column(JSON)
    policy_version = Column(String)

class PeerAccessPattern(Base):
    __tablename__ = "peer_access_patterns"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    level = Column(String)
    peer_count = Column(Integer)
    common_access = Column(JSON)

class DepartmentStandard(Base):
    __tablename__ = "department_standards"
    id = Column(Integer, primary_key=True, index=True)
    department = Column(String, unique=True)
    standard_systems = Column(JSON)

class OnboardingSession(Base):
    __tablename__ = "onboarding_sessions"
    session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String, unique=True)
    correlation_id = Column(String)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SelectedAccessRequest(Base):
    __tablename__ = "selected_access_requests"
    request_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String)
    selected_systems = Column(JSON)
    status = Column(String)
    approval_id = Column(String, nullable=True)
    ticket_id = Column(String, nullable=True)
    idempotency_key = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ManagerApproval(Base):
    __tablename__ = "manager_approvals"
    approval_id = Column(String, primary_key=True, index=True)
    request_id = Column(Integer)
    employee_id = Column(String)
    manager_id = Column(String)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    decision_reason = Column(String, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)

class ITSMTicket(Base):
    __tablename__ = "itsm_tickets"
    ticket_id = Column(String, primary_key=True, index=True)
    request_id = Column(Integer)
    employee_id = Column(String)
    selected_systems = Column(JSON)
    status = Column(String)
    idempotency_key = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditEvent(Base):
    __tablename__ = "audit_events"
    event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    correlation_id = Column(String, index=True)
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

class SlackMessage(Base):
    __tablename__ = "slack_messages"
    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    channel_or_user = Column(String)
    message_type = Column(String)
    message = Column(String)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
