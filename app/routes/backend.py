from fastapi import APIRouter
from app.schemas import BackendTicketRequest
from app.services.backend_adapter import (
    get_ticket_status,
    get_ticket_debt,
    get_ticket_time,
    get_payment_link,
    create_support_case
)

router = APIRouter(prefix="/api/v1/backend", tags=["backend"])


@router.post("/ticket/status")
def ticket_status(payload: BackendTicketRequest):
    return get_ticket_status(payload.ticket_code, payload.user_phone, payload.site_id)


@router.post("/ticket/debt")
def ticket_debt(payload: BackendTicketRequest):
    return get_ticket_debt(payload.ticket_code, payload.user_phone, payload.site_id)


@router.post("/ticket/time")
def ticket_time(payload: BackendTicketRequest):
    return get_ticket_time(payload.ticket_code, payload.user_phone, payload.site_id)


@router.post("/ticket/payment-link")
def ticket_payment_link(payload: BackendTicketRequest):
    return get_payment_link(payload.ticket_code, payload.user_phone, payload.site_id)


@router.post("/support/create")
def support_create(payload: dict):
    ticket_code = payload.get("ticket_code", "")
    category = payload.get("category", "general")
    return create_support_case(ticket_code, category)