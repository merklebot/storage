from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from storage.db.base_class import Base
from storage.db.models.user import User


class Key(Base):
    __tablename__ = "keys"

    id = Column("id", Integer, primary_key=True, index=True)
    aes_key = Column("aes_key", String, nullable=False)
    owner_id = Column("owner_id", Integer, ForeignKey("tenant.users.id"))
    owner = relationship(User, back_populates="keys")
    __table_args__ = ({"schema": "tenant"},)
