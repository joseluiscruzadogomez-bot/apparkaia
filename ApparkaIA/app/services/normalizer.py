from datetime import datetime
from uuid import uuid4


def normalize_message(payload: dict) -> dict:
    message_type = payload.get("message_type", "text")
    interactive = payload.get("interactive")
    text = payload.get("text")

    # Si viene interacción tipo botón o lista, convertimos el id en texto utilizable
    if message_type == "interactive" and interactive:
        interactive_type = interactive.get("type")

        if interactive_type == "button_reply":
            button_reply = interactive.get("button_reply", {})
            text = button_reply.get("id") or button_reply.get("title")

        elif interactive_type == "list_reply":
            list_reply = interactive.get("list_reply", {})
            text = list_reply.get("id") or list_reply.get("title")

    return {
        "message_id": f"msg_{uuid4().hex[:8]}",
        "channel": payload.get("channel", "whatsapp"),
        "user_phone": payload.get("from"),
        "message_type": message_type,
        "text": text,
        "interactive": interactive,
        "attachments": payload.get("attachments", []),
        "qr_context": payload.get("qr_context"),
        "received_at": datetime.now().isoformat(),
    }