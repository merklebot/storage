from fastapi_camelcase import CamelModel as BaseModel


class KeyBase(BaseModel):
    pass


class KeyCreate(KeyBase):
    pass


class KeyUpdate(KeyBase):
    pass


class KeyInDBBase(KeyBase):
    id: int
    aes_key: str
    owner_id: int

    class Config:
        orm_mode = True


class Key(KeyInDBBase):
    pass


class KeyInDB(KeyInDBBase):
    pass
