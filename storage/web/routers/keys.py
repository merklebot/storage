from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.db.models import Key, User
from storage.db.session import SessionLocal
from storage.logging import log
from storage.schemas import key as schemas
from storage.services.custody import custody
from storage.web import deps

router = APIRouter()


@router.get("/", response_model=list[schemas.Key])
async def read_keys(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    log.debug(f"read_keys, {current_user.id=}")

    keys = db.query(Key).filter(Key.owner_id == current_user.id).all()
    return keys


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Key)
async def create_key(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    log.debug(f"create_key, {current_user.id=}")
    custody_key = await custody.create_key()
    print(custody_key)
    key = Key(aes_key=custody_key["aes_key"], owner_id=current_user.id)
    db.add(key)
    db.commit()
    return key


@router.get("/{id}", response_model=schemas.Key)
async def read_key_by_id(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
):
    log.debug(f"read_key_by_id, {id=}")
    try:
        return (
            db.query(Key).filter(Key.id == id, Key.owner_id == current_user.id).first()
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Key not found"
        )


@router.delete("/{id}", response_model=schemas.Key)
async def delete_key(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
):
    log.debug(f"delete_key, {id=}")
    key = db.query(Key).filter(Key.id == id, Key.owner_id == current_user.id).first()

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Key not found"
        )
    db.delete(key)
    db.commit()
    return key
