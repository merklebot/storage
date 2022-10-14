from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web import deps
from storage.web.schemas import job as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Job])
async def read_jobs(
    *,
    db: dict = Depends(deps.get_db),
):
    return list(db["jobs"].values())


@router.post("/", response_model=schemas.Job, status_code=status.HTTP_201_CREATED)
async def create_job(*, db: dict = Depends(deps.get_db), job_in: schemas.JobCreate):
    log.debug(f"create_job, {job_in=}")
    job = schemas.Job(
        id=max(db["jobs"].keys()) + 1 if db["jobs"].keys() else 0,
        **job_in.dict(),
    )
    db["jobs"][job.id] = job.dict()
    return job


@router.get("/{job_id}", response_model=schemas.Job)
async def read_job_by_id(*, db: dict = Depends(deps.get_db), job_id: int):
    log.debug(f"read_job_by_id, {job_id=}")
    try:
        return db["jobs"][job_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")


@router.patch("/{job_id}", response_model=schemas.Job)
async def update_job(
    *, db: dict = Depends(deps.get_db), job_id: int, job_in: schemas.JobUpdate
):
    log.debug(f"update_job, {job_id=}, {job_in=}")
    if job_id not in db["jobs"]:
        raise HTTPException(status_code=404, detail="Job not found")
    job = db["jobs"][job_id]
    log.debug(job)
    job.update({k: v for k, v in job_in.dict().items() if v is not None})
    db["jobs"][job_id] = job
    return job
