from fastapi import APIRouter, HTTPException, Query, Request

from app.config import WHATSAPP_VERIFY_TOKEN
from app.services.normalizer import normalize_message
from app.services.session_manager import get_or_create_session, get_session, update_session
from app.services.intent_classifier import classify_intent
from app.services.context_resolver import resolve_context
from app.services.backend_adapter import (
    get_ticket_status,
    get_ticket_debt,
    get_ticket_time,
    get_payment_link,
    create_support_case,
)
from app.services.conversation_engine import get_next_response
from app.services.response_builder import build_response
from app.services.whatsapp_sender import send_whatsapp_message
from app.database import MESSAGES_DB

router = APIRouter(tags=["webhook"])


def extract_whatsapp_message(value: dict) -> dict | None:
    messages = value.get("messages", [])
    if not messages:
        return None

    contacts = value.get("contacts", [])
    wa_from = messages[0].get("from")
    profile_name = None

    if contacts:
        profile_name = contacts[0].get("profile", {}).get("name")

    msg = messages[0]
    msg_type = msg.get("type", "text")

    payload = {
        "channel": "whatsapp",
        "from": wa_from,
        "message_type": msg_type,
        "text": None,
        "interactive": None,
        "attachments": [],
        "qr_context": None,
        "profile_name": profile_name,
        "wamid": msg.get("id"),
    }

    if msg_type == "text":
        payload["text"] = msg.get("text", {}).get("body")

    elif msg_type == "interactive":
        interactive = msg.get("interactive", {})
        interactive_type = interactive.get("type")

        if interactive_type == "button_reply":
            payload["interactive"] = {
                "type": "button_reply",
                "button_reply": {
                    "id": interactive.get("button_reply", {}).get("id"),
                    "title": interactive.get("button_reply", {}).get("title"),
                },
            }

        elif interactive_type == "list_reply":
            payload["interactive"] = {
                "type": "list_reply",
                "list_reply": {
                    "id": interactive.get("list_reply", {}).get("id"),
                    "title": interactive.get("list_reply", {}).get("title"),
                    "description": interactive.get("list_reply", {}).get("description"),
                },
            }

    elif msg_type == "image":
        payload["attachments"] = [{
            "type": "image",
            "id": msg.get("image", {}).get("id"),
            "mime_type": msg.get("image", {}).get("mime_type"),
            "caption": msg.get("image", {}).get("caption"),
        }]

    elif msg_type == "document":
        payload["attachments"] = [{
            "type": "document",
            "id": msg.get("document", {}).get("id"),
            "mime_type": msg.get("document", {}).get("mime_type"),
            "filename": msg.get("document", {}).get("filename"),
            "caption": msg.get("document", {}).get("caption"),
        }]

    elif msg_type == "audio":
        payload["attachments"] = [{
            "type": "audio",
            "id": msg.get("audio", {}).get("id"),
            "mime_type": msg.get("audio", {}).get("mime_type"),
        }]

    elif msg_type == "video":
        payload["attachments"] = [{
            "type": "video",
            "id": msg.get("video", {}).get("id"),
            "mime_type": msg.get("video", {}).get("mime_type"),
            "caption": msg.get("video", {}).get("caption"),
        }]

    return payload


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)

    raise HTTPException(status_code=403, detail="Token de verificación inválido")


