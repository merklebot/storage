import secrets

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_api_key():
    return secrets.token_urlsafe(64)


def verify_api_key(plain_api_key, hashed_api_key):
    return pwd_context.verify(plain_api_key, hashed_api_key)


def get_api_key_hash(api_key: str):
    return pwd_context.hash(api_key)
