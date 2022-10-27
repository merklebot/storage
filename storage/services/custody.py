import aiohttp

from storage.config import settings


class CustodyClient:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.headers = {"Authorization": f"bearer {self.api_key}"}

    async def prepare_content_encryption(self, content_id):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                f"{self.url}/content/{content_id}/methods/prepare_encryption",
                headers=self.headers,
                json={},
            ) as resp:
                print(resp.status)

    async def start_content_encryption(self, content_id, job_id):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                f"{self.url}/content/{content_id}/methods/process_encryption",
                headers=self.headers,
                json={
                    "webhook_url": f"{settings.SELF_URL}/jobs/{job_id}/webhooks/finish"
                },
            ) as resp:
                print(resp.status)

    async def start_content_decryption(self, content_id, job_id):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.url}/content/{content_id}/methods/process_encryption",
                headers=self.headers,
                json={
                    "webhook_url": f"{settings.SELF_URL}/jobs/{job_id}/webhooks/finish"
                },
            ) as resp:
                print(resp.status)


custody = CustodyClient(url=settings.CUSTODY_URL, api_key=settings.CUSTODY_API_KEY)
