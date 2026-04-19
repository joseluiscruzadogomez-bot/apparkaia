INTENTS = {
    "greeting": "greeting",
    "pay_ticket": "pay_ticket",
    "check_status": "check_status",
    "check_debt": "check_debt",
    "check_time": "check_time",
    "exit_problem": "exit_problem",
    "lost_ticket": "lost_ticket",
    "support": "support",
    "human_agent": "human_agent",
    "unknown": "unknown",
}

CONVERSATION_STATES = {
    "new": "new",
    "awaiting_intent": "awaiting_intent",
    "awaiting_ticket_code": "awaiting_ticket_code",
    "awaiting_plate": "awaiting_plate",
    "awaiting_phone_validation": "awaiting_phone_validation",
    "ticket_identified": "ticket_identified",
    "awaiting_backend_response": "awaiting_backend_response",
    "awaiting_payment_confirmation": "awaiting_payment_confirmation",
    "payment_link_sent": "payment_link_sent",
    "awaiting_support_confirmation": "awaiting_support_confirmation",
    "support_case_opened": "support_case_opened",
    "resolved": "resolved",
    "handoff_to_human": "handoff_to_human",
    "error_recovery": "error_recovery",
    "closed": "closed",
}

FLOW_ORIGINS = {
    "direct_whatsapp": "direct_whatsapp",
    "qr_exit": "qr_exit",
    "qr_payment": "qr_payment",
    "unknown": "unknown",
}