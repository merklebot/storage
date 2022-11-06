from fastapi_camelcase import CamelModel as BaseModel
from enum import Enum


class PermissionKind(str, Enum):
    get = "get"
    update = "update"


class PermissionBase(BaseModel):
    content_id: int
    owner_id: int
    assignee_id: int
    kind: PermissionKind


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
