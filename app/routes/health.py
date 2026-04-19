from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "ok": True,
        "service": "apparkaia-orchestrator",
        "version": "1.0.0"
    }