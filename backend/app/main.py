from fastapi import APIRouter, FastAPI
from sqlalchemy import text

from app.core.config import get_settings
from app.core.db import DbSession
from app.core.errors import registrar_manejadores
from app.core.logging import configurar_logging
from app.modules.auth.router import router as auth_router

configurar_logging()

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
)

registrar_manejadores(app)

api_v1 = APIRouter(prefix="/api/v1")


@api_v1.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@api_v1.get("/health/db", tags=["Sistema"])
def health_db(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


api_v1.include_router(auth_router)
app.include_router(api_v1)
app.include_router(auth_router, prefix="/api/v1")
