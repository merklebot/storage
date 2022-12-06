from sqlalchemy import TIMESTAMP, Column, Integer, func
from sqlalchemy.orm import relationship

from storage.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
    tokens = relationship("Token", back_populates="owner")
    contents = relationship("Content", back_populates="owner")
    keys = relationship("Key", back_populates="owner")
    permissions = relationship("Permission", back_populates="assignee")

    __table_args__ = ({"schema": "tenant"},)
