from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web.schemas import specification as schemas

router = APIRouter()


db = {}


@router.get("/", response_model=list[schemas.Specification])
async def read_specifications():
    return list(db.values())


@router.post(
    "/", response_model=schemas.Specification, status_code=status.HTTP_201_CREATED
)
async def create_specification(specification_in: schemas.SpecificationCreate):
    log.debug(f"create_specification, {specification_in=}")
    specification = schemas.Specification(
        id=max(db.keys()) + 1 if db.keys() else 0,
        **specification_in.dict(),
    )
    db[specification.id] = specification.dict()
    return specification


@router.get("/{specification_id}", response_model=schemas.Specification)
async def read_specification_by_id(specification_id: int):
    log.debug(f"read_specification_by_id, {specification_id=}")
    try:
        return db[specification_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Specification not found")


@router.put("/{specification_id}", response_model=schemas.Specification)
async def update_specification(
    specification_id: int, specification_in: schemas.SpecificationUpdate
):
    log.debug(f"update_specification, {specification_id=}, {specification_in=}")
    if specification_id not in db:
        raise HTTPException(status_code=404, detail="Specification not found")
    specification = db[specification_id]
    log.debug(specification)
    specification.update(
        {k: v for k, v in specification_in.dict().items() if v is not None}
    )
    db[specification_id] = specification
    return specification
