from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web import deps
from storage.web.schemas import permission as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Permission])
async def read_permissions(
    *,
    db: dict = Depends(deps.get_db),
):
    return list(db["permissions"].values())


@router.post(
    "/", response_model=schemas.Permission, status_code=status.HTTP_201_CREATED
)
async def create_permission(
    *, db: dict = Depends(deps.get_db), permission_in: schemas.PermissionCreate
):
    log.debug(f"create_permission, {permission_in=}")
    permission = schemas.Permission(
        id=max(db["permissions"].keys()) + 1 if db["permissions"].keys() else 0,
        **permission_in.dict(),
    )
    db["permissions"][permission.id] = permission.dict()
    return permission


@router.get("/{permission_id}", response_model=schemas.Permission)
async def read_permission_by_id(*, db: dict = Depends(deps.get_db), permission_id: int):
    log.debug(f"read_permission_by_id, {permission_id=}")
    try:
        return db["permissions"][permission_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Permission not found")


@router.put("/{permission_id}", response_model=schemas.Permission)
async def update_permission(
    *,
    db: dict = Depends(deps.get_db),
    permission_id: int,
    permission_in: schemas.PermissionUpdate,
):
    log.debug(f"update_permission, {permission_id=}, {permission_in=}")
    if permission_id not in db["permissions"]:
        raise HTTPException(status_code=404, detail="Permission not found")
    permission = db["permissions"][permission_id]
    log.debug(permission)
    permission.update({k: v for k, v in permission_in.dict().items() if v is not None})
    db["permissions"][permission_id] = permission
    return permission
