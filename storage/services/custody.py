import aiohttp

from storage.config import settings
from storage.logging import log


class CustodyClient:
    def __init__(self, url):
        self.url = url

    async def prepare_car_archive(self, content_pack):
        req = content_pack.to_json_request()
        log.info(f"preparing car for content pack {req}")

        log.info(f"{req}")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.url}/content/methods/encrypt_content_pack",
                json=req,
                timeout=2000,
            ) as resp:
                print(resp.status)
                res = await resp.json()
                return res


custody = CustodyClient(url=settings.CUSTODY_URL)
