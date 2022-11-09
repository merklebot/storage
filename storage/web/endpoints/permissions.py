from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web import deps
from storage.web.schemas import permission as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Permission])
async def read_permissions(
    *,
    db: dict = Depends(deps.get_fake_db),
):
    return list(db["permissions"].values())


@router.post(
    "/", response_model=schemas.Permission, status_code=status.HTTP_201_CREATED
)
async def create_permission(
    *,
    db: dict = Depends(deps.get_fake_db),
    permission_in: schemas.PermissionCreate,
    user_id: int,
):

    permissions = deps.get_permission_for_user_by_content_id(
        db, content_id=permission_in.content_id, user_id=user_id
    )
    if not permissions.owner:
        raise HTTPException(
            status_code=403, detail="No permission to create permission"
        )
    log.debug(f"create_permission, {permission_in=}")
    permission = schemas.Permission(
        id=max(db["permissions"].keys()) + 1 if db["permissions"].keys() else 0,
        **permission_in.dict(),
    )
    db["permissions"][permission.id] = permission.dict()
    return permission


@router.get("/{permission_id}", response_model=schemas.Permission)
async def read_permission_by_id(
    *,
    db: dict = Depends(deps.get_fake_db),
    permission_id: int,
):
    log.debug(f"read_permission_by_id, {permission_id=}")
    try:
        return db["permissions"][permission_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Permission not found")


@router.put("/{permission_id}", response_model=schemas.Permission)
async def update_permission(
    *,
    db: dict = Depends(deps.get_fake_db),
    permission_id: int,
    permission_in: schemas.PermissionUpdate,
    user_id: int,
):
    permissions = deps.get_permission_for_user_by_content_id(
        db, content_id=permission_in.content_id, user_id=user_id
    )
    if not (permissions.owner or permissions.update):
        raise HTTPException(
            status_code=403, detail="No permission to update permission"
        )
    log.debug(f"update_permission, {permission_id=}, {permission_in=}")
    if permission_id not in db["permissions"]:
        raise HTTPException(status_code=404, detail="Permission not found")
    permission = db["permissions"][permission_id]
    log.debug(permission)
    permission.update({k: v for k, v in permission_in.dict().items() if v is not None})
    db["permissions"][permission_id] = permission
    return permission


@router.delete("/{permission_id}", response_model=schemas.Permission)
async def delete_permission(
    *,
    db: dict = Depends(deps.get_fake_db),
    permission_id: int,
    user_id: int,
):
    log.debug(f"delete_permission, {permission_id=}")
    if permission_id not in db["permission"]:
        raise HTTPException(status_code=404, detail="Permission not found")
    permission = db["permissions"].pop(permission_id)
    if not permission["owner_id"] != user_id:
        raise HTTPException(
            status_code=403, detail="No permission to delete permission"
        )
    log.debug(permission)
    return permission
