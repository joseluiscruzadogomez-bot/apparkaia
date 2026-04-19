def get_ticket_status(ticket_code: str, user_phone: str, site_id: str | None = None) -> dict:
    ticket_code = (ticket_code or "").upper()

    if ticket_code == "TK404":
        return {
            "success": False,
            "error_code": "TICKET_NOT_FOUND",
            "message": "No se encontró el ticket.",
        }

    if ticket_code == "TKPAID":
        return {
            "success": True,
            "ticket_id": "TCK_PAID_001",
            "ticket_code": ticket_code,
            "status": "paid",
            "amount_due": 0,
            "currency": "PEN",
            "entry_time": "2026-04-18T08:15:00-05:00",
            "exit_time": None,
            "site_id": site_id or "SITE_001",
            "site_name": "Apparka Miraflores",
            "lane_id": "EXIT_02",
            "can_exit": True,
            "payment_url": None,
            "support_required": False,
            "message": "Ticket pagado",
        }

    if ticket_code == "TKSUPPORT":
        return {
            "success": True,
            "ticket_id": "TCK_SUPPORT_001",
            "ticket_code": ticket_code,
            "status": "paid",
            "amount_due": 0,
            "currency": "PEN",
            "entry_time": "2026-04-18T08:15:00-05:00",
            "exit_time": None,
            "site_id": site_id or "SITE_001",
            "site_name": "Apparka Miraflores",
            "lane_id": "EXIT_02",
            "can_exit": True,
            "payment_url": None,
            "support_required": True,
            "message": "Ticket pagado, requiere soporte",
        }

    return {
        "success": True,
        "ticket_id": "TCK_PENDING_001",
        "ticket_code": ticket_code,
        "status": "pending_payment",
        "amount_due": 12.50,
        "currency": "PEN",
        "entry_time": "2026-04-18T08:15:00-05:00",
        "exit_time": None,
        "site_id": site_id or "SITE_001",
        "site_name": "Apparka Miraflores",
        "lane_id": "EXIT_02",
        "can_exit": False,
        "payment_url": "https://pagos.apparkaia.com/pay/TK123456",
        "support_required": False,
        "message": "Ticket pendiente de pago",
    }


def get_ticket_debt(ticket_code: str, user_phone: str, site_id: str | None = None) -> dict:
    data = get_ticket_status(ticket_code, user_phone, site_id)
    if not data.get("success"):
        return data

    return {
        "success": True,
        "ticket_code": ticket_code,
        "amount_due": data.get("amount_due", 0),
        "currency": data.get("currency", "PEN"),
        "message": "Consulta de deuda realizada correctamente",
    }


def get_ticket_time(ticket_code: str, user_phone: str, site_id: str | None = None) -> dict:
    if ticket_code == "TK404":
        return {
            "success": False,
            "error_code": "TICKET_NOT_FOUND",
            "message": "No se encontró el ticket.",
        }

    return {
        "success": True,
        "ticket_code": ticket_code,
        "minutes_parked": 135,
        "formatted_time": "2 horas y 15 minutos",
        "message": "Consulta de tiempo realizada correctamente",
    }


def get_payment_link(ticket_code: str, user_phone: str, site_id: str | None = None) -> dict:
    if ticket_code == "TK404":
        return {
            "success": False,
            "error_code": "TICKET_NOT_FOUND",
            "message": "No se encontró el ticket.",
        }

    return {
        "success": True,
        "ticket_code": ticket_code,
        "payment_url": f"https://pagos.apparkaia.com/pay/{ticket_code}",
        "message": "Link de pago generado correctamente",
    }


def create_support_case(ticket_code: str, category: str) -> dict:
    return {
        "success": True,
        "case_id": "CASE_001",
        "ticket_code": ticket_code,
        "category": category,
        "message": "Caso de soporte creado correctamente",
    }