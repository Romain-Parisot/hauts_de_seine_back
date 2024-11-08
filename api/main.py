from fastapi import APIRouter

from api.routes import health_check

api_router = APIRouter()
api_router.include_router(health_check.router, prefix="/healthcheck", tags=["healthcheck"])
