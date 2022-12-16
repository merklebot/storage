import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from storage.db.base_class import Base


class JobKind(str, enum.Enum):
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    REPLICATE = "replicate"
    RESTORE = "restore"


class JobStatus(str, enum.Enum):
    CREATED = "created"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    INPROGRESS = "inprogress"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETE = "complete"


class Job(Base):
    __tablename__ = "jobs"

    id = Column("id", Integer, primary_key=True, index=True)
    content_id = Column(
        "content_id",
        Integer,
        ForeignKey("tenant.contents.id"),
        index=True,
        nullable=False,
    )
    kind = Column("kind", Enum(JobKind), index=True, nullable=False)
    status = Column("status", Enum(JobStatus), index=True, nullable=False)
    config = Column(
        "config",
        JSONB,
        nullable=False,
    )
    content = relationship("Content", back_populates="jobs")

    __table_args__ = ({"schema": "tenant"},)
