from fastapi_camelcase import CamelModel as BaseModel


class PermissionBase(BaseModel):
    content_id: int


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    pass


class PermissionInDBBase(PermissionBase):
    id: int

    class Config:
        orm_mode = True


class Permission(PermissionInDBBase):
    pass


class PermissionInDB(PermissionInDBBase):
    pass
