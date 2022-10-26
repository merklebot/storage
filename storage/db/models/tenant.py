from sqlalchemy import Column, Integer

from storage.db.base_class import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
