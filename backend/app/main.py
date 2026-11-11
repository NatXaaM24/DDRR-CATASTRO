from fastapi import APIRouter, FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
)

api_v1 = APIRouter(prefix="/api/v1")


@api_v1.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


app.include_router(api_v1)
