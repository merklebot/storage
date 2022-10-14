from typing import Generator

db = {
    "contents": {},
    "jobs": {},
    "keys": {},
    "permissions": {},
    "specifications": {},
    "tenants": {},
    "users": {},
}


def get_db() -> Generator:
    yield db
