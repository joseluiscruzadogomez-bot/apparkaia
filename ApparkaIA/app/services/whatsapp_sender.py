import requests

from app.config import (
    WHATSAPP_API_VERSION,
    WHATSAPP_PHONE_NUMBER_ID,
    WHATSAPP_ACCESS_TOKEN,
    WHATSAPP_SEND_REAL_MESSAGES,
)


def _build_meta_text_payload(to: str, body: str) -> dict:
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": body
        }
    }


def _build_meta_buttons_payload(to: str, body: str, buttons: list[dict]) -> dict:
    # Meta admite hasta 3 reply buttons
    meta_buttons = []
    for btn in buttons[:3]:
        meta_buttons.append({
            "type": "reply",
            "reply": {
                "id": btn.get("id", ""),
                "title": btn.get("title", "")[:20]
            }
        })

    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body
            },
            "action": {
                "buttons": meta_buttons
            }
        }
    }


def convert_final_response_to_meta_payload(to: str, final_response: dict) -> dict:
    payload = final_response.get("payload", {})
    payload_type = payload.get("type")

    if payload_type == "text":
        return _build_meta_text_payload(
            to=to,
            body=payload.get("body", "")
        )

    if payload_type == "interactive" and payload.get("interactive_type") == "button":
        return _build_meta_buttons_payload(
            to=to,
            body=payload.get("body", ""),
            buttons=payload.get("buttons", [])
        )

    # Fallback a texto
    return _build_meta_text_payload(
        to=to,
        body=payload.get("body", "Mensaje sin contenido")
    )


def send_whatsapp_message(to: str, final_response: dict) -> dict:
    meta_payload = convert_final_response_to_meta_payload(to, final_response)

    if not WHATSAPP_SEND_REAL_MESSAGES:
        return {
            "success": True,
            "mode": "simulation",
            "meta_payload": meta_payload
        }

    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=meta_payload, timeout=30)

    try:
        response_json = response.json()
    except Exception:
        response_json = {"raw_text": response.text}

    return {
        "success": response.ok,
        "mode": "real",
        "status_code": response.status_code,
        "meta_payload": meta_payload,
        "meta_response": response_json
    }