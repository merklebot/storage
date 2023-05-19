from casdoor import CasdoorSDK
from fastapi import APIRouter, Request, status

from storage.config import settings
from storage.db.models import User
from storage.db.models.tenant import Tenant, Token
from storage.db.multitenancy import tenant_create
from storage.db.session import with_db
from storage.web.routers import (
    contents,
    jobs,
    keys,
    permissions,
    specifications,
    tokens,
    users,
)
from storage.web.security import create_api_key, get_api_key_hash

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
api_router.include_router(tokens.router, prefix="/tokens", tags=["Tokens"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])


@api_router.post("/signin")
async def process_tenant_signin(request: Request):

    sdk = CasdoorSDK(
        endpoint=settings.CASDOOR_ENDPOINT,
        client_id=settings.CASDOOR_CLIENT_ID,
        client_secret=settings.CASDOOR_CLIENT_SECRET,
        certificate=settings.CASDOOR_CERTIFICATE,
        org_name=settings.CASDOOR_ORG_NAME,
        application_name=settings.CASDOOR_APPLICATION_NAME,
    )
    code = request.query_params.get("code")
    token = sdk.get_oauth_token(code)
    user = sdk.parse_jwt_token(token)
    with with_db() as db:
        tenant = db.query(Tenant).filter(Tenant.name == user["name"]).first()
    if not tenant:
        tenant_name = user["name"]
        tenant = Tenant(
            name=tenant_name,
            schema=tenant_name,
            host=tenant_name.replace("_", "-"),
        )
        tenant = tenant_create(tenant)
    api_key = create_api_key()
    token = Token(
        hashed_token=get_api_key_hash(api_key),
        owner_id=tenant.id,
    )
    with with_db() as db:
        db.add(token)
        db.commit()
    with with_db(tenant.schema) as db:
        tenant_user = db.query(User).first()
        if not tenant_user:
            tenant_user = User()
            db.add(tenant_user)
            db.commit()

    return {"status": "ok", "tenant_name": tenant.name, "tenant_key": api_key}


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
