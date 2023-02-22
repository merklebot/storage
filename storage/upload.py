import io

import httpx

from storage.config import settings
from storage.db.models import Content
from storage.db.models.content import ContentAvailability
from storage.logging import log


async def process_data_from_origin(origin: str, content_id: int, db) -> None:
    log.debug(f"fetching content {content_id} {origin}")
    async with httpx.AsyncClient() as client:
        r = await client.get(origin)
        content_file = io.BytesIO(r.content)
    async with httpx.AsyncClient(
        base_url=settings.IPFS_HTTP_PROVIDER,
    ) as client:
        response = await client.post(
            "/api/v0/add", params={'cid-version': 1}, files={"upload-files": content_file}
        )

    content: Content = db.query(Content).filter(Content.id == content_id).first()
    content.ipfs_cid = response.json()["Hash"]
    content.ipfs_file_size = int(response.json()["Size"])
    content.availability = ContentAvailability.INSTANT
    db.commit()
    db.refresh(content)
    log.debug(f"fetched {content=}")
