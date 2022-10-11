from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web.schemas import key as schemas

router = APIRouter()


db = {}


@router.get("/", response_model=list[schemas.Key])
async def read_keys():
    return list(db.values())


@router.post("/", response_model=schemas.Key)
async def create_key(key_in: schemas.KeyCreate):
    log.debug(f"create_key, {key_in=}")
    key = schemas.Key(
        id=max(db.keys()) + 1 if db.keys() else 0,
        **key_in.dict(),
    )
    db[key.id] = key.dict()
    return key


@router.get("/{id}", response_model=schemas.Key)
async def read_key_by_id(id: int):
    log.debug(f"read_key_by_id, {id=}")
    try:
        return db[id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Key not found")


@router.delete("/{id}", response_model=schemas.Key)
async def delete_key(id: int):
    log.debug(f"delete_key, {id=}")
    if id not in db:
        raise HTTPException(status_code=404, detail="Key not found")
    key = db[id]
    del db[id]
    return key
