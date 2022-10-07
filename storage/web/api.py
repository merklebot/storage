from fastapi import APIRouter

from storage.web.endpoints import contents, tenants

api_router = APIRouter()
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(contents.router, prefix="/contents", tags=["Contents"])
