import httpx

from storage.config import settings
from storage.logging import log


async def replicate(cid: str) -> None:
    async with httpx.AsyncClient(
        base_url=settings.IPFS_HTTP_PROVIDER,
    ) as client:
        response = await client.post(
            "/api/v0/add",
            params={
                "arg": cid,
            },
        )
        log.debug(f"{response=}")
        size = int(response.json()["CumulativeSize"])
    async with httpx.AsyncClient(
        base_url=settings.WEB3_STORAGE_MANAGER_URL,
    ) as client:
        response = await client.post(
            "/content.add",
            data={
                "cid": cid,
                "fileSize": size,
            },
        )
        log.debug(f"{response=}")
