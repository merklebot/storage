from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.db.models import Content, Permission
from storage.db.session import SessionLocal
from storage.logging import log
from storage.web import deps
from storage.web.schemas import permission as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Permission])
async def read_permissions(
    *,
    db: SessionLocal = Depends(deps.get_db),
):
    log.debug("read_permissions")
    permissions = db.query(Permission).all()
    return permissions


@router.post("/", response_model=schemas.Permission)
async def create_permission(
    *,
    db: SessionLocal = Depends(deps.get_db),
    user_id: int,
    permission_in: schemas.PermissionCreate,
):
    log.debug(f"create_permission, {permission_in=}, {user_id=}")
    content: Content | None = (
        db.query(Content).filter(Content.id == permission_in.content_id).first()
    )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    if user_id != content.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    permission = Permission(
        kind=permission_in.kind,
        content_id=permission_in.content_id,
        assignee_id=permission_in.assignee_id,
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


@router.get("/{permission_id}", response_model=schemas.Permission)
async def read_permission_by_id(
    *,
    db: SessionLocal = Depends(deps.get_db),
    permission_id: int,
):
    log.debug(f"read_permission_by_id, {permission_id=}")
    permission: Permission | None = (
        db.query(Permission).filter(Permission.id == permission_id).first()
    )
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )
    return permission


@router.delete("/{permission_id}", response_model=schemas.Permission)
async def delete_permission(
    *,
    db: SessionLocal = Depends(deps.get_db),
    user_id: int,
    permission_id: int,
):
    log.debug(f"delete_permission, {permission_id=}, {user_id=}")
    permission: Permission | None = (
        db.query(Permission).filter(Permission.id == permission_id).first()
    )
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )
    content: Content = (
        db.query(Content).filter(Content.id == permission.content_id).first()
    )
    if user_id != content.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    db.delete(permission)
    db.commit()
    return permission
