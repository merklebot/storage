from sqlalchemy import TIMESTAMP, Column, MetaData, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr

metadata = MetaData(schema="tenant")
Base = declarative_base(metadata=metadata)


class TimestampMixin(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
