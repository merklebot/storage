from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from storage.db.models import User
from storage.db.models.tenant import Tenant
from storage.logging import log
from storage.web import deps
from storage.web.deps import get_current_tenant
from storage.web.schemas import user as schemas

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


@router.post("/", response_model=schemas.User)
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


@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    *,
    db: dict = Depends(deps.get_db),
    user_id: int,
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.debug(f"read_user_by_id, {user_id=}, {current_tenant.id=}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(
    *,
    db: dict = Depends(deps.get_db),
    user_id: int,
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.debug(f"delete_user, {user_id=}, {db=}, {current_tenant.id=}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user
