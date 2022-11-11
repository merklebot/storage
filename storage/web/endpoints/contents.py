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
from storage.logging import log
from storage.web import deps
from storage.web.schemas import content as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Content])
async def read_contents(
    *,
    db: dict = Depends(deps.get_fake_db),
):
    log.debug("read_contents")
    return list(db["contents"].values())


@router.post("/", response_model=schemas.Content)
async def create_content(
    content_create: schemas.ContentCreate,
    db: dict = Depends(deps.get_fake_db),
):
    log.debug(f"create_content, {content_create.origin}")
    async with httpx.AsyncClient() as client:
        r = await client.get(content_create.origin)
        content_file = io.BytesIO(r.content)
    async with httpx.AsyncClient(
        base_url=settings.IPFS_HTTP_PROVIDER,
    ) as client:
        response = await client.post(
            "/api/v0/add", files={"upload-files": content_file}
        )

    content = schemas.Content(
        id=max(db["contents"].keys()) + 1 if db["contents"].keys() else 0,
        ipfs_cid=response.json()["Hash"],
        owner_id=content_create.owner_id,
    )

    db["contents"][content.id] = content.dict()

    return content


@router.get("/{content_id}", response_model=schemas.Content)
async def read_content_by_id(
    *,
    db: dict = Depends(deps.get_fake_db),
    content_id: int,
):
    log.debug(f"read_content_by_id, {content_id=}")

    try:
        return db["contents"][content_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Content not found")


@router.patch("/{content_id}", response_model=schemas.Content)
async def update_content(
    *,
    db: dict = Depends(deps.get_fake_db),
    content_id: int,
    content_in: schemas.ContentUpdate,
):
    log.debug(f"update_content, {content_id=}, {content_in=}")
    if content_id not in db["contents"]:
        raise HTTPException(status_code=404, detail="Content not found")
    content = db["contents"][content_id]
    content.update(content_in.dict())
    db["contents"][content_id] = content
    return content


@router.delete("/{content_id}", response_model=schemas.Content)
async def delete_content(*, db: dict = Depends(deps.get_fake_db), content_id: int):
    log.debug(f"delete_content, {content_id=}")
    if content_id not in db["contents"]:
        raise HTTPException(status_code=404, detail="Content not found")
    content = db["contents"][content_id]
    del db["contents"][content_id]
    return content


@router.get("/{content_id}/download")
async def download_content_file(
    *, db: dict = Depends(deps.get_fake_db), content_id: int
):
    log.debug(f"download_content_file, {content_id=}")
    try:
        metadata = db["contents"][content_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Content not found")

    cid = metadata["ipfs_cid"]
    fd = tempfile.NamedTemporaryFile()
    ipfs_provider_url = urlparse(settings.IPFS_HTTP_PROVIDER)
    host, port = ipfs_provider_url.hostname, ipfs_provider_url.port
    proc = await asyncio.create_subprocess_shell(
        f"ipfs --api /dns4/{host}/tcp/{port} get -o {fd.name} {cid}",
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
    filename = metadata["origin"].split("/")[-1]
    return FileResponse(fd.name, filename=filename, background=BackgroundTask(fd.close))


@router.get("/{content_id}/files/{filename}")
async def download_content_by_filename(
    *, db: dict = Depends(deps.get_fake_db), content_id: int, filename: str
):
    log.debug(f"download_content_by_filename, {content_id=}, {filename=}")

    try:
        metadata = db["contents"][content_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Content not found")

    if filename not in metadata["origin"]:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    cid = metadata["ipfs_cid"]
    fd = tempfile.NamedTemporaryFile()
    ipfs_provider_url = urlparse(settings.IPFS_HTTP_PROVIDER)
    host, port = ipfs_provider_url.hostname, ipfs_provider_url.port
    proc = await asyncio.create_subprocess_shell(
        f"ipfs --api /dns4/{host}/tcp/{port} get -o {fd.name} {cid}",
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
    filename = metadata["origin"].split("/")[-1]
    return FileResponse(fd.name, filename=filename, background=BackgroundTask(fd.close))
