from fastapi_camelcase import CamelModel as BaseModel


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: int
    tenant_id: int

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    pass
