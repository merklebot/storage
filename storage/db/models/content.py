import enum

from sqlalchemy import BigInteger, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import URLType

from storage.db.base_class import Base, TimestampMixin
from storage.db.models.user import User


class ContentAvailability(str, enum.Enum):
    INSTANT = "instant"
    ENCRYPTED = "encrypted"
    ARCHIVE = "archive"
    ABSENT = "absent"


class Content(TimestampMixin, Base):
    __tablename__ = "contents"

    id = Column("id", Integer, primary_key=True, index=True)
    ipfs_cid = Column("ipfs_cid", String(256), nullable=True)
    encrypted_file_cid = Column("encrypted_file_cid", String(256), nullable=True)
    encrypted_file_size = Column("encrypted_file_size", BigInteger, nullable=True)
    availability = Column("availability", Enum(ContentAvailability), nullable=False)
    origin = Column("origin", URLType, nullable=True)
    owner_id = Column("owner_id", Integer, ForeignKey("tenant.users.id"))
    owner = relationship(User, back_populates="contents")
    permissions = relationship("Permission", back_populates="content")
    jobs = relationship("Job", back_populates="content")

    __table_args__ = ({"schema": "tenant"},)
