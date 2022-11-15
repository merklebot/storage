from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.services.custody import custody
from storage.web import deps
from storage.web.schemas import job as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Job])
async def read_jobs(
    *,
    db: dict = Depends(deps.get_fake_db),
):
    return list(db["jobs"].values())


@router.post("/", response_model=schemas.Job)
async def create_job(
    *, db: dict = Depends(deps.get_fake_db), job_in: schemas.JobCreate
):
    log.debug(f"create_job, {job_in=}")
    job = schemas.Job(
        id=max(db["jobs"].keys()) + 1 if db["jobs"].keys() else 0,
        **job_in.dict(),
    )

    db["jobs"][job.id] = job.dict()
    if job.kind == "encryption":
        log.debug(f"start content {job.content_id} encryption")
        await custody.start_content_encryption(job.content_id, job.id)
    elif job.kind == "decryption":
        log.debug(f"start content {job.content_id} decryption")
        await custody.start_content_decryption(job.content_id, job.id)

    return job


@router.get("/{job_id}", response_model=schemas.Job)
async def read_job_by_id(*, db: dict = Depends(deps.get_fake_db), job_id: int):
    log.debug(f"read_job_by_id, {job_id=}")
    try:
        return db["jobs"][job_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")


@router.get("/{job_id}/webhooks/finish", response_model=schemas.Job)
async def mark_job_finished(*, db: dict = Depends(deps.get_fake_db), job_id: int):
    log.debug(f"read_job_by_id, {job_id=}")
    try:
        job = db["jobs"][job_id]
        job.update({"status": "finished"})
        db["jobs"][job_id] = job
        return job
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")


@router.patch("/{job_id}", response_model=schemas.Job)
async def update_job(
    *, db: dict = Depends(deps.get_fake_db), job_id: int, job_in: schemas.JobUpdate
):
    log.debug(f"update_job, {job_id=}, {job_in=}")
    if job_id not in db["jobs"]:
        raise HTTPException(status_code=404, detail="Job not found")
    job = db["jobs"][job_id]
    log.debug(job)
    job.update({k: v for k, v in job_in.dict().items() if v is not None})
    db["jobs"][job_id] = job
    return job
