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
    """Read encryption keys the user owns."""

    log.debug(f"read_keys, {current_user.id=}")
    keys: list[Key] = db.query(Key).filter(Key.owner_id == current_user.id).all()
    return keys


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Key)
async def create_key(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Create new encryption key for the user."""

    log.debug(f"create_key, {current_user.id=}")
    custody_key = await custody.create_key()
    log.debug(f"{custody_key=}")
    key: Key = Key(aes_key=custody_key["aes_key"], owner_id=current_user.id)
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


@router.get(
    "/{key_id}",
    response_model=schemas.Key,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}},
)
async def read_key_by_id(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    key_id: int,
):
    """Read a certain encryption key the user owns."""

    log.debug(f"read_key_by_id, {key_id=}, {current_user.id=}")
    key: Key | None = db.query(Key).filter(Key.id == key_id).first()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Key not found"
        )
    if current_user.id != key.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return key


@router.delete(
    "/{key_id}",
    response_model=schemas.Key,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}},
)
async def delete_key(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    key_id: int,
):
    """Delete key the user owns."""

    log.debug(f"delete_key, {key_id=}, {current_user.id=}")
    key: Key | None = db.query(Key).filter(Key.id == key_id).first()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Key not found"
        )
    if current_user.id != key.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    db.delete(key)
    db.commit()
    return key
