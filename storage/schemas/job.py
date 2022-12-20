from typing import Any

from fastapi_camelcase import CamelModel as BaseModel
from pydantic_partial import create_partial_model

from storage.db.models.job import JobKind, JobStatus


class JobBase(BaseModel):
    content_id: int
    kind: JobKind
    config: Any


class JobResult(BaseModel):
    status: str
    result: dict | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(create_partial_model(JobBase)):
    pass


class JobInDBBase(JobBase):
    id: int
    status: JobStatus = JobStatus.CREATED

    class Config:
        orm_mode = True


class Job(JobInDBBase):
    pass


class JobInDB(JobInDBBase):
    pass
