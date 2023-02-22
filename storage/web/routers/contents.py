import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, status, File, UploadFile, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse

from storage.config import settings
from storage.db.models import Content, Permission, User
from storage.db.models.content import ContentAvailability
from storage.db.models.permission import PermissionKind
from storage.db.session import SessionLocal
from storage.logging import log
from storage.schemas import content as schemas
from storage.upload import process_data_from_origin
from storage.web import deps

router = APIRouter()


@router.get("/", response_model=list[schemas.Content])
async def read_contents(
        *,
        db: SessionLocal = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user),
):
    """Read contents the user owns or has permission to read."""

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
        background_tasks: BackgroundTasks,
        current_user: User = Depends(deps.get_current_user),
        file_in: UploadFile | None = None,
        request: Request
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
                "/api/v0/add", params={'cid-version': 1}, files={"upload-files": file_in.file}
            )
        content = Content(
            filename=file_in.filename,
            ipfs_cid = response.json()["Hash"],
            ipfs_file_size = int(response.json()["Size"]),
            availability = ContentAvailability.INSTANT,
            owner_id=current_user.id
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
            process_data_from_origin, origin=content.origin, content_id=content.id, db=db
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

    filename = content.origin.split("/")[-1]
    url = f"{settings.IPFS_HTTP_PROVIDER}/api/v0/get?arg={content.ipfs_cid}"
    print(url)
    client = httpx.AsyncClient()

    async def iterative_download(download_url, async_client):
        # download file with on-the-fly tar unpacking
        try:
            async with async_client.stream("POST", download_url) as response:
                start_bytes = []
                current_length = 0
                size_read_flag = False
                SIZE_OFFSET = 124  # start position of filesize bytes
                SZ_SIZE = 12  # length of filesize bytes
                HEADER_LENGTH = 512  # length of tar header
                async for chunk in response.aiter_bytes():
                    current_length += len(chunk)
                    if current_length < HEADER_LENGTH:
                        start_bytes += chunk
                        continue

                    if not size_read_flag:
                        start_bytes += chunk
                        filesize_oct_str = "".join(
                            [
                                chr(byte_code)
                                for byte_code in start_bytes[
                                                 SIZE_OFFSET: SIZE_OFFSET + SZ_SIZE - 1
                                                 ]
                            ]
                        )
                        filesize = int(filesize_oct_str, 8)
                        size_read_flag = True
                        yield bytes(start_bytes[HEADER_LENGTH:])
                        continue

                    if current_length > filesize + HEADER_LENGTH:
                        yield bytes(
                            chunk[
                            : (filesize + HEADER_LENGTH)
                              - (current_length - len(chunk))
                            ]
                        )
                        break
                    yield chunk
        except Exception as e:
            import traceback

            traceback.print_exc()
            log.error(f"download_content_file, {e=} {content.id=}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="IPFS provider failure",
            )

    return StreamingResponse(
        iterative_download(url, client),
        headers={"Content-Disposition": f"attachment;filename={filename}"},
    )
