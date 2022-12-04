import asyncio
import io
import tempfile
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from starlette.background import BackgroundTask

from storage.config import settings
from storage.db.models import Content, Permission, User
from storage.db.models.permission import PermissionKind
from storage.db.session import SessionLocal
from storage.logging import log
from storage.schemas import content as schemas
from storage.web import deps

router = APIRouter()


@router.get("/", response_model=list[schemas.Content])
async def read_contents(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Read contents the user owns or has permission to read.."""

    log.debug(f"read_contents, {current_user.id=}")
    contents_owner: list[Content] = (
        db.query(Content).filter(Content.owner_id == current_user.id).all()
    )
    read_permissions: list[Permission] = (
        db.query(Permission)
        .filter(
            Permission.assignee_id == current_user.id,
            Permission.kind == PermissionKind.READ,
        )
        .all()
    )
    contents_permissed_ids: list[int] = [
        permission.content_id for permission in read_permissions
    ]
    contents_permissed: list[Content] = (
        db.query(Content).filter(Content.id.in_(contents_permissed_ids)).all()
    )
    return [*contents_owner, *contents_permissed]


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
    current_user: User = Depends(deps.get_current_user),
    content_in: schemas.ContentCreate,
):
    """Create content or get a redirect to an existing one if the same was created
    earlier.
    """

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
    async with httpx.AsyncClient() as client:
        r = await client.get(content_in.origin)
        content_file = io.BytesIO(r.content)
    async with httpx.AsyncClient(
        base_url=settings.IPFS_HTTP_PROVIDER,
    ) as client:
        response = await client.post(
            "/api/v0/add", files={"upload-files": content_file}
        )
    content = Content(
        origin=content_in.origin,
        ipfs_cid=response.json()["Hash"],
        owner_id=current_user.id,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
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


@router.get(
    "/{content_id}/download",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not Found"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Storage Unavailable"},
    },
)
async def download_content_file(
    *,
    db: dict = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    content_id: int,
):
    """Read content file the user owns or has permission to read."""

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
    filename = content.origin.split("/")[-1]
    url = f"{settings.IPFS_HTTP_PROVIDER}/api/v0/get?arg={content.ipfs_cid}"
    print(url)
    client = httpx.AsyncClient()

    async def iterative_download(download_url, async_client):
        try:
            async with async_client.stream('POST', download_url) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
        except Exception as e:
            log.error(f"download_content_file, {e=} {content.id=}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="IPFS provider failure",
            )
    return StreamingResponse(iterative_download(url, client),
                             headers={"Content-Disposition": f"attachment;{filename=}.tar"})

