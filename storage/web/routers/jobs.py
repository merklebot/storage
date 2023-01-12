from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.exceptions import HTTPException

from storage.archive import replicate, restore
from storage.db.models import Content, Job, Key
from storage.db.models.content import ContentAvailability
from storage.db.models.job import JobKind, JobStatus
from storage.db.models.tenant import Tenant
from storage.db.session import SessionLocal
from storage.encryption import decrypt, encrypt
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
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_404_NOT_FOUND: {"description": "Not Found"},
    },
    response_model=schemas.Job,
)
async def create_job(
    *,
    background_tasks: BackgroundTasks,
    db: SessionLocal = Depends(deps.get_db),
    current_tenant: Tenant = Depends(deps.get_current_tenant),
    job_in: schemas.JobCreate,
):
    """Order a new job."""

    log.debug(f"create_job, {job_in=}, {current_tenant.id=}")
    content: Content | None = (
        db.query(Content).filter(Content.id == job_in.content_id).first()
    )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    match job_in.kind:
        case JobKind.ENCRYPT | JobKind.DECRYPT:
            key: Key | None = (
                db.query(Key).filter(Key.id == job_in.config["keyId"]).first()
            )
            if not key:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Key not found"
                )
            if content.owner_id != key.owner_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Content and key owners are different",
                )
        case JobKind.REPLICATE | JobKind.RESTORE:
            if not content.encrypted_file_cid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Content is not encrypted",
                )
    job = Job(**job_in.dict(), status=JobStatus.CREATED)
    db.add(job)
    db.commit()
    db.refresh(job)
    match job_in.kind:
        case JobKind.ENCRYPT:
            print(f"{current_tenant.host=}")
            background_tasks.add_task(
                encrypt, current_tenant.host, job.id, key.aes_key, content.ipfs_cid
            )
        case JobKind.DECRYPT:
            background_tasks.add_task(
                decrypt, current_tenant.host, job.id, key.aes_key, content.ipfs_cid
            )
        case JobKind.REPLICATE:
            background_tasks.add_task(
                replicate, content.encrypted_file_cid, content.encrypted_file_size
            )
        case JobKind.RESTORE:
            background_tasks.add_task(restore, content.encrypted_file_cid)
    return job


@router.get(
    "/{job_id}",
    response_model=schemas.Job,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}},
)
async def read_job_by_id(
    *,
    db: SessionLocal = Depends(deps.get_db),
    current_tenant: Tenant = Depends(deps.get_current_tenant),
    job_id: int,
):
    """Read a certain job."""

    log.debug(f"read_job_by_id, {job_id=}, {current_tenant.id=}")
    job: Job | None = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return job


@router.post("/{job_id}/webhooks/result", response_model=schemas.Job)
async def webhook(
    *,
    db: SessionLocal = Depends(deps.get_db),
    job_id: int,
    job_result: schemas.JobResult,
):
    """For internal purposes only, don't use it."""

    log.debug(f"webhook, {job_id=}, {job_result=}")
    job = db.query(Job).filter(Job.id == job_id).first()
    content = db.query(Content).filter(Content.id == job.content_id).first()

    job.status = (
        JobStatus.COMPLETE if job_result.status == "finished" else JobStatus.FAILED
    )
    job.config = {**dict(job.config), **dict(result=job_result.result)}
    match job.kind:
        case JobKind.ENCRYPT:
            if job_result.status == "finished":
                content.encrypted_file_cid = job_result.result["encrypted_cid"]
                content.encrypted_file_size = int(job_result.result["encrypted_size"])
                db.commit()
                db.refresh(content)
        case JobKind.DECRYPT:
            if job_result.status == "finished":
                content.availability = ContentAvailability.INSTANT
                db.commit()
                db.refresh(content)

    db.commit()
    db.refresh(job)
    return job
