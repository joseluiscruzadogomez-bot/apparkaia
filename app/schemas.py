from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class IncomingMessage(BaseModel):
    channel: str = "whatsapp"
    from_phone: str = Field(..., alias="from")
    message_type: str = "text"
    text: Optional[str] = None
    interactive: Optional[Dict[str, Any]] = None
    attachments: List[Dict[str, Any]] = []
    qr_context: Optional[Dict[str, Any]] = None


class NormalizedMessage(BaseModel):
    message_id: str
    channel: str
    user_phone: str
    message_type: str
    text: Optional[str]
    interactive: Optional[Dict[str, Any]]
    attachments: List[Dict[str, Any]]
    qr_context: Optional[Dict[str, Any]]
    received_at: str


class SessionRequest(BaseModel):
    user_phone: str
    channel: str = "whatsapp"


class SessionModel(BaseModel):
    session_id: str
    user_phone: str
    channel: str
    flow_origin: str
    conversation_state: str
    ticket_id: Optional[str] = None
    ticket_code: Optional[str] = None
    site_id: Optional[str] = None
    site_name: Optional[str] = None
    lane_id: Optional[str] = None
    last_intent: Optional[str] = None
    last_backend_status: Optional[str] = None
    context_prevalidated: bool = False
    created_at: str
    updated_at: str


class IntentRequest(BaseModel):
    text: Optional[str] = ""
    conversation_state: str
    flow_origin: str


class IntentResponse(BaseModel):
    intent: str
    confidence: float
    requires_ticket_context: bool
    requires_human: bool


class ContextResolveRequest(BaseModel):
    session_id: str
    intent: str
    flow_origin: str
    user_phone: str
    qr_context: Optional[Dict[str, Any]] = None
    text: Optional[str] = None


class BackendTicketRequest(BaseModel):
    ticket_code: str
    user_phone: str
    site_id: Optional[str] = None


class ResponseBuildRequest(BaseModel):
    reply_type: str
    message: str
    buttons: List[Dict[str, str]] = []
    list_sections: List[Dict[str, Any]] = []


class OutgoingTestRequest(BaseModel):
    to: str
    payload: Dict[str, Any]


class ConversationNextRequest(BaseModel):
    session: Dict[str, Any]
    intent: str
    backend_result: Optional[Dict[str, Any]] = None