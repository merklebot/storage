from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import URLType

from storage.db.base_class import Base
from storage.db.models.user import User


class Content(Base):
    __tablename__ = "contents"

    id = Column("id", Integer, primary_key=True, index=True)
    ipfs_cid = Column("ipfs_cid", String(256), nullable=True)
    origin = Column("origin", URLType, nullable=True)
    owner_id = Column("owner_id", Integer, ForeignKey("tenant.users.id"))
    owner = relationship(User, back_populates="contents")
    permissions = relationship("Permission", back_populates="content")

    __table_args__ = ({"schema": "tenant"},)
