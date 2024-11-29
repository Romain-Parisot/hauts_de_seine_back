from fastapi import APIRouter

from api.routes import health_check , user, product, qr

api_router = APIRouter()
api_router.include_router(health_check.router, prefix="/healthcheck", tags=["healthcheck"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(product.router, prefix="/products", tags=["products"])
api_router.include_router(qr.router, prefix="/qr", tags=["qr"])