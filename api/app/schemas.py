from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


class ApiEnvelope(BaseModel):
    ok: bool
    status: str
    message: Optional[str] = None
    employee_id: Optional[str] = None
    correlation_id: Optional[str] = None
    error_code: Optional[str] = None
    recoverable: Optional[bool] = None
    next_action: Optional[str] = None


class ApiError(BaseModel):
    ok: bool = False
    status: str = "ERROR"
    error_code: str
    message: str
    employee_id: Optional[str] = None
    correlation_id: Optional[str] = None
    recoverable: Optional[bool] = None
    next_action: Optional[str] = None


class HealthResponse(BaseModel):
    ok: bool = True
    status: str = "healthy"
    service: str = "hr-onboarding-api"
    version: str = "0.1.0"


class ReadyResponse(BaseModel):
    ok: bool
    status: str
    database: Optional[str] = None
    seed_data: Optional[str] = None
    llm: Optional[str] = None
    version: Optional[str] = None
    error_code: Optional[str] = None
    message: Optional[str] = None
    recoverable: Optional[bool] = None


class VersionResponse(BaseModel):
    service: str = "hr-onboarding-api"
    version: str = "0.1.0"
    runtime: str = "local-demo"
    mock_boundary: bool = True


class EmployeeProfile(BaseModel):
    employee_id: str
    name: str
    email: str
    role: str
    level: str
    department: str
    manager_id: Optional[str] = None
    start_date: str
    employment_status: str
    profile_status: str = "active"


class EmployeeProfileStatus(BaseModel):
    hr_profile_complete: bool = False
    slack_profile_complete: bool = False
    salesforce_profile_complete: bool = False


class EmployeeProfilePatchRequest(BaseModel):
    hr_profile_complete: Optional[bool] = None
    preferred_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    level: Optional[str] = None
    manager_id: Optional[str] = None
    employment_status: Optional[str] = None
    department: Optional[str] = None
    correlation_id: str


class ManagerProfile(BaseModel):
    manager_id: str
    name: str
    email: str
    is_active: bool = True
    has_contact: bool = True


class TrainingModuleStatus(BaseModel):
    module_id: str
    status: str


class TrainingStatusResponse(BaseModel):
    employee_id: str
    modules: List[TrainingModuleStatus]


class TrainingModulePatchRequest(BaseModel):
    status: Literal["complete", "incomplete", "not_required_yet", "blocked"]
    correlation_id: str


class SalesforceProfile(BaseModel):
    employee_id: str
    profile_complete: bool = False
    setup_status: str = "not_started"
    assigned_licenses: List[str] = []
    last_updated: Optional[str] = None

SalesforceProfileOut = SalesforceProfile


class SalesforceProfilePatchRequest(BaseModel):
    salesforce_profile_complete: Optional[bool] = None
    role_profile: Optional[str] = None
    correlation_id: str


class AccessRecommendation(BaseModel):
    system: str
    recommendation_type: str
    reason_codes: List[str]
    requires_manager_approval: bool = False
    peer_frequency: Optional[int] = None


class BlockedSystem(BaseModel):
    system: str
    reason_codes: List[str]


class AccessRecommendationResponse(BaseModel):
    employee_id: str
    role: str
    level: str
    recommendations: List[AccessRecommendation]
    blocked_systems: List[BlockedSystem]
    policy_version: str


class SelectAccessRequest(BaseModel):
    employee_id: str
    selected_systems: List[str]
    correlation_id: str
    source: str = "n8n-demo"


class SelectAccessResponse(BaseModel):
    ok: bool = True
    status: str = "EMPLOYEE_SELECTED"
    employee_id: str
    request_id: str
    selected_systems: List[str]
    correlation_id: str
    next_action: str = "REQUEST_MANAGER_APPROVAL"


class CreateApprovalRequest(BaseModel):
    employee_id: str
    request_id: str
    manager_id: str
    correlation_id: str


class ApprovalDecisionRequest(BaseModel):
    decided_by: str
    decision_reason: str
    correlation_id: str


class ApprovalResponse(BaseModel):
    ok: bool = True
    status: str
    approval_status: str
    approval_is_approved: bool = False
    approval_id: str
    request_id: str
    employee_id: str
    manager_id: str
    correlation_id: str
    next_action: str


class CreateTicketRequest(BaseModel):
    employee_id: str
    approval_id: str
    requested_systems: List[str]
    requested_by: str = "hr-onboarding-agent"
    idempotency_key: Optional[str] = None
    correlation_id: str
    simulate_failure: bool = False


class TicketResponse(BaseModel):
    ok: bool
    status: str
    ticket_id: Optional[str] = None
    request_id: Optional[str] = None
    approval_id: Optional[str] = None
    employee_id: Optional[str] = None
    requested_systems: Optional[List[str]] = None
    ticket_created: bool = False
    duplicate: bool = False
    pre_approval_blocked: bool = False
    correlation_id: Optional[str] = None
    error_code: Optional[str] = None
    reason_code: Optional[str] = None
    message: Optional[str] = None
    recoverable: Optional[bool] = None
    next_action: Optional[str] = None


class SlackMessageRequest(BaseModel):
    channel_or_user: Optional[str] = None
    channel: Optional[str] = None
    message_type: str
    message: str
    metadata: Optional[Dict[str, Any]] = None
    simulate_failure: bool = False


class SlackMessageResponse(BaseModel):
    ok: bool = True
    status: str = "STORED"
    message_id: str
    correlation_id: Optional[str] = None


class LLMMessageRequest(BaseModel):
    message_type: str
    employee_id: str
    correlation_id: str
    llm_boundary: str = "communication_only"
    context: Optional[Dict[str, Any]] = None


class LLMMessageResponse(BaseModel):
    ok: bool = True
    status: str = "GENERATED"
    message: str
    generated_message: str
    llm_provider: str
    fallback_used: bool
    correlation_id: str


class OnboardingQuestionRequest(BaseModel):
    employee_id: str
    question: str
    correlation_id: str


class OnboardingQuestionResponse(BaseModel):
    ok: bool
    status: str
    employee_id: Optional[str] = None
    answer: Optional[str] = None
    source: Optional[str] = None
    correlation_id: Optional[str] = None
    error_code: Optional[str] = None
    message: Optional[str] = None


class AuditEventOut(BaseModel):
    event_id: int
    correlation_id: str
    employee_id: Optional[str] = None
    actor_type: str
    actor_id: Optional[str] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    status: str
    reason_code: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class AuditEventsResponse(BaseModel):
    ok: bool = True
    events: List[AuditEventOut]
    count: int
    limit: int = 100
    offset: int = 0


class OnboardingStatusResponse(BaseModel):
    employee_id: str
    status: str
    correlation_id: Optional[str] = None
    created_at: Optional[str] = None
    session_id: Optional[int] = None


class OnboardingStartRequest(BaseModel):
    correlation_id: str
