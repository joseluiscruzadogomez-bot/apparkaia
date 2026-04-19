from fastapi import APIRouter
from app.schemas import OutgoingTestRequest

router = APIRouter(prefix="/api/v1/outgoing", tags=["outgoing"])


@router.post("/test")
def outgoing_test(payload: OutgoingTestRequest):
    return {
        "sent": True,
        "mode": "simulation",
        "preview": {
            "to": payload.to,
            "payload": payload.payload
        }
    }