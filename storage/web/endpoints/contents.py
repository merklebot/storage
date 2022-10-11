from fastapi import APIRouter, UploadFile
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web.schemas import content as schemas

router = APIRouter()


db = {}


@router.get("/", response_model=list[schemas.Content])
async def read_contents():
    log.debug("read_contents")
    return list(db.values())


@router.post("/", response_model=schemas.Content)
async def create_upload_content(content_in: UploadFile):
    log.debug(f"create_content, {content_in.filename=}")
    content = schemas.Content(
        id=max(db.keys()) + 1 if db.keys() else 0,
        filename=content_in.filename,
        ipfs_cid="",
        encryption_key="",
        owner_id=1,
        specification_id=1,
    )
    db[content.id] = content.dict()
    return content


@router.get("/{content_id}", response_model=schemas.Content)
async def read_content_by_id(content_id: int):
    log.debug(f"read_content_by_id, {content_id=}")
    try:
        return db[content_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Content not found")


@router.patch("/{content_id}", response_model=schemas.Content)
async def update_content(content_id: int, content_in: schemas.ContentUpdate):
    log.debug(f"update_content, {content_id=}, {content_in=}")
    if content_id not in db:
        raise HTTPException(status_code=404, detail="Content not found")
    content = db[content_id]
    content.update(content_in.dict())
    db[content_id] = content
    return content


@router.delete("/{content_id}", response_model=schemas.Content)
async def delete_content(content_id: int):
    log.debug(f"delete_content, {content_id=}")
    if content_id not in db:
        raise HTTPException(status_code=404, detail="Content not found")
    content = db[content_id]
    del db[content_id]
    return content
