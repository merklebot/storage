from fastapi import APIRouter

from storage.web.endpoints import tenants

api_router = APIRouter()
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
