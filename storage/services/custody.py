import aiohttp

from storage.config import settings


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

    async def start_content_encryption(self, original_cid, job_id):
        key = await self.create_key()
        print(original_cid)
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                f"{self.url}/content/methods/process_encryption",
                headers=self.headers,
                json={
                    "original_cid": original_cid,
                    "aes_key": key["aes_key"],
                    "webhook_url": f"{settings.SELF_URL}/jobs/{job_id}/webhooks/result",
                },
            ) as resp:
                print(resp.status)

    async def start_content_decryption(self, original_cid, aes_key, job_id):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.url}/content/methods/process_decryption",
                headers=self.headers,
                json={
                    "original_cid": original_cid,
                    "aes_key": aes_key,
                    "webhook_url": f"{settings.SELF_URL}/jobs/{job_id}/webhooks/result",
                },
            ) as resp:
                print(resp.status)


custody = CustodyClient(url=settings.CUSTODY_URL, api_key=settings.CUSTODY_API_KEY)
