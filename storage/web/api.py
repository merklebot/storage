from fastapi import APIRouter, status

from storage.web.endpoints import (
    contents,
    jobs,
    keys,
    permissions,
    specifications,
    tenants,
    tokens,
    users,
)

api_router = APIRouter(
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Forbidden",
        },
    },
)
api_router.include_router(contents.router, prefix="/contents", tags=["Contents"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(keys.router, prefix="/keys", tags=["Keys"])
api_router.include_router(
    permissions.router, prefix="/permissions", tags=["Permissions"]
)
api_router.include_router(
    specifications.router, prefix="/specifications", tags=["Specifications"]
)
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(tokens.router, prefix="/tokens", tags=["Tokens"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
