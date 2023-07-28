import datetime
import uuid

from storage.db.models.content import Content
from storage.db.models.filecoin import Car
from storage.db.models.tenant import Tenant
from storage.db.session import with_db
from storage.logging import log

MAX_FILES_SIZE = 1073741824 * 2  # 25GiB
MIN_FILES_SIZE = 1073741824 * 1  # 16GiB


class ContentPack:
    def __init__(self):
        self.contents = []
        self.files_size = 0
        self.uuid = str(uuid.uuid4())

    def can_add_content(self, content: Content):
        return self.files_size + content.ipfs_file_size < MAX_FILES_SIZE

    def is_enough_contents(self):
        return self.files_size > MIN_FILES_SIZE

    def add_content(self, content: Content):
        assert self.can_add_content(content), "Too big content size"
        self.contents.append(content)
        self.files_size += content.ipfs_file_size

    def to_json_request(self):
        return {
            "contents": [
                {"ipfs_cid": content.ipfs_cid, "ipfs_file_size": content.ipfs_file_size}
                for content in self.contents
            ],
            "uuid": self.uuid,
        }

    def __str__(self):
        return (
            f"ContentPack(content_number={len(self.contents)},"
            f" total_size={self.files_size})"
        )


async def start_content_processor():
    log.info("starting content processor...")

    with with_db() as db:
        tenants = db.query(Tenant).all()
    for tenant in tenants:
        content_pack = ContentPack()
        print(tenant.schema)
        with with_db(tenant_schema=tenant.schema) as tenant_db:
            contents = (
                tenant_db.query(Content)
                .filter(
                    Content.encrypted_file_cid is None,
                    Content.created_at >= datetime.datetime(2023, 5, 25, 0, 0, 0, 0),
                )
                .all()
            )
        for content in contents:
            if content_pack.can_add_content(content):
                content_pack.add_content(content)
            elif content_pack.is_enough_contents():
                print("prepared_content_pack", content_pack)

                car = Car(
                    pack_uuid=content_pack.uuid,
                    original_content_cids=[
                        content.ipfs_cid for content in content_pack.contents
                    ],
                    original_contents_size=content_pack.files_size,
                    tenant_name=tenant.schema,
                )

                with with_db() as db:
                    db.add(car)
                    db.commit()
                content_pack = ContentPack()

    print(content_pack)
