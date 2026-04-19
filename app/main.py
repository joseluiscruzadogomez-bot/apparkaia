from fastapi import FastAPI
from app.config import APP_NAME, APP_VERSION
from app.routes.health import router as health_router
from app.routes.incoming import router as incoming_router
from app.routes.sessions import router as sessions_router
from app.routes.conversation import router as conversation_router
from app.routes.backend import router as backend_router
from app.routes.responses import router as responses_router
from app.routes.outgoing import router as outgoing_router
from app.routes.orchestrator import router as orchestrator_router
from app.routes.webhook import router as webhook_router

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="MVP Apparkaia para pruebas modulares en Postman"
)
@app.get("/")
def root():
    return {
        "message": "Apparkaia MVP activo",
        "docs": "/docs",
        "health": "/health"
    }
app.include_router(health_router)
app.include_router(incoming_router)
app.include_router(sessions_router)
app.include_router(conversation_router)
app.include_router(backend_router)
app.include_router(responses_router)
app.include_router(outgoing_router)
app.include_router(orchestrator_router)
app.include_router(webhook_router)