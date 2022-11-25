from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.db.models import Token, User
from storage.db.models.tenant import Tenant
from storage.logging import log
from storage.web import deps
from storage.web.deps import get_current_tenant
from storage.schemas import token as schemas
from storage.web.security import create_api_key, get_api_key_hash

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_description="Created",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}},
    response_model=schemas.TokenSecret,
)
async def create_token(
    *,
    db: dict = Depends(deps.get_db),
    current_tenant: Tenant = Depends(get_current_tenant),
    token_in: schemas.TokenCreate,
):
    """Create access token for a given user."""

    log.debug(f"create_token, {token_in=}, {current_tenant.id=}")
    user = db.query(User).filter(User.id == token_in.owner_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    api_key = create_api_key()
    token = Token(
        hashed_token=get_api_key_hash(api_key),
        expiry=token_in.expiry,
        owner_id=token_in.owner_id,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return {"plain_token": api_key, **token.__dict__}


@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    response_description="Updated",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not Found"},
    },
    response_model=schemas.Token,
)
async def update_token_expiry(
    *,
    db: dict = Depends(deps.get_db),
    current_tenant: Tenant = Depends(get_current_tenant),
    token_update: schemas.TokenUpdateExpiry,
):
    """Update token expiry. Must be in future, but not exceed current expiry value."""

    log.debug(f"create_token, {token_update=}, {current_tenant.id=}")
    token: Token | None = db.query(Token).filter(Token.id == token_update.id).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )
    # ToDo: compare in RDBMS
    if token.expiry and token_update.expiry > token.expiry.replace(tzinfo=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Can't extend token expiration",
        )
    # ToDo: compare with RDBMS time
    if token_update.expiry <= datetime.now(tz=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Can't set expiry to the moment in the past",
        )
    token.expiry = token_update.expiry
    db.commit()
    db.refresh(token)
    return token
