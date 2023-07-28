from fastapi import APIRouter, Depends
from fastapi_camelcase import CamelModel as BaseModel
from sqlalchemy.sql import case

from storage.db.models.content import Content
from storage.db.models.filecoin import Car
from storage.db.session import with_db
from storage.web import deps

router = APIRouter()


class CarCreatedSchema(BaseModel):
    tenant_name: str
    pack_uuid: str
    root_cid: str
    comm_p: str
    car_size: int
    piece_size: int
    original_content_cids: list[str]
    original_contents_size: int
    encrypted_contents: list[dict]


@router.get(".getCarToProcess")
async def get_car_to_process(authed=Depends(deps.get_app_by_admin_token)):
    with with_db() as db:
        car = db.query(Car).filter(Car.comm_p.is_(None)).first()
    if car:
        return {
            "pack_uuid": car.pack_uuid,
            "tenant_name": car.tenant_name,
            "contents": car.original_content_cids,
        }


@router.post(".carCreated")
async def car_created_callback(
    car: CarCreatedSchema, authed=Depends(deps.get_app_by_admin_token)
):
    pack_uuid = car.pack_uuid
    root_cid = car.root_cid
    encrypted_contents = car.encrypted_contents
    comm_p = car.comm_p
    piece_size = car.piece_size
    car_size = car.car_size

    content_encrypted_cid_updates = {}
    content_encrypted_size_updates = {}
    for encrypted_content in encrypted_contents:
        content_encrypted_cid_updates[
            encrypted_content["original_cid"]
        ] = encrypted_content["encrypted_cid"]
        content_encrypted_size_updates[
            encrypted_content["original_cid"]
        ] = encrypted_content["encrypted_size"]

    with with_db(tenant_schema=car.tenant_name) as tenant_db:
        tenant_db.query(Content).filter(
            Content.ipfs_cid.in_(content_encrypted_cid_updates)
        ).update(
            {
                Content.encrypted_file_cid: case(
                    content_encrypted_cid_updates, value=Content.Content.ipfs_cid
                ),
                Content.encrypted_file_size: case(
                    content_encrypted_size_updates, value=Content.Content.ipfs_cid
                ),
            },
            synchronize_session=False,
        )

    with with_db() as db:
        car_in_db = db.query(Car).filter(Car.pack_uuid == pack_uuid).first()
        car_in_db.root_cid = root_cid
        car_in_db.comm_p = comm_p
        car_in_db.piece_size = piece_size
        car_in_db.car_size = car_size
        db.commit()

    return {"status": "ok"}
