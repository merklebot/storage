from fastapi_camelcase import CamelModel as BaseModel


class TenantBase(BaseModel):
    pass


class TenantCreate(TenantBase):
    pass


class TenantUpdate(TenantBase):
    pass


class TenantInDBBase(TenantBase):
    id: int

    class Config:
        orm_mode = True


class Tenant(TenantInDBBase):
    pass


class TenantInDB(TenantInDBBase):
    pass
