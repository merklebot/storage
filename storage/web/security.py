import json
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_api_key():
    return secrets.token_urlsafe(64)


def verify_api_key(plain_api_key, hashed_api_key):
    return pwd_context.verify(plain_api_key, hashed_api_key)


def get_api_key_hash(api_key: str):
    return pwd_context.hash(api_key)


def create_access_token(token_id: int, api_key: str):
    data = {"id": token_id, "val": api_key}
    payload = json.dumps(data).encode("utf-8")
    token = urlsafe_b64encode(payload)
    return token


def decode_access_token(token: str):
    payload = urlsafe_b64decode(token)
    data = json.loads(payload.decode("utf-8"))
    return data["id"], data["val"]
