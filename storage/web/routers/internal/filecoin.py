import httpx
from fastapi import APIRouter, Depends
from fastapi_camelcase import CamelModel as BaseModel
from sqlalchemy.sql import case

from storage.db.models.content import Content, ContentAvailability
from storage.db.models.filecoin import Car, RestoreRequest, RestoreRequestStatus
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
    encrypted_contents: list[dict]


class StartRestoreProcessSchema(BaseModel):
    worker_instance: str


class FinishRestoreProcessSchema(BaseModel):
    worker_instance: str
    restore_request_id: int
    status: str


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


@router.post(".startRestoreProcess")
async def start_restore_process(
    start_restore_process_request: StartRestoreProcessSchema,
    authed=Depends(deps.get_app_by_admin_token),
):
    with with_db() as db:
        try:
            restore_request = (
                db.query(RestoreRequest)
                .filter(RestoreRequest.status == RestoreRequestStatus.PENDING)
                .with_for_update()
                .one()
            )
        except Exception as e:
            print(e.__traceback__)
            return {}
        restore_request.worker_instance = start_restore_process_request.worker_instance
        restore_request.status = RestoreRequestStatus.PROCESSING
        db.commit()
        db.refresh(restore_request)

    with with_db(tenant_schema=restore_request.tenant_name) as db:
        content = (
            db.query(Content).filter(Content.id == restore_request.content_id).first()
        )
    return {"original_cid": content.ipfs_cid, "restore_request_id": restore_request.id}


@router.post(".finishRestoreProcess")
async def finish_restore_process(
    finish_restore_process_request: FinishRestoreProcessSchema,
    authed=Depends(deps.get_app_by_admin_token),
):
    with with_db() as db:
        restore_request = (
            db.query(RestoreRequest)
            .filter(
                RestoreRequest.id == finish_restore_process_request.restore_request_id
                and RestoreRequest.worker_instance
                == finish_restore_process_request.worker_instance
            )
            .with_for_update()
            .one()
        )
        restore_request.status = finish_restore_process_request.status
        db.commit()
        db.refresh(restore_request)

    if finish_restore_process_request.status == RestoreRequestStatus.DONE:
        with with_db(tenant_schema=restore_request.tenant_name) as db:
            content = (
                db.query(Content)
                .filter(Content.id == restore_request.content_id)
                .first()
            )
            content.availability = ContentAvailability.INSTANT
            db.commit()
    if restore_request.webhook_url:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    restore_request.webhook_url,
                    json={
                        "restore_status": finish_restore_process_request.status,
                        "tenant_name": restore_request.tenant_name,
                        "content_id": restore_request.content_id,
                    },
                )
        except Exception as e:
            print(e.__traceback__)
            pass

    return {
        "status": "ok",
    }


@router.get(".getPreparedCars")
async def get_prepared_cars(authed=Depends(deps.get_app_by_admin_token)):
    with with_db() as db:
        cars = [
            {
                "pack_uuid": car.pack_uuid,
                "contents_size": car.original_contents_size,
                "root_cid": car.root_cid,
                "comm_p": car.comm_p,
                "car_size": car.car_size,
                "piece_size": car.piece_size,
            }
            for car in db.query(Car).filter(Car.comm_p.isnot(None)).all()
        ]

    return {"status": "ok", "cars": cars}


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
        content_encrypted_size_updates[encrypted_content["original_cid"]] = int(
            encrypted_content["encrypted_size"]
        )

    with with_db(tenant_schema=car.tenant_name) as tenant_db:
        tenant_db.query(Content).filter(
            Content.ipfs_cid.in_(content_encrypted_cid_updates)
        ).update(
            {
                Content.encrypted_file_cid: case(
                    content_encrypted_cid_updates, value=Content.ipfs_cid
                ),
                Content.encrypted_file_size: case(
                    content_encrypted_size_updates, value=Content.ipfs_cid
                ),
            },
            synchronize_session=False,
        )
        tenant_db.commit()

    with with_db() as db:
        car_in_db = db.query(Car).filter(Car.pack_uuid == pack_uuid).first()
        car_in_db.root_cid = root_cid
        car_in_db.comm_p = comm_p
        car_in_db.piece_size = piece_size
        car_in_db.car_size = car_size
        db.commit()

    return {"status": "ok"}
