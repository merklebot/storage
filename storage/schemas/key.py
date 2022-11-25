from fastapi_camelcase import CamelModel as BaseModel


class KeyBase(BaseModel):
    user_id: int


class KeyCreate(KeyBase):
    pass


class KeyUpdate(KeyBase):
    pass


class KeyInDBBase(KeyBase):
    id: int

    class Config:
        orm_mode = True


class Key(KeyInDBBase):
    pass


class KeyInDB(KeyInDBBase):
    pass
