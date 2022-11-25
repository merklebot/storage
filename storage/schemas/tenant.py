from fastapi_camelcase import CamelModel as BaseModel
from pydantic import constr


class TenantBase(BaseModel):
    name: constr(max_length=256)


class TenantCreate(TenantBase):
    pass


class TenantUpdate(TenantBase):
    pass


class TenantInDBBase(TenantBase):
    id: int
    host: constr(max_length=256)

    class Config:
        orm_mode = True


class Tenant(TenantInDBBase):
    pass


class TenantInDB(TenantInDBBase):
    pass
