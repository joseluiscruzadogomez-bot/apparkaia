from app.constants import CONVERSATION_STATES


def get_next_response(session: dict, intent: str, backend_result: dict | None = None) -> dict:
    if intent == "greeting":
        return {
            "reply_type": "buttons",
            "message": "Hola, soy Apparkaia. Te ayudo con tu ticket de estacionamiento. Elige una opción:",
            "buttons": [
                {"id": "pay_ticket", "title": "Pagar"},
                {"id": "check_status", "title": "Ver estado"},
                {"id": "exit_problem", "title": "Problema en salida"},
            ],
            "actions": [],
            "next_state": CONVERSATION_STATES["awaiting_intent"],
        }

    if intent in ["human_agent", "support", "lost_ticket"]:
        return {
            "reply_type": "text",
            "message": "Voy a derivar tu caso a soporte para ayudarte lo antes posible.",
            "actions": [],
            "next_state": CONVERSATION_STATES["handoff_to_human"],
        }

    if not backend_result:
        return {
            "reply_type": "text",
            "message": "Necesito más información para ayudarte. Envíame tu código de ticket.",
            "actions": [],
            "next_state": CONVERSATION_STATES["awaiting_ticket_code"],
        }

    if not backend_result.get("success"):
        return {
            "reply_type": "text",
            "message": "No pude encontrar ese ticket. Verifica el código o solicita soporte.",
            "actions": [],
            "next_state": CONVERSATION_STATES["awaiting_ticket_code"],
        }

    status = backend_result.get("status")
    amount_due = backend_result.get("amount_due", 0)
    payment_url = backend_result.get("payment_url")
    ticket_code = backend_result.get("ticket_code")
    if intent == "send_payment_link":
        if not backend_result:
            return {
                "reply_type": "text",
                "message": "Necesito tu ticket para enviarte el link de pago.",
                "actions": [],
                "next_state": CONVERSATION_STATES["awaiting_ticket_code"],
            }

        if not backend_result.get("success"):
            return {
                "reply_type": "text",
                "message": "No pude encontrar ese ticket. Verifica el código o solicita soporte.",
                "actions": [],
                "next_state": CONVERSATION_STATES["awaiting_ticket_code"],
            }

        amount_due = backend_result.get("amount_due", 0)
        payment_url = backend_result.get("payment_url")
        ticket_code = backend_result.get("ticket_code")

        if amount_due > 0 and payment_url:
            return {
                "reply_type": "text",
                "message": f"Aquí tienes tu link de pago para el ticket {ticket_code}: {payment_url}",
                "actions": [],
                "next_state": CONVERSATION_STATES["payment_link_sent"],
            }

        return {
            "reply_type": "text",
            "message": "Tu ticket no registra deuda pendiente.",
            "actions": [],
            "next_state": CONVERSATION_STATES["resolved"],
        }
    if intent == "pay_ticket":
        if amount_due > 0 and payment_url:
            return {
                "reply_type": "buttons",
                "message": f"Tu ticket registra una deuda de S/ {amount_due:.2f}. ¿Deseas que te envíe el link de pago?",
                "buttons": [
                    {"id": "send_payment_link", "title": "Sí, enviar link"},
                    {"id": "support", "title": "Necesito ayuda"},
                ],
                "actions": [],
                "next_state": CONVERSATION_STATES["awaiting_payment_confirmation"],
            }

        return {
            "reply_type": "text",
            "message": "Tu ticket no registra deuda pendiente.",
            "actions": [],
            "next_state": CONVERSATION_STATES["resolved"],
        }

    if intent == "check_status":
        return {
            "reply_type": "text",
            "message": f"El estado de tu ticket {ticket_code} es: {status}.",
            "actions": [],
            "next_state": CONVERSATION_STATES["resolved"],
        }

    if intent == "check_debt":
        return {
            "reply_type": "text",
            "message": f"Tu ticket registra una deuda de S/ {amount_due:.2f}.",
            "actions": [],
            "next_state": CONVERSATION_STATES["resolved"],
        }

    if intent == "check_time":
        formatted = backend_result.get("formatted_time", "No disponible")
        return {
            "reply_type": "text",
            "message": f"Tu tiempo de permanencia es {formatted}.",
            "actions": [],
            "next_state": CONVERSATION_STATES["resolved"],
        }

    if intent == "exit_problem":
        if status == "paid" and backend_result.get("can_exit"):
            return {
                "reply_type": "text",
                "message": "Tu ticket ya figura como pagado. Estoy registrando tu caso para soporte inmediato en salida.",
                "actions": [
                    {
                        "type": "create_support_case",
                        "payload": {
                            "ticket_code": ticket_code,
                            "category": "exit_barrier_not_opening",
                        },
                    }
                ],
                "next_state": CONVERSATION_STATES["support_case_opened"],
            }

        if amount_due > 0:
            return {
                "reply_type": "text",
                "message": f"Tu ticket aún tiene un pago pendiente de S/ {amount_due:.2f}. Puedo enviarte el link de pago.",
                "actions": [],
                "next_state": CONVERSATION_STATES["awaiting_payment_confirmation"],
            }

    return {
        "reply_type": "text",
        "message": "No pude determinar la mejor acción. Te recomiendo contactar a soporte.",
        "actions": [],
        "next_state": CONVERSATION_STATES["error_recovery"],
    }