from fastapi import APIRouter
from app.schemas import ResponseBuildRequest
from app.services.response_builder import build_response

router = APIRouter(prefix="/api/v1/responses", tags=["responses"])


@router.post("/build")
def responses_build(payload: ResponseBuildRequest):
    return build_response(
        reply_type=payload.reply_type,
        message=payload.message,
        buttons=payload.buttons,
        list_sections=payload.list_sections
    )