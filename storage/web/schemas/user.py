from fastapi_camelcase import CamelModel as BaseModel


class UserBase(BaseModel):
    tenant_id: int


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: int

    class Config:
        orm_mode = True


class User(UserInDBBase):
    tenant_id: int


class UserInDB(UserInDBBase):
    pass
