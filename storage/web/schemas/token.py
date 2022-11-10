from datetime import datetime

from fastapi_camelcase import CamelModel as BaseModel


class TokenBase(BaseModel):
    owner_id: int
    expiry: datetime | None = None


class TokenCreate(TokenBase):
    pass


class Token(TokenBase):
    id: int
    hashed_token: str

    class Config:
        orm_mode = True
