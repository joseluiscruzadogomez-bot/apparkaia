from app.constants import INTENTS


def classify_intent(text: str | None, conversation_state: str, flow_origin: str) -> dict:
    normalized = (text or "").strip().lower()

    if not normalized:
        return {
            "intent": INTENTS["unknown"],
            "confidence": 0.20,
            "requires_ticket_context": False,
            "requires_human": False,
        }

    if normalized in ["pay_ticket", "pagar"]:
        return {
            "intent": INTENTS["pay_ticket"],
            "confidence": 0.99,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    if normalized in ["check_status", "ver estado"]:
        return {
            "intent": INTENTS["check_status"],
            "confidence": 0.99,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    if normalized in ["exit_problem", "problema en salida"]:
        return {
            "intent": INTENTS["exit_problem"],
            "confidence": 0.99,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    if normalized in ["send_payment_link", "enviar link", "sí", "si"]:
        return {
            "intent": "send_payment_link",
            "confidence": 0.98,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    if normalized in ["support", "necesito ayuda", "soporte", "ayuda", "asesor"]:
        return {
            "intent": INTENTS["support"],
            "confidence": 0.95,
            "requires_ticket_context": False,
            "requires_human": True,
        }

    if "apparkaia ref" in normalized or normalized.startswith("ref "):
        return {
            "intent": INTENTS["exit_problem"],
            "confidence": 0.98,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    if any(word in normalized for word in ["hola", "buenas", "buenos días", "buenas tardes"]):
        return {
            "intent": INTENTS["greeting"],
            "confidence": 0.95,
            "requires_ticket_context": False,
            "requires_human": False,
        }

    if any(word in normalized for word in ["pagar", "pago", "link de pago"]):
        return {
            "intent": INTENTS["pay_ticket"],
            "confidence": 0.95,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    if any(word in normalized for word in ["estado", "ver estado"]):
        return {
            "intent": INTENTS["check_status"],
            "confidence": 0.92,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    if any(word in normalized for word in ["deuda", "debo", "cuánto debo", "cuanto debo"]):
        return {
            "intent": INTENTS["check_debt"],
            "confidence": 0.92,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    if any(word in normalized for word in ["tiempo", "cuánto tiempo", "cuanto tiempo", "horas"]):
        return {
            "intent": INTENTS["check_time"],
            "confidence": 0.90,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    if any(word in normalized for word in ["barrera", "no abre", "salida", "no puedo salir"]):
        return {
            "intent": INTENTS["exit_problem"],
            "confidence": 0.96,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    if any(word in normalized for word in ["perdí", "perdi", "ticket perdido"]):
        return {
            "intent": INTENTS["lost_ticket"],
            "confidence": 0.90,
            "requires_ticket_context": False,
            "requires_human": True,
        }

    if any(word in normalized for word in ["humano", "persona", "agente"]):
        return {
            "intent": INTENTS["human_agent"],
            "confidence": 0.95,
            "requires_ticket_context": False,
            "requires_human": True,
        }

    if normalized.startswith("tk"):
        return {
            "intent": INTENTS["check_status"],
            "confidence": 0.80,
            "requires_ticket_context": True,
            "requires_human": False,
        }

    return {
        "intent": INTENTS["unknown"],
        "confidence": 0.40,
        "requires_ticket_context": False,
        "requires_human": False,
    }