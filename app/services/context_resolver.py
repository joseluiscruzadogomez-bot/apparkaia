from app.services.session_manager import update_session, get_session
from app.constants import CONVERSATION_STATES, FLOW_ORIGINS


def resolve_context(session_id: str, intent: str, flow_origin: str, user_phone: str, qr_context=None, text=None) -> dict:
    session = get_session(session_id)
    if not session:
        return {
            "context_status": "session_not_found",
            "required_fields": [],
            "next_state": CONVERSATION_STATES["error_recovery"],
        }

    # 1. Resolver contexto QR según ref
    if qr_context and qr_context.get("ref"):
        ref = str(qr_context.get("ref")).strip().lower()

        qr_map = {
            "abc123": {
                "ticket_id": "TCK_001",
                "ticket_code": "TK123456",
                "site_id": "SITE_001",
                "site_name": "Apparka Miraflores",
                "lane_id": "EXIT_02",
            },
            "paid001": {
                "ticket_id": "TCK_PAID_001",
                "ticket_code": "TKPAID",
                "site_id": "SITE_001",
                "site_name": "Apparka Miraflores",
                "lane_id": "EXIT_01",
            },
            "help001": {
                "ticket_id": "TCK_SUPPORT_001",
                "ticket_code": "TKSUPPORT",
                "site_id": "SITE_001",
                "site_name": "Apparka Miraflores",
                "lane_id": "EXIT_03",
            },
        }

        qr_data = qr_map.get(ref)

        if qr_data:
            updates = {
                "flow_origin": FLOW_ORIGINS["qr_exit"],
                "ticket_id": qr_data["ticket_id"],
                "ticket_code": qr_data["ticket_code"],
                "site_id": qr_data["site_id"],
                "site_name": qr_data["site_name"],
                "lane_id": qr_data["lane_id"],
                "context_prevalidated": True,
                "conversation_state": CONVERSATION_STATES["ticket_identified"],
                "last_intent": intent,
            }
            update_session(session_id, updates)

            return {
                "context_status": "resolved",
                "ticket_id": qr_data["ticket_id"],
                "ticket_code": qr_data["ticket_code"],
                "site_id": qr_data["site_id"],
                "site_name": qr_data["site_name"],
                "lane_id": qr_data["lane_id"],
                "next_state": CONVERSATION_STATES["ticket_identified"],
            }

        return {
            "context_status": "invalid_qr_ref",
            "required_fields": [],
            "next_state": CONVERSATION_STATES["error_recovery"],
        }

    # 2. Resolver ticket escrito manualmente
    cleaned_text = (text or "").strip().upper()
    if cleaned_text.startswith("TK"):
        updates = {
            "ticket_code": cleaned_text,
            "conversation_state": CONVERSATION_STATES["ticket_identified"],
            "last_intent": intent,
        }
        update_session(session_id, updates)

        return {
            "context_status": "resolved",
            "ticket_code": cleaned_text,
            "next_state": CONVERSATION_STATES["ticket_identified"],
        }

    # 3. Reusar ticket existente en sesión
    if session.get("ticket_code"):
        return {
            "context_status": "resolved",
            "ticket_code": session["ticket_code"],
            "next_state": CONVERSATION_STATES["ticket_identified"],
        }

    # 4. Falta ticket
    return {
        "context_status": "missing_ticket",
        "required_fields": ["ticket_code"],
        "next_state": CONVERSATION_STATES["awaiting_ticket_code"],
    }