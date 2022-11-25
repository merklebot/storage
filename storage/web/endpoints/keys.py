from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web import deps
from storage.schemas import key as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Key])
async def read_keys(
    *,
    db: dict = Depends(deps.get_fake_db),
):
    return list(db["keys"].values())


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Key)
async def create_key(
    *, db: dict = Depends(deps.get_fake_db), key_in: schemas.KeyCreate
):
    log.debug(f"create_key, {key_in=}")
    key = schemas.Key(
        id=max(db["keys"].keys()) + 1 if db["keys"].keys() else 0,
        **key_in.dict(),
    )
    db["keys"][key.id] = key.dict()
    return key


@router.get("/{id}", response_model=schemas.Key)
async def read_key_by_id(*, db: dict = Depends(deps.get_fake_db), id: int):
    log.debug(f"read_key_by_id, {id=}")
    try:
        return db["keys"][id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Key not found"
        )


@router.delete("/{id}", response_model=schemas.Key)
async def delete_key(*, db: dict = Depends(deps.get_fake_db), id: int):
    log.debug(f"delete_key, {id=}")
    if id not in db["keys"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Key not found"
        )
    key = db["keys"][id]
    del db["keys"][id]
    return key
