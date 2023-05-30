from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from storage.db.base_class import Base


class TokenForTenant(Base):
    __tablename__ = "tokens"

    id = Column("id", Integer, primary_key=True, index=True)
    hashed_token = Column("hashed_token", String(64), nullable=False, index=True)
    expiry = Column("expiry", TIMESTAMP, nullable=True, index=True)
    owner_id = Column("owner_id", Integer, ForeignKey("shared.tenants.id"))
    owner = relationship("Tenant", back_populates="tokens")

    __table_args__ = ({"schema": "shared"},)


Token = TokenForTenant


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column("id", Integer, primary_key=True, nullable=False)
    name = Column("name", String(256), nullable=False, index=True, unique=True)
    schema = Column("schema", String(256), nullable=False, unique=True)
    host = Column("host", String(256), nullable=False, unique=True)
    tokens = relationship(TokenForTenant, back_populates="owner")
    owner_email = Column("owner_email", String(256), nullable=True, unique=True)
    merklebot_user_id = Column("merklebot_user_id", String, nullable=True)

    __table_args__ = ({"schema": "shared"},)
