import enum

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import URLType

from storage.db.base_class import Base, TimestampMixin
from storage.db.models.user import User


class ContentAvailability(str, enum.Enum):
    PENDING = "pending"
    INSTANT = "instant"
    ENCRYPTED = "encrypted"
    ARCHIVE = "archive"
    ABSENT = "absent"


class Content(TimestampMixin, Base):
    __tablename__ = "contents"

    id = Column("id", Integer, primary_key=True, index=True)
    filename = Column("filename", String, nullable=True)
    ipfs_cid = Column("ipfs_cid", String(256), nullable=True)
    ipfs_file_size = Column("ipfs_file_size", BigInteger, nullable=True)
    encrypted_file_cid = Column("encrypted_file_cid", String(256), nullable=True)
    encrypted_file_size = Column("encrypted_file_size", BigInteger, nullable=True)
    availability = Column("availability", Enum(ContentAvailability), nullable=False)
    key = Column("key", String, nullable=True)
    instant_till = Column(
        "instant_till", TIMESTAMP, nullable=True, server_default=func.now()
    )
    is_instant = Column("is_instant", Boolean, nullable=True)
    is_filecoin = Column("is_filecoin", Boolean, nullable=True)

    origin = Column("origin", URLType, nullable=True)
    owner_id = Column("owner_id", Integer, ForeignKey("tenant.users.id"))
    owner = relationship(User, back_populates="contents")
    permissions = relationship("Permission", back_populates="content")
    jobs = relationship("Job", back_populates="content")

    __table_args__ = ({"schema": "tenant"},)
