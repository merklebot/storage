from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse

from storage.db.models import Content, Permission, User
from storage.db.session import SessionLocal
from storage.logging import log
from storage.web import deps
from storage.web.schemas import permission as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Permission])
async def read_permissions(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Read permissions where the user is an owner of a content or a permission
    assignee.
    """

    log.debug(f"read_permissions, {current_user=}")
    # ToDo: optimize queries with eager relationships loading and joins
    permissions_assigned: list[Permission] = (
        db.query(Permission).filter(Permission.assignee_id == current_user.id).all()
    )
    contents: list[Content] = (
        db.query(Content.id).filter(Content.owner_id == current_user.id).all()
    )
    contents_ids: list[int] = [content.id for content in contents]
    permissions_issued: list[Permission] = db.query(Permission).filter(
        Permission.content_id.in_(contents_ids)
    )
    return [*permissions_issued, *permissions_assigned]


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.Permission
)
async def create_permission(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    permission_in: schemas.PermissionCreate,
):
    """Create permission or get a redirect to an existing one if the given combination
    of agignee, content and permission kind already exists. Requires the user to be an
    owner of the given content and existance of the content and the given ansignee.
    """

    log.debug(f"create_permission, {permission_in=}, {current_user.id=}")
    assignee_exists: bool = db.query(
        db.query(User).filter(User.id == permission_in.assignee_id).exists()
    ).scalar()
    if not assignee_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assignee user not found"
        )
    content: Content | None = (
        db.query(Content).filter(Content.id == permission_in.content_id).first()
    )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    if current_user.id != content.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    permission_id: int | None = (
        db.query(Permission.id)
        .filter(
            Permission.assignee_id == permission_in.assignee_id,
            Permission.content_id == permission_in.content_id,
            Permission.kind == permission_in.kind,
        )
        .scalar()
    )
    if permission_id:
        return RedirectResponse(
            f"/permissions/{permission_id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    permission = Permission(
        assignee_id=permission_in.assignee_id,
        content_id=permission_in.content_id,
        kind=permission_in.kind,
    )
    # ToDo: what if the content or assignee deleted while querying?
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


@router.get("/{permission_id}", response_model=schemas.Permission)
async def read_permission_by_id(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    permission_id: int,
):
    """Read permission if the user is an owner of the permission content or a
    permission assignee.
    """

    log.debug(f"read_permission_by_id, {permission_id=}, {current_user.id=}")
    # ToDo: optimize query for content owner check
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
    # ToDo: what if permission or content deleted?
    if (
        current_user.id != content.owner_id
        and current_user.id != permission.assignee_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return permission


@router.delete("/{permission_id}", response_model=schemas.Permission)
async def delete_permission(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    permission_id: int,
):
    log.debug(f"delete_permission, {permission_id=}, {current_user.id=}")
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
    if current_user.id != content.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    db.delete(permission)
    db.commit()
    return permission
