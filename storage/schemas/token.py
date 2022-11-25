from datetime import datetime

from fastapi_camelcase import CamelModel as BaseModel
from pydantic import constr


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
    hashed_token: constr(max_length=64)

    class Config:
        orm_mode = True


class Token(TokenInDBBase):
    pass


class TokenSecret(TokenInDBBase):
    id: int
    plain_token: str


class TokenInDB(TokenInDBBase):
    pass
