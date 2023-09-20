from sqlalchemy import ARRAY, BigInteger, Column, Integer, String

from storage.db.base_class import Base, TimestampMixin


class RestoreRequestStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class Car(TimestampMixin, Base):
    __tablename__ = "cars"

    id = Column("id", Integer, primary_key=True, index=True)
    pack_uuid = Column("pack_uuid", String(64), nullable=False, index=True)
    tenant_name = Column("tenant_name", String(64), nullable=False, index=True)
    original_content_cids = Column("content_cids", ARRAY(String), nullable=True)
    original_contents_size = Column(
        "contents_size", BigInteger, nullable=True, index=True
    )

    root_cid = Column("root_cid", String(64), nullable=True, index=True)
    comm_p = Column("comm_p", String(64), nullable=True, index=True)
    car_size = Column("car_size", BigInteger, nullable=True, index=True)
    piece_size = Column("piece_size", BigInteger, nullable=True, index=True)

    __table_args__ = ({"schema": "shared"},)


class RestoreRequest(TimestampMixin, Base):
    __tablename__ = "restore_requests"

    id = Column("id", Integer, primary_key=True, index=True)

    tenant_name = Column("tenant_name", String(64), nullable=False, index=True)
    content_id = Column("content_id", Integer, nullable=False, index=True)
    status = Column("status", String(64), nullable=False, index=True)
    worker_instance = Column("worker_instance", String(64), nullable=True, index=True)
    webhook_url = Column("webhook_url", String(64), nullable=True, index=True)

    __table_args__ = ({"schema": "shared"},)
