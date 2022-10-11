from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web.schemas import user as schemas

router = APIRouter()


db = {}


@router.get("/", response_model=list[schemas.User])
async def read_users():
    return list(db.values())


@router.post("/", response_model=schemas.User)
async def create_user(user_in: schemas.UserCreate):
    log.debug(f"create_user, {user_in=}")
    user = schemas.User(
        id=max(db.keys()) + 1 if db.keys() else 0,
        **user_in.dict(),
    )
    db[user.id] = user.dict()
    return user


@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(user_id: int):
    log.debug(f"read_user_by_id, {user_id=}")
    try:
        return db[user_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="User not found")


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user_in: schemas.UserUpdate):
    log.debug(f"update_user, {user_id=}, {user_in=}")
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    user = db[user_id]
    user.update(user_in.dict())
    db[user_id] = user
    return user


@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(user_id: int):
    log.debug(f"delete_user, {user_id=}, {db=}")
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    user = db[user_id]
    del db[user_id]
    return user
