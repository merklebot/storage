import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from storage.db.base_class import Base


class PermissionKind(enum.Enum):
    READ = 1


class Permission(Base):
    __tablename__ = "permissions"

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
