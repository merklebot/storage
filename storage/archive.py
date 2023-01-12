import httpx

from storage.config import settings
from storage.logging import log


async def replicate(cid: str, filesize: int) -> None:
    request_data = {
        "cid": cid,
        "filesize": filesize,
    }
    log.debug(f"web3_storage_manager content.add request {request_data}")
    async with httpx.AsyncClient(
        base_url=settings.WEB3_STORAGE_MANAGER_URL,
    ) as client:
        response = await client.post("/content.add", json=request_data)
        log.debug(f"{response=}")


async def restore(cid: str) -> None:
    log.debug(f"{cid=}")
    async with httpx.AsyncClient(
        base_url=settings.IPFS_HTTP_PROVIDER,
    ) as client:
        response = await client.post(
            "/api/v0/pin/add",
            params={
                "arg": cid,
            },
        )
        log.debug(f"{response=}")
