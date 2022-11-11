import asyncio
import io
import tempfile
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from storage.config import settings
from storage.db.models import Content, User
from storage.db.session import SessionLocal
from storage.logging import log
from storage.web import deps
from storage.web.schemas import content as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Content])
async def read_contents(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    log.debug(f"read_contents, {current_user.id=}")
    contents: Content = (
        db.query(Content).filter(Content.owner_id == current_user.id).all()
    )
    return contents


@router.post("/", response_model=schemas.Content)
async def create_content(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    content_in: schemas.ContentCreate,
):
    log.debug(f"create_content, {content_in.origin=}, {current_user.id=}")
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


@router.get("/{content_id}", response_model=schemas.Content)
async def read_content_by_id(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    content_id: int,
):
    log.debug(f"read_content_by_id, {content_id=}, {current_user.id=}")
    content: Content | None = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return content


@router.delete("/{content_id}", response_model=schemas.Content)
async def delete_content(
    *,
    db: dict = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    content_id: int,
):
    log.debug(f"delete_content, {content_id=}, {current_user.id=}")
    content: Content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db.delete(content)
    db.commit()
    return content


@router.get("/{content_id}/download")
async def download_content_file(
    *,
    db: dict = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    content_id: int,
):
    log.debug(f"download_content_file, {content_id=}, {current_user.id=}")
    content: Content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    fd = tempfile.NamedTemporaryFile()
    ipfs_provider_url = urlparse(settings.IPFS_HTTP_PROVIDER)
    host, port = ipfs_provider_url.hostname, ipfs_provider_url.port
    proc = await asyncio.create_subprocess_shell(
        f"ipfs --api /dns4/{host}/tcp/{port} get -o {fd.name} {content.ipfs_cid}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode:
        log.error(f"{stdout=}, {stderr=}, {fd.name=}, {proc.returncode=}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="IPFS provider failure",
        )
    log.debug(f"{stdout=}, {stderr=}, {fd.name=}")
    filename = content.origin.split("/")[-1]
    return FileResponse(fd.name, filename=filename, background=BackgroundTask(fd.close))
