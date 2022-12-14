from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.db.models import User
from storage.db.models.tenant import Tenant
from storage.logging import log
from storage.schemas import user as schemas
from storage.web import deps
from storage.web.deps import get_current_tenant

router = APIRouter()


@router.get("/", response_model=list[schemas.User])
async def read_users(
    *,
    db: dict = Depends(deps.get_db),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.info(f"read_users, {current_tenant.id=}")
    users = db.query(User).all()
    return users


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_description="Created",
    response_model=schemas.User,
)
async def create_user(
    *,
    db: dict = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.debug(f"create_user, {user_in=}, {current_tenant.id=}")
    user = User()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get(
    "/{user_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not Found"},
    },
    response_model=schemas.User,
)
async def read_user_by_id(
    *,
    db: dict = Depends(deps.get_db),
    user_id: int,
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.debug(f"read_user_by_id, {user_id=}, {current_tenant.id=}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_description="Deleted",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}},
    response_model=schemas.User,
)
async def delete_user(
    *,
    db: dict = Depends(deps.get_db),
    user_id: int,
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.debug(f"delete_user, {user_id=}, {db=}, {current_tenant.id=}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.delete(user)
    db.commit()
    return user
