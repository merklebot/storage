from fastapi_camelcase import CamelModel as BaseModel
from pydantic import AnyHttpUrl
from pydantic_partial import create_partial_model


class JobBase(BaseModel):
    tenant_id: int
    kind: str
    aes_key: str | None = None
    content_id: int | None = None
    original_cid: str | None = None
    status: str | None = "created"
    on_status_update: AnyHttpUrl | None = None
    result: dict | None = None


class JobResult(BaseModel):
    status: str
    result: dict | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(create_partial_model(JobBase)):
    pass


class JobInDBBase(JobBase):
    id: int

    class Config:
        orm_mode = True


class Job(JobInDBBase):
    pass


class JobInDB(JobInDBBase):
    pass
