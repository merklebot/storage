from ipaddress import IPv4Address
from typing import Any, Literal

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    SERVER_HOST: AnyHttpUrl | IPv4Address | Literal["localhost"]
    SERVER_PORT: int
    SERVER_ROOT_PATH: str = ""

    LOGURU_LEVEL: str = "INFO"
    IPFS_HTTP_PROVIDER: AnyHttpUrl

    CUSTODY_URL: str
    CUSTODY_API_KEY: str

    SELF_URL: str

    WEB3_STORAGE_MANAGER_URL: AnyHttpUrl

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True


settings = Settings()
