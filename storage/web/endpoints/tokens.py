from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.db.models import Token, User
from storage.db.models.tenant import Tenant
from storage.logging import log
from storage.web import deps
from storage.web.deps import get_current_tenant
from storage.web.schemas import token as schemas
from storage.web.security import create_api_key, get_api_key_hash

router = APIRouter()


@router.post("/", response_model=schemas.Token)
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
