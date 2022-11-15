from typing import List

from fastapi_camelcase import CamelModel as BaseModel

from storage.db.models.permission import PermissionKind


class PermissionWrapper:
    def __init__(self, permissions_list: List[str]):
        self.owner = "owner" in permissions_list
        self.read = "read" in permissions_list
        self.update = "update" in permissions_list


class PermissionBase(BaseModel):
    assignee_id: int
    content_id: int
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
