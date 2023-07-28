from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_camelcase import CamelModel as BaseModel

from storage.db.models.tenant import Tenant
from storage.db.models.token import Token
from storage.db.models.user import User
from storage.db.session import with_db
from storage.web import deps
from storage.web.security import create_access_token, create_api_key, get_api_key_hash

router = APIRouter()


class NewUserSchema(BaseModel):
    tenant_name: str


class UserInfoSchema(BaseModel):
    tenant_name: str
    user_id: int


@router.post(".add")
async def add_user(user: NewUserSchema, authed=Depends(deps.get_app_by_admin_token)):
    with with_db() as db:
        tenant = db.query(Tenant).filter(Tenant.name == user.tenant_name).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant doesn't exist"
        )
    with with_db(tenant_schema=tenant.schema) as db:
        user = User()
        db.add(user)
        db.commit()
        db.refresh(user)

    return {"status": "ok", "user": user}


@router.get(".listTokens")
async def list_tokens(
    tenant_name: str, user_id: int, authed=Depends(deps.get_app_by_admin_token)
):
    with with_db(tenant_schema=tenant_name) as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant doesn't exist"
            )
        tokens = db.query(Token).filter(Token.owner_id == user.id).all()
    return {"status": "ok", "tokens": tokens}


@router.post(".createToken")
async def create_token(
    user_req: UserInfoSchema, authed=Depends(deps.get_app_by_admin_token)
):
    with with_db(tenant_schema=user_req.tenant_name) as db:
        user = db.query(User).filter(User.id == user_req.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant doesn't exist"
            )
        api_key = create_api_key()
        token = Token(
            hashed_token=get_api_key_hash(api_key),
            owner_id=user.id,
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        access_token = create_access_token(token.id, api_key)
    return {"status": "ok", "access_token": access_token}
