import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from storage.db.base_class import Base


class PermissionKind(str, enum.Enum):
    READ = "read"


class Permission(Base):
    __tablename__ = "permissions"
    # ToDo: uniqueness constraint by (kind, content_id, assignee_id) combination
    # ToDo: content_owner != assignee constraint
    # ToDo: assignee and content exists constraint

    id = Column("id", Integer, primary_key=True, index=True)
    kind = Column("kind", Enum(PermissionKind), index=True, nullable=False)
    content_id = Column(
        "content_id", Integer, ForeignKey("tenant.contents.id"), nullable=False
    )
    content = relationship("Content", back_populates="permissions")
    assignee_id = Column(
        "assignee_id", Integer, ForeignKey("tenant.users.id"), nullable=False
    )
    assignee = relationship("User", back_populates="permissions")

    __table_args__ = ({"schema": "tenant"},)
