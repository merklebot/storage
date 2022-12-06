from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.db.models import Content, Key, User
from storage.db.session import SessionLocal
from storage.logging import log
from storage.schemas import job as schemas
from storage.services.custody import custody
from storage.web import deps

router = APIRouter()


@router.get("/", response_model=list[schemas.Job])
async def read_jobs(
    *,
    db: dict = Depends(deps.get_fake_db),
):
    return list(db["jobs"].values())


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Job)
async def create_job(
    *,
    local_db: dict = Depends(deps.get_fake_db),
    db: SessionLocal = Depends(deps.get_db),
    job_in: schemas.JobCreate,
    current_user: User = Depends(deps.get_current_user),
):
    log.debug(f"create_job, {job_in=}")
    job = schemas.Job(
        id=max(local_db["jobs"].keys()) + 1 if local_db["jobs"].keys() else 0,
        **job_in.dict(),
    )

    local_db["jobs"][job.id] = job.dict()

    key = (
        db.query(Key)
        .filter(Key.id == job.key_id, Key.owner_id == current_user.id)
        .first()
    )
    content = (
        db.query(Content)
        .filter(Content.id == job.content_id, Content.owner_id == current_user.id)
        .first()
    )
    if job.kind == "encryption":
        log.debug(f"start content {content.id} encryption")
        await custody.start_content_encryption(content, key, job.id)
    elif job.kind == "decryption":
        log.debug(f"start content {content.id} decryption")
        await custody.start_content_decryption(content, key, job.id)

    return job


@router.get("/{job_id}", response_model=schemas.Job)
async def read_job_by_id(*, db: dict = Depends(deps.get_fake_db), job_id: int):
    log.debug(f"read_job_by_id, {job_id=}")
    try:
        return db["jobs"][job_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )


@router.post("/{job_id}/webhooks/result", response_model=schemas.Job)
async def mark_job_finished(
    *, db: dict = Depends(deps.get_fake_db), job_id: int, job_result: schemas.JobResult
):
    log.debug(f"read_job_by_id, {job_id=}")
    try:
        job = db["jobs"][job_id]
        job.update({"status": job_result.status, "result": job_result.result})
        db["jobs"][job_id] = job
        return job
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )


@router.patch("/{job_id}", response_model=schemas.Job)
async def update_job(
    *, db: dict = Depends(deps.get_fake_db), job_id: int, job_in: schemas.JobUpdate
):
    log.debug(f"update_job, {job_id=}, {job_in=}")
    if job_id not in db["jobs"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    job = db["jobs"][job_id]
    log.debug(job)
    job.update({k: v for k, v in job_in.dict().items() if v is not None})
    db["jobs"][job_id] = job
    return job
