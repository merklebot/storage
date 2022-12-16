import aiohttp

from storage.config import settings
from storage.db.models import Content, Key


class CustodyClient:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.headers = {"Authorization": f"bearer {self.api_key}"}

    async def create_key(self):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                f"{self.url}/keys/",
                headers=self.headers,
                json={},
            ) as resp:
                key = await resp.json()
                return key

    async def start_content_encryption(self, job_id, aes_key, ipfs_cid):
        print(ipfs_cid)
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                f"{self.url}/content/methods/process_encryption",
                headers=self.headers,
                json={
                    "original_cid": ipfs_cid,
                    "aes_key": aes_key,
                    "webhook_url": f"{settings.SELF_URL}/jobs/{job_id}/webhooks/result",
                },
            ) as resp:
                print(resp.status)

    async def start_content_decryption(self, content: Content, key: Key, job_id):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.url}/content/methods/process_decryption",
                headers=self.headers,
                json={
                    "original_cid": content.ipfs_cid,
                    "aes_key": key.aes_key,
                    "webhook_url": f"{settings.SELF_URL}/jobs/{job_id}/webhooks/result",
                },
            ) as resp:
                print(resp.status)


custody = CustodyClient(url=settings.CUSTODY_URL, api_key=settings.CUSTODY_API_KEY)
