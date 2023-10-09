from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_camelcase import CamelModel as BaseModel
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.sql import func

from storage.db.models import Content
from storage.db.models.tenant import Tenant
from storage.db.models.token import Token
from storage.db.models.user import User
from storage.db.session import with_db
from storage.schemas import content as content_schemas
from storage.services.instant_storage import (
    generate_access_link_for_instant_storage_data,
)
from storage.web import deps
from storage.web.security import create_access_token, create_api_key, get_api_key_hash

router = APIRouter()


class NewUserSchema(BaseModel):
    tenant_name: str


class UserInfoSchema(BaseModel):
    tenant_name: str
    user_id: int


class RemoveTokenSchema(BaseModel):
    tenant_name: str
    user_id: int
    token_id: int


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


@router.get(".getStats")
async def get_stats(
    tenant_name: str, user_id: int, authed=Depends(deps.get_app_by_admin_token)
):
    with with_db(tenant_schema=tenant_name) as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant doesn't exist"
            )
        contents_number = db.query(Content).filter(Content.owner_id == user.id).count()
        contents_funcs = (
            db.query(func.sum(Content.ipfs_file_size).label("sum_ipfs_file_size"))
            .filter(Content.owner_id == user.id)
            .first()
        )
    return {
        "contents_number": contents_number,
        "contents_size": contents_funcs["sum_ipfs_file_size"],
    }


@router.get(".getContentDownloadLink")
async def get_content_download_link(
    tenant_name: str,
    user_id: int,
    content_id: int,
    authed=Depends(deps.get_app_by_admin_token),
):
    with with_db(tenant_schema=tenant_name) as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant doesn't exist"
            )
        content: Content = (
            db.query(Content)
            .filter(Content.id == content_id, Content.owner_id == user.id)
            .first()
        )

    presigned_url, expires_in = await generate_access_link_for_instant_storage_data(
        content.ipfs_cid, filename=content.filename
    )
    return {"status": "ok", "url": presigned_url, "expires_in": expires_in}


@router.get(".listContents", response_model=Page[content_schemas.Content])
async def list_contents(
    tenant_name: str, user_id: int, authed=Depends(deps.get_app_by_admin_token)
):
    with with_db(tenant_schema=tenant_name) as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant doesn't exist"
            )
        return paginate(db, select(Content).filter(Content.owner_id == user.id))


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


@router.post(".removeToken")
async def remove_token(
    remove_token_req: RemoveTokenSchema, authed=Depends(deps.get_app_by_admin_token)
):
    with with_db(tenant_schema=remove_token_req.tenant_name) as db:
        user = db.query(User).filter(User.id == remove_token_req.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant doesn't exist"
            )

        db.query(Token).filter(
            Token.owner_id == user.id and Token.id == remove_token_req.token_id
        ).delete()
        db.commit()
    return {"status": "ok"}
