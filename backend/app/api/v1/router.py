"""
API v1 Router - Combines all route modules
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.licenses import router as licenses_router
from app.api.v1.devices import router as devices_router
from app.api.v1.admin import router as admin_router
from app.api.v1.revenue import router as revenue_router
from app.api.v1.products import router as products_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(licenses_router)
api_router.include_router(devices_router)
api_router.include_router(admin_router)
api_router.include_router(revenue_router)
api_router.include_router(products_router)
