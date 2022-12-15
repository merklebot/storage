from fastapi_camelcase import CamelModel as BaseModel
from pydantic import AnyHttpUrl


class ContentBase(BaseModel):
    pass


class ContentCreate(ContentBase):
    origin: AnyHttpUrl


class ContentUpdate(ContentBase):
    pass


class ContentInDBBase(ContentBase):
    id: int
    origin: AnyHttpUrl
    ipfs_cid: str | None = None
    encrypted_file_cid: str | None = None
    owner_id: int | None = None

    class Config:
        orm_mode = True


class Content(ContentInDBBase):
    pass


class ContentInDB(ContentInDBBase):
    pass
