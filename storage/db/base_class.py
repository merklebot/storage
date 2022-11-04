from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData(schema="tenant")
Base = declarative_base(metadata=metadata)