@router.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.json()

    entries = body.get("entry", [])
    if not entries:
        return {"ok": True, "message": "No entry data"}

    processed_events = []

    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})

            if value.get("statuses"):
                processed_events.append({
                    "event_type": "status",
                    "statuses": value.get("statuses", [])
                })
                continue

            incoming_payload = extract_whatsapp_message(value)
            if not incoming_payload:
                processed_events.append({
                    "event_type": "ignored",
                    "reason": "No se encontraron mensajes manejables"
                })
                continue

            normalized = normalize_message(incoming_payload)
            MESSAGES_DB[normalized["message_id"]] = normalized

            session = get_or_create_session(
                user_phone=normalized["user_phone"],
                channel=normalized["channel"]
            )

            qr_context = normalized.get("qr_context") or {}
            has_qr_ref = bool(qr_context.get("ref"))
            raw_text = (normalized.get("text") or "").strip().upper()

            if has_qr_ref:
                update_session(session["session_id"], {"flow_origin": "qr_exit"})
                session = get_session(session["session_id"])

            current_state = session.get("conversation_state", "awaiting_intent")
            previous_intent = session.get("last_intent")

            if has_qr_ref:
                intent_result = {
                    "intent": "exit_problem",
                    "confidence": 0.99,
                    "requires_ticket_context": True,
                    "requires_human": False,
                }
                intent = "exit_problem"
            else:
                intent_result = classify_intent(
                    text=normalized.get("text"),
                    conversation_state=current_state,
                    flow_origin=session.get("flow_origin", "direct_whatsapp")
                )
                intent = intent_result["intent"]

                if current_state == "awaiting_ticket_code" and raw_text.startswith("TK"):
                    if previous_intent in [
                        "pay_ticket",
                        "check_status",
                        "check_debt",
                        "check_time",
                        "exit_problem",
                        "send_payment_link",
                    ]:
                        intent = previous_intent
                        intent_result["intent"] = previous_intent
                        intent_result["confidence"] = 0.99
                        intent_result["requires_ticket_context"] = True
                        intent_result["requires_human"] = False

            update_session(session["session_id"], {"last_intent": intent})
            session = get_session(session["session_id"])

            context_result = resolve_context(
                session_id=session["session_id"],
                intent=intent,
                flow_origin=session.get("flow_origin", "direct_whatsapp"),
                user_phone=normalized["user_phone"],
                qr_context=qr_context,
                text=normalized.get("text")
            )

            session = get_session(session["session_id"])

            backend_result = None
            ticket_code = context_result.get("ticket_code") or session.get("ticket_code")
            site_id = session.get("site_id")

            if context_result.get("context_status") == "resolved" and ticket_code:
                if intent in ["pay_ticket", "check_status", "exit_problem", "send_payment_link"]:
                    backend_result = get_ticket_status(
                        ticket_code=ticket_code,
                        user_phone=normalized["user_phone"],
                        site_id=site_id
                    )
                elif intent == "check_debt":
                    backend_result = get_ticket_debt(
                        ticket_code=ticket_code,
                        user_phone=normalized["user_phone"],
                        site_id=site_id
                    )
                elif intent == "check_time":
                    backend_result = get_ticket_time(
                        ticket_code=ticket_code,
                        user_phone=normalized["user_phone"],
                        site_id=site_id
                    )
                elif intent == "pay_ticket_link":
                    backend_result = get_payment_link(
                        ticket_code=ticket_code,
                        user_phone=normalized["user_phone"],
                        site_id=site_id
                    )

                if backend_result and backend_result.get("status"):
                    update_session(
                        session["session_id"],
                        {"last_backend_status": backend_result.get("status")}
                    )
                    session = get_session(session["session_id"])

            final_decision = get_next_response(
                session=session,
                intent=intent,
                backend_result=backend_result
            )

            action_results = []
            for action in final_decision.get("actions", []):
                action_type = action.get("type")
                action_payload = action.get("payload", {})

                if action_type == "create_support_case":
                    support_result = create_support_case(
                        ticket_code=action_payload.get("ticket_code", ""),
                        category=action_payload.get("category", "general")
                    )
                    action_results.append({
                        "type": action_type,
                        "result": support_result
                    })

            update_session(
                session["session_id"],
                {
                    "conversation_state": final_decision.get(
                        "next_state",
                        session["conversation_state"]
                    )
                }
            )
            session = get_session(session["session_id"])

            final_response = build_response(
                reply_type=final_decision.get("reply_type", "text"),
                message=final_decision.get("message", ""),
                buttons=final_decision.get("buttons", []),
                list_sections=final_decision.get("list_sections", [])
            )

            send_result = send_whatsapp_message(
                to=normalized["user_phone"],
                final_response=final_response
            )

            processed_events.append({
                "event_type": "message",
                "normalized_message": normalized,
                "session": session,
                "intent": intent_result,
                "context": context_result,
                "backend_result": backend_result,
                "decision": final_decision,
                "action_results": action_results,
                "final_response": final_response,
                "send_result": send_result,
            })

    return {
        "ok": True,
        "processed_events": processed_events
    }