from typing import Generator
from urllib.parse import urlparse

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy import func

from storage.db.models.tenant import Tenant
from storage.db.models.token import Token
from storage.db.session import with_db
from storage.web.security import verify_api_key

db = {
    "contents": {},
    "jobs": {},
    "keys": {},
    "permissions": {},
    "specifications": {},
    "tenants": {},
    "users": {},
}


def get_fake_db() -> Generator:
    yield db


def get_tenant(request: Request) -> Tenant:
    host_without_port = request.headers["host"].split(":", 1)[0]
    url = urlparse(host_without_port)
    subdomain = url.path.split(".", 1)[0]

    with with_db(None) as db:
        tenant = db.query(Tenant).filter(Tenant.host == subdomain).one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not found"
        )

    return tenant


def get_db(tenant: Tenant = Depends(get_tenant)) -> Generator:
    with with_db(tenant.schema) as db:
        yield db


def get_tokens_by_tenant_id(db, tenant_id: int) -> list[Token]:
    tokens = (
        db.query(Token)
        .filter(Token.owner_id == tenant_id)
        .filter((Token.expiry == None) | (Token.expiry > func.now()))  # noqa: E711
        .all()
    )
    return tokens


api_key_header_auth = APIKeyHeader(name="Authorization", auto_error=True)


def get_api_key(api_key_header: str = Security(api_key_header_auth)) -> str:
    return api_key_header


def get_current_tenant(
    api_key: str = Depends(get_api_key),
    tenant: Tenant = Depends(get_tenant),
) -> Tenant:
    with with_db() as db:
        tokens = get_tokens_by_tenant_id(db, tenant.id)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials2",
        )
    verify = [verify_api_key(api_key, token.hashed_token) for token in tokens]
    if not any(verify):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    return tenant
