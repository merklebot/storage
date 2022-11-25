from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.logging import log
from storage.web import deps
from storage.schemas import tenant as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Tenant])
async def read_tenants(
    *,
    db: dict = Depends(deps.get_fake_db),
):
    return list(db["tenants"].values())


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Tenant)
async def create_tenant(
    *, db: dict = Depends(deps.get_fake_db), tenant_in: schemas.TenantCreate
):
    log.debug(f"create_tenant, {tenant_in=}")
    tenant = schemas.Tenant(
        id=max(db["tenants"].keys()) + 1 if db["tenants"].keys() else 0,
        **tenant_in.dict(),
    )
    db["tenants"][tenant.id] = tenant.dict()
    return tenant


@router.get("/{tenant_id}", response_model=schemas.Tenant)
async def read_tenant_by_id(*, db: dict = Depends(deps.get_fake_db), tenant_id: int):
    log.debug(f"read_tenant_by_id, {tenant_id=}")
    try:
        return db["tenants"][tenant_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )


@router.put("/{tenant_id}", response_model=schemas.Tenant)
async def update_tenant(
    *,
    db: dict = Depends(deps.get_fake_db),
    tenant_id: int,
    tenant_in: schemas.TenantUpdate,
):
    log.debug(f"update_tenant, {tenant_id=}, {tenant_in=}")
    if tenant_id not in db["tenants"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )
    tenant = db["tenants"][tenant_id]
    tenant.update(tenant_in.dict())
    db["tenants"][tenant_id] = tenant
    return tenant
