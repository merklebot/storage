from ipaddress import IPv4Address
from typing import Any, Literal

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator

certificate = """
-----BEGIN CERTIFICATE-----
MIIE2TCCAsGgAwIBAgIDAeJAMA0GCSqGSIb3DQEBCwUAMCYxDjAMBgNVBAoTBWFk
bWluMRQwEgYDVQQDDAtjZXJ0XzE5bHQwZDAeFw0yMzA0MjkwODQ3MTlaFw00MzA0
MjkwODQ3MTlaMCYxDjAMBgNVBAoTBWFkbWluMRQwEgYDVQQDDAtjZXJ0XzE5bHQw
ZDCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAM6O+xs7vL5suMgFVLMM
J2KgEW8c4/HAxAoFWIRKcPXOqHxLxHZUWNavgurLbCf0ugeAfWazvKhefqmqwOlY
xTc33pV9sQd5EKV7tSOXdhJlFplnSvXa6qG/5EZS/9yRnwGuxdmsbCAPka1AFizU
aLYN/GrdUyEl05KgqE4kQzifIJp/fD4ybuYrC5uFYf9N/ybLFtgCRcyQkBGX/VQr
pSWWzbgbiNtZ/iSNAZ6TqpeGcg3dSZ4RvirFqcpAe1jFsmwATIcbmnVjbiZaxDWJ
hlia7dDwrL5ngZnAZz8NXY5Myxt893pXpCM7ELC7I8I5rnChU40Zbh491koz+evP
jFc9hmxGQRWrnUa3doNkgTwWhvMCXlayxOnR04+y91pLKP6jVs3kfUQY5TlfBkdF
zNqse13KbG5Gd+7xISi045TJos3hU6u67eHVY9XEycAo74Yz5fCH5Uo8A6eeyIrA
4s/zqyE4zUz1ByCsrH8NpBa31jxdf6SMbd5xht4YZ3HYdB8BW27SHcDtONnjRayL
cXmLUiSGNtJi5j+sZW5iVCHZlHx3VkpoACLug9vbUe0wd/ZqfMpukrSKWRAat7pP
TxESYot3Qk0g7DkcINSE3rc/+IUc2MLd/LCNsn4LJ5e5u/06E/IobYz9LvLZu85U
+FCaYGAT4hE0DdbDkt5FtB11AgMBAAGjEDAOMAwGA1UdEwEB/wQCMAAwDQYJKoZI
hvcNAQELBQADggIBABw/F3VoeKc1rY3G5Wmsxf5HbJ0Gn6paApdEUAEsugZGIqHU
cYKXb4N15Du/4xJETPKkc6z+UefXtN4kZ8NajuED0wyfNr6GXYxHOi/bZKCspY8v
gXcMyMonIhoZDPcWnOpuFixVikH750k0CbIpPu+qeBKHdducWbnqn4+F8GVcM6OM
NSTfbfCjt7tKb8V+5/nDZg1dPfIrRUG+CbF8UftzAxCwxwNHsj7VnmdmvvSDpkoU
dhHyeQ6u7jvuqFtFvSwumadqFZbCL9SFHmci+zkEWsI99/9Sg8Ct6+yw24+bTtRs
sfU7xv5GWy4eVkfoTcT4y/q2cqjqLDT0IN9XKyBv4KVDxmD90qxV4rqed/NM8jv1
OLI3p66Aq7Esp6BEVwgUhuT7HgzXFsFNsHVvRtSXeoejptl47Ysz/196qucPdFro
6dg2t8YcOCAQRj/0+nlgBK77UKPA7gAhee2Dml8xZH3x21/f+zxWBEOyH17YlP0t
Nk0+nbxu+NmiLVQ4OVgTO71erV/8tQn/QscDcYCoTE9N64AbJzkZvQ5JfFgYKwIT
mcwa/7dlMfcg0A3hP+g5XMnYoHw9FPDjzLhMpn8F7+MS2nWgBmdlui/Ue437cu0W
sLhaJbOxxxZ0LT47AqKAFfhiigD0OwWO13ZRkGhSYRsACHsVEZHRNtImPm5+
-----END CERTIFICATE-----"""


class Settings(BaseSettings):
    SERVER_HOST: AnyHttpUrl | IPv4Address | Literal["localhost"]
    SERVER_PORT: int
    SERVER_ROOT_PATH: str = ""

    LOGURU_LEVEL: str = "INFO"
    IPFS_HTTP_PROVIDER: AnyHttpUrl
    ENCRYPTED_IPFS_HTTP_PROVIDER: AnyHttpUrl

    CUSTODY_URL: str
    CUSTODY_API_KEY: str

    SELF_URL: str

    WEB3_STORAGE_MANAGER_URL: AnyHttpUrl

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    INSTANT_STORAGE_REGION: str
    INSTANT_STORAGE_ENDPOINT: str
    INSTANT_STORAGE_ACCESS_KEY: str
    INSTANT_STORAGE_SECRET_ACCESS_KEY: str
    INSTANT_STORAGE_BUCKET_NAME: str

    CASDOOR_ENDPOINT: str
    CASDOOR_CLIENT_ID: str
    CASDOOR_CLIENT_SECRET: str
    CASDOOR_ORG_NAME: str
    CASDOOR_APPLICATION_NAME: str
    CASDOOR_CERTIFICATE = certificate

    ADMIN_TOKEN: str

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
