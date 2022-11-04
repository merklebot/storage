from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from storage.db.base_class import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column("id", Integer, primary_key=True, index=True)
    hashed_token = Column("hashed_token", String(64), nullable=False, index=True)
    expiry = Column("expiry", TIMESTAMP, nullable=True, index=True)
    owner_id = Column("owner_id", Integer, ForeignKey("shared.tenants.id"))
    owner = relationship("Tenant", back_populates="tokens")

    __table_args__ = ({"schema": "shared"},)
