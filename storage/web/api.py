from fastapi import APIRouter

from storage.web.endpoints import contents, jobs, keys, specifications, tenants, users

api_router = APIRouter()
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(keys.router, prefix="/keys", tags=["Keys"])
api_router.include_router(contents.router, prefix="/contents", tags=["Contents"])
api_router.include_router(
    specifications.router, prefix="/specifications", tags=["Specifications"]
)
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
