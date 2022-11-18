from datetime import datetime

from fastapi_camelcase import CamelModel as BaseModel


class TokenBase(BaseModel):
    owner_id: int
    expiry: datetime | None = None


class TokenCreate(TokenBase):
    pass


class TokenUpdateExpiry(BaseModel):
    id: int
    expiry: datetime | None = None  # allow UTC timezone only


class TokenInDBBase(TokenBase):
    id: int

    class Config:
        orm_mode = True


class Token(TokenBase):
    id: int
    plain_token: str

    class Config:
        orm_mode = True


class TokenInDB(TokenInDBBase):
    pass
