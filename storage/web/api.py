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

tags_metadata = [
    {
        "name": "Contents",
        "description": (
            "Content resource represents stored file. Duplicates are not allowed and "
            "an attemt to create a duplicate by the same user will redirect to an "
            "existing content resource created by the user earlier."
        ),
    },
    {
        "name": "Jobs",
        "description": (
            "Job resource represents heavy operation order like an encryption or "
            "decryption. Implementation is incomplete yet and not ready for usage."
        ),
    },
    {
        "name": "Keys",
        "description": (
            "Key resource represents encryption key data. Implementation is incomplete "
            "yet and not ready for usage."
        ),
    },
    {
        "name": "Permissions",
        "description": (
            "Permission resource represents access permission content owner may "
            "assign to another users. Only `read` permissions can be issued at "
            "current version."
        ),
    },
    {
        "name": "Specifications",
        "description": (
            "Specification resource represents content storing rules and constraints "
            "like region, replication networks and number of relications. "
            "Implementation is incomplete yet and not ready for usage."
        ),
    },
    {
        "name": "Tenants",
        "description": ("Tenant can manage users and issue auth tokens for them."),
    },
    {
        "name": "Tokens",
        "description": (
            "Token resource represents access token. Plain tokens are never stored "
            "and revealed only once. If expiry is not set, the token is valid "
            "infinitely. Expiration can be set to the near future to invalidate the "
            "token."
        ),
    },
    {
        "name": "Users",
        "description": (
            "User resource represents current or potential content owner or reader."
        ),
    },
]
