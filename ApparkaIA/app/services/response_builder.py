def build_response(reply_type: str, message: str, buttons=None, list_sections=None) -> dict:
    buttons = buttons or []
    list_sections = list_sections or []

    if reply_type == "text":
        return {
            "channel": "whatsapp",
            "payload": {
                "type": "text",
                "body": message,
            }
        }

    if reply_type == "buttons":
        return {
            "channel": "whatsapp",
            "payload": {
                "type": "interactive",
                "interactive_type": "button",
                "body": message,
                "buttons": buttons,
            }
        }

    if reply_type == "list":
        return {
            "channel": "whatsapp",
            "payload": {
                "type": "interactive",
                "interactive_type": "list",
                "body": message,
                "sections": list_sections,
            }
        }

    return {
        "channel": "whatsapp",
        "payload": {
            "type": "text",
            "body": message,
        }
    }