from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from storage.db.models.tenant import Tenant
from storage.logging import log
from storage.web import deps
from storage.web.deps import get_current_tenant
from storage.web.schemas import user as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.User])
async def read_users(
    *,
    db: dict = Depends(deps.get_fake_db),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.info(f"read_users, {current_tenant.id=}")
    return list(db["users"].values())


@router.post("/", response_model=schemas.User)
async def create_user(
    *,
    db: dict = Depends(deps.get_fake_db),
    user_in: schemas.UserCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.debug(f"create_user, {user_in=}, {current_tenant.id=}")
    user = schemas.User(
        id=max(db["users"].keys()) + 1 if db["users"].keys() else 0,
        **user_in.dict(),
        tenant_id=current_tenant.id,
    )
    db["users"][user.id] = user.dict()
    return user


@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    *,
    db: dict = Depends(deps.get_fake_db),
    user_id: int,
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.debug(f"read_user_by_id, {user_id=}, {current_tenant.id=}")
    try:
        return db["users"][user_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="User not found")


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    *,
    db: dict = Depends(deps.get_fake_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.debug(f"update_user, {user_id=}, {user_in=}, {current_tenant.id=}")
    if user_id not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    user = db["users"][user_id]
    user.update(user_in.dict())
    db["users"][user_id] = user
    return user


@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(
    *,
    db: dict = Depends(deps.get_fake_db),
    user_id: int,
    current_tenant: Tenant = Depends(get_current_tenant),
):
    log.debug(f"delete_user, {user_id=}, {db=}, {current_tenant.id=}")
    if user_id not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    user = db["users"][user_id]
    del db["users"][user_id]
    return user
