from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.db.models import Content, Job
from storage.db.models.tenant import Tenant
from storage.db.session import SessionLocal
from storage.logging import log
from storage.schemas import job as schemas
from storage.web import deps

router = APIRouter()


@router.get("/", response_model=list[schemas.Job])
async def read_jobs(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_tenant: Tenant = Depends(deps.get_current_tenant),
):
    """Read jobs created by the tenant."""

    log.debug(f"read_jobs, {current_tenant.id=}")
    jobs: list[Job] = db.query(Job).all()
    return jobs


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_description="Created",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not Found"},
    },
    response_model=schemas.Job,
)
async def create_job(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_tenant: Tenant = Depends(deps.get_current_tenant),
    job_in: schemas.JobCreate,
):
    """Order a new job."""

    log.debug(f"create_job, {job_in=}, {current_tenant.id=}")
    content_exists: bool = db.query(
        db.query(Content).filter(Content.id == job_in.content_id).exists()
    ).scalar()
    if not content_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    job = Job(**job_in.dict())
    db.add(job)
    db.commit()
    db.refresh(job)
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
