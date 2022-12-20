from storage.logging import log
from storage.services.custody import custody


async def encrypt(tenant, job_id, aes_key, ipfs_cid) -> None:
    log.debug(f"{tenant=}, {job_id=}, {aes_key=}, {ipfs_cid=}")
    await custody.start_content_encryption(tenant, job_id, aes_key, ipfs_cid)


async def decrypt():
    ...
