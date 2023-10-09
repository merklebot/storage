import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, Request, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from storage.config import settings
from storage.db.models import Content, Permission, User
from storage.db.models.content import ContentAvailability
from storage.db.models.filecoin import RestoreRequest, RestoreRequestStatus
from storage.db.models.permission import PermissionKind
from storage.db.models.tenant import Tenant
from storage.db.session import SessionLocal, with_db
from storage.logging import log
from storage.schemas import content as schemas
from storage.services.instant_storage import (
    generate_access_link_for_instant_storage_data,
    upload_data_to_instant_storage,
)
from storage.upload import process_data_from_origin
from storage.web import deps

router = APIRouter()


@router.get("/", response_model=Page[schemas.Content])
async def read_contents(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Read contents the user owns or has permission to read."""

    log.debug(f"read_contents, {current_user.id=}")
    # contents_owner: list[Content] = (
    #     db.query(Content).filter(Content.owner_id == current_user.id).all()
    # )
    # read_permissions: list[Permission] = (
    #     db.query(Permission)
    #     .filter(
    #         Permission.assignee_id == current_user.id,
    #         Permission.kind == PermissionKind.READ,
    #     )
    #     .all()
    # )
    # contents_permissed_ids: list[int] = [
    #     permission.content_id for permission in read_permissions
    # ]
    # contents_permissed: list[Content] = (
    #     db.query(Content).filter(Content.id.in_(contents_permissed_ids)).all()
    # )
    # return [*contents_owner, *contents_permissed]

    return paginate(db, select(Content).filter(Content.owner_id == current_user.id))


@router.post(
    "/",
    response_model=schemas.Content,
    status_code=status.HTTP_201_CREATED,
    response_description="Created",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Content,
            "description": "Duplicate",
        },
        status.HTTP_303_SEE_OTHER: {
            "model": None,
            "description": "Already Exists",
        },
    },
)
async def create_content(
    *,
    db: SessionLocal = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_user),
    file_in: UploadFile | None = None,
    request: Request,
):
    """Create content or get a redirect to an existing one if the same was created
    earlier.
    """
    if file_in:
        log.debug(f"create_content, {file_in.filename=}")
        async with httpx.AsyncClient(
            base_url=settings.IPFS_HTTP_PROVIDER,
        ) as client:
            response = await client.post(
                "/api/v0/add",
                params={"cid-version": 1, "only-hash": True},
                files={"upload-files": file_in.file},
            )
        file_in.file.seek(0)
        data = file_in.file.read()
        ipfs_cid = response.json()["Hash"]
        await upload_data_to_instant_storage(data=data, ipfs_cid=ipfs_cid)
        content = Content(
            filename=file_in.filename,
            ipfs_cid=ipfs_cid,
            ipfs_file_size=int(response.json()["Size"]),
            availability=ContentAvailability.INSTANT,
            is_instant=True,
            owner_id=current_user.id,
        )
        db.add(content)
        db.commit()
        db.refresh(content)
        return content

    body = await request.json()
    content_in = schemas.ContentCreate(**body)

    if content_in:
        log.debug(f"create_content, {content_in.origin=}, {current_user.id=}")
        content_id: int | None = (
            db.query(Content.id)
            .filter(
                Content.owner_id == current_user.id,
                Content.origin == content_in.origin,
            )
            .scalar()
        )
        if content_id:
            return RedirectResponse(
                f"/contents/{content_id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        content = Content(
            origin=content_in.origin,
            availability=ContentAvailability.PENDING,
            owner_id=current_user.id,
        )
        db.add(content)
        db.commit()
        db.refresh(content)

        background_tasks.add_task(
            process_data_from_origin,
            origin=content.origin,
            content_id=content.id,
            db=db,
        )

        return content


@router.get(
    "/{content_id}",
    response_model=schemas.Content,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}},
)
async def read_content_by_id(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    content_id: int,
):
    """Read content the user owns or has permission to read."""

    log.debug(f"read_content_by_id, {content_id=}, {current_user.id=}")
    content: Content | None = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    permission: Permission = (
        db.query(Permission)
        .filter(
            Permission.assignee_id == current_user.id,
            Permission.content_id == content.id,
            Permission.kind == PermissionKind.READ,
        )
        .first()
    )
    if current_user.id != content.owner_id and not permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return content


@router.delete(
    "/{content_id}",
    response_model=schemas.Content,
    status_code=status.HTTP_200_OK,
    response_description="Deleted",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}},
)
async def delete_content(
    *,
    db: dict = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    content_id: int,
):
    """Delete content the user owns."""

    log.debug(f"delete_content, {content_id=}, {current_user.id=}")
    content: Content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    if content.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    db.delete(content)
    db.commit()
    return content


@router.post("/{content_id}/restore")
async def restore_content_file(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    tenant: Tenant = Depends(deps.get_tenant),
    content_restore_request: schemas.ContentRestoreRequest,
    content_id: int,
):
    log.debug(f"restore_content_by_id, {content_id=}, {current_user.id=}")
    content: Content | None = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    permission: Permission = (
        db.query(Permission)
        .filter(
            Permission.assignee_id == current_user.id,
            Permission.content_id == content.id,
            Permission.kind == PermissionKind.READ,
        )
        .first()
    )
    if current_user.id != content.owner_id and not permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    if content.availability == ContentAvailability.ARCHIVE:
        with with_db() as session:
            restore_request = RestoreRequest(
                tenant_name=tenant.name,
                content_id=content.id,
                status=RestoreRequestStatus.PENDING,
            )
            if content_restore_request.webhook_url:
                restore_request.webhook_url = content_restore_request.webhook_url
            session.add(restore_request)
            session.commit()

        return {"status": "ok"}
    else:
        return content


@router.get(
    "/{content_id}/download",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not Found"},
        status.HTTP_410_GONE: {"description": "Permanently unavailable"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Storage Unavailable"},
    },
)
async def download_content_file(
    *,
    db: dict = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    content_id: int,
):
    """Returns temporary link to file the user owns or has permission to read."""

    log.debug(f"download_content_file, {content_id=}, {current_user.id=}")
    content: Content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    permission: Permission = (
        db.query(Permission)
        .filter(
            Permission.assignee_id == current_user.id,
            Permission.content_id == content.id,
            Permission.kind == PermissionKind.READ,
        )
        .first()
    )
    if current_user.id != content.owner_id and not permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    if content.availability == ContentAvailability.ABSENT:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Permanently unavailable",
        )
    if content.availability == ContentAvailability.ARCHIVE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archived")
    if content.availability == ContentAvailability.ENCRYPTED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encrypted")
    if content.availability != ContentAvailability.INSTANT:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unavailable by unknown reason",
        )

    presigned_url, expires_in = await generate_access_link_for_instant_storage_data(
        content.ipfs_cid, content.filename
    )
    return {"url": presigned_url, "expires_in": expires_in}
