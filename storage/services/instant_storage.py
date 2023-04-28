import aioboto3

from storage.config import settings


async def upload_data_to_instant_storage(data, ipfs_cid: str):
    async with aioboto3.Session().client(
        service_name="s3",
        region_name=settings.INSTANT_STORAGE_REGION,
        endpoint_url=settings.INSTANT_STORAGE_ENDPOINT,
        aws_access_key_id=settings.INSTANT_STORAGE_ACCESS_KEY,
        aws_secret_access_key=settings.INSTANT_STORAGE_SECRET_ACCESS_KEY,
    ) as s3:
        await s3.put_object(
            Bucket=settings.INSTANT_STORAGE_BUCKET_NAME, Key=f"{ipfs_cid}", Body=data
        )
