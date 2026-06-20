import logging

from fastapi import FastAPI

from app.api.v1.routes.report_routes import router as report_router
from app.core.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
app.include_router(report_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}

