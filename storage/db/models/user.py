from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from storage.db.base_class import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, nullable=False)
    tokens = relationship("Token", back_populates="owner")
    contents = relationship("Content", back_populates="owner")
    keys = relationship("Key", back_populates="owner")
    permissions = relationship("Permission", back_populates="assignee")

    __table_args__ = ({"schema": "tenant"},)
