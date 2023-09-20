from datetime import datetime

from fastapi_camelcase import CamelModel as BaseModel
from pydantic import AnyHttpUrl

from storage.db.models.content import ContentAvailability


class ContentBase(BaseModel):
    pass


class ContentCreate(ContentBase):
    origin: AnyHttpUrl


class ContentRestoreRequest(BaseModel):
    restore_days: int
    webhook_url: AnyHttpUrl | None


class ContentUpdate(ContentBase):
    pass


class ContentInDBBase(ContentBase):
    id: int
    filename: str | None = None
    origin: AnyHttpUrl | None = None
    ipfs_cid: str | None = None
    ipfs_file_size: int | None = None
    encrypted_file_cid: str | None = None
    availability: ContentAvailability
    owner_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Content(ContentInDBBase):
    pass


class ContentInDB(ContentInDBBase):
    pass
