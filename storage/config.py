from ipaddress import IPv4Address
from typing import Literal

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    SERVER_HOST: AnyHttpUrl | IPv4Address | Literal["localhost"]
    SERVER_PORT: int
    SERVER_ROOT_PATH: str = ""

    LOGURU_LEVEL: str = "INFO"
    IPFS_HTTP_PROVIDER: AnyHttpUrl

    CUSTODY_URL: str
    CUSTODY_API_KEY: str

    SELF_URL: str

    class Config:
        case_sensitive = True


settings = Settings()
