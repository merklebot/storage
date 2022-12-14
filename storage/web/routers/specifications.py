from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.schemas import specification as schemas
from storage.web import deps

router = APIRouter()


@router.get("/", response_model=list[schemas.Specification])
async def read_specifications(
    *,
    db: dict = Depends(deps.get_fake_db),
):
    return list(db["specification"].values())


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.Specification
)
async def create_specification(
    *,
    db: dict = Depends(deps.get_fake_db),
    specification_in: schemas.SpecificationCreate,
):
    log.debug(f"create_specification, {specification_in=}")
    specification = schemas.Specification(
        id=max(db["specification"].keys()) + 1 if db["specification"].keys() else 0,
        **specification_in.dict(),
    )
    db["specification"][specification.id] = specification.dict()
    return specification


@router.get("/{specification_id}", response_model=schemas.Specification)
async def read_specification_by_id(
    *, db: dict = Depends(deps.get_fake_db), specification_id: int
):
    log.debug(f"read_specification_by_id, {specification_id=}")
    try:
        return db["specification"][specification_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Specification not found"
        )


@router.put("/{specification_id}", response_model=schemas.Specification)
async def update_specification(
    *,
    db: dict = Depends(deps.get_fake_db),
    specification_id: int,
    specification_in: schemas.SpecificationUpdate,
):
    log.debug(f"update_specification, {specification_id=}, {specification_in=}")
    if specification_id not in db["specification"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Specification not found"
        )
    specification = db["specification"][specification_id]
    log.debug(specification)
    specification.update(
        {k: v for k, v in specification_in.dict().items() if v is not None}
    )
    db["specification"][specification_id] = specification
    return specification
