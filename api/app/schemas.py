from pydantic import BaseModel
from typing import List, Optional

class ModuleStatus(BaseModel):
    module_id: str
    status: str

class TrainingStatusResponse(BaseModel):
    employee_id: str
    modules: List[ModuleStatus]

class EmployeeResponse(BaseModel):
    employee_id: str
    name: str
    email: str
    role: str
    level: str
    department: str
    manager_id: Optional[str]
    start_date: str
    employment_status: str

class RecommendationItem(BaseModel):
    system: str
    recommendation_type: str
    reason_codes: List[str]
    requires_manager_approval: bool
    peer_frequency: Optional[int]

class BlockedSystemItem(BaseModel):
    system: str
    reason_codes: List[str]

class AccessRecommendationResponse(BaseModel):
    employee_id: str
    role: str
    level: str
    recommendations: List[RecommendationItem]
    blocked_systems: List[BlockedSystemItem]
    policy_version: str

class AccessSelectionRequest(BaseModel):
    employee_id: str
    selected_systems: List[str]
    correlation_id: str
    source: str = "n8n-demo"

class AccessSelectionResponse(BaseModel):
    request_id: int
    employee_id: str
    selected_systems: List[str]
    status: str
    approval_id: Optional[str] = None

class ApprovalCreate(BaseModel):
    employee_id: str
    request_id: int
    manager_id: str
    correlation_id: str

from datetime import datetime

class ApprovalResponse(BaseModel):
    approval_id: str
    request_id: int
    employee_id: str
    manager_id: str
    status: str
    decision_reason: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None

class TicketRequest(BaseModel):
    employee_id: str
    approval_id: str
    requested_systems: List[str]
    requested_by: str
    idempotency_key: str
    correlation_id: str

class TicketResponse(BaseModel):
    ticket_id: Optional[str] = None
    status: str
    created: bool = False
    error: Optional[str] = None

from typing import Dict, Any

class LLMMessageRequest(BaseModel):
    message_type: str
    employee_id: str
    correlation_id: str
    context: Optional[Dict[str, Any]] = None
    llm_boundary: str = "communication_only"

class LLMMessageResponse(BaseModel):
    message: str
    message_type: str
    generated_by: str

class OnboardingStartRequest(BaseModel):
    correlation_id: str

class SlackMessageRequest(BaseModel):
    channel_or_user: str
    message_type: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

class SlackMessageResponse(BaseModel):
    message_id: int
    status: str = "stored"
