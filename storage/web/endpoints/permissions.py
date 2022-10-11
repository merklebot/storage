from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web.schemas import permission as schemas

router = APIRouter()


db = {}


@router.get("/", response_model=list[schemas.Permission])
async def read_permissions():
    return list(db.values())


@router.post(
    "/", response_model=schemas.Permission, status_code=status.HTTP_201_CREATED
)
async def create_permission(permission_in: schemas.PermissionCreate):
    log.debug(f"create_permission, {permission_in=}")
    permission = schemas.Permission(
        id=max(db.keys()) + 1 if db.keys() else 0,
        **permission_in.dict(),
    )
    db[permission.id] = permission.dict()
    return permission


@router.get("/{permission_id}", response_model=schemas.Permission)
async def read_permission_by_id(permission_id: int):
    log.debug(f"read_permission_by_id, {permission_id=}")
    try:
        return db[permission_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Permission not found")


@router.put("/{permission_id}", response_model=schemas.Permission)
async def update_permission(
    permission_id: int, permission_in: schemas.PermissionUpdate
):
    log.debug(f"update_permission, {permission_id=}, {permission_in=}")
    if permission_id not in db:
        raise HTTPException(status_code=404, detail="Permission not found")
    permission = db[permission_id]
    log.debug(permission)
    permission.update({k: v for k, v in permission_in.dict().items() if v is not None})
    db[permission_id] = permission
    return permission
