from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web.schemas import job as schemas

router = APIRouter()


db = {}


@router.get("/", response_model=list[schemas.Job])
async def read_jobs():
    return list(db.values())


@router.post("/", response_model=schemas.Job, status_code=status.HTTP_201_CREATED)
async def create_job(job_in: schemas.JobCreate):
    log.debug(f"create_job, {job_in=}")
    job = schemas.Job(
        id=max(db.keys()) + 1 if db.keys() else 0,
        **job_in.dict(),
    )
    db[job.id] = job.dict()
    return job


@router.get("/{job_id}", response_model=schemas.Job)
async def read_job_by_id(job_id: int):
    log.debug(f"read_job_by_id, {job_id=}")
    try:
        return db[job_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")


@router.patch("/{job_id}", response_model=schemas.Job)
async def update_job(job_id: int, job_in: schemas.JobUpdate):
    log.debug(f"update_job, {job_id=}, {job_in=}")
    if job_id not in db:
        raise HTTPException(status_code=404, detail="Job not found")
    job = db[job_id]
    log.debug(job)
    job.update({k: v for k, v in job_in.dict().items() if v is not None})
    db[job_id] = job
    return job
