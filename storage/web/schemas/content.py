from fastapi_camelcase import CamelModel as BaseModel
from pydantic import AnyHttpUrl


class ContentBase(BaseModel):
    filename: str | None = None
    ipfs_cid: str | None = None
    encryption_key_id: str | None = None
    owner_id: int | None = None


class ContentCreate(ContentBase):
    method: str | None = "external"
    url: AnyHttpUrl


class ContentUpdate(ContentBase):
    pass


class ContentInDBBase(ContentBase):
    id: int

    class Config:
        orm_mode = True


class Content(ContentInDBBase):
    pass


class ContentInDB(ContentInDBBase):
    pass
