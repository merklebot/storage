from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from storage.db.models.tenant import Tenant
from storage.logging import log
from storage.schemas import tenant as schemas
from storage.web import deps

router = APIRouter()


@router.get("/", response_model=list[schemas.Tenant])
async def read_tenants(
    *,
    db: dict = Depends(deps.get_db),
):
    log.debug("read_tenants")
    tenants = db.query(Tenant).all()
    return tenants


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Tenant)
async def create_tenant(
    *, db: dict = Depends(deps.get_db), tenant_in: schemas.TenantCreate
):
    log.debug(f"create_tenant, {tenant_in=}")
    # ToDo: does not keep invariants, check storage.db.multitenancy.tenant_create
    tenant = Tenant(
        name=tenant_in.name,
        schema=tenant_in.name,
        host=tenant_in.name,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("/{tenant_id}", response_model=schemas.Tenant)
async def read_tenant_by_id(*, db: dict = Depends(deps.get_db), tenant_id: int):
    log.debug(f"read_tenant_by_id, {tenant_id=}")
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )
    return tenant


@router.put("/{tenant_id}", response_model=schemas.Tenant)
async def update_tenant(
    *,
    db: dict = Depends(deps.get_db),
    tenant_in: schemas.TenantUpdate,
    tenant_id: int,
):
    log.debug(f"update_tenant, {tenant_id=}, {tenant_in=}")
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )
    # ToDo: rename schema
    tenant.name = tenant_in.name
    tenant.host = tenant_in.name
    db.commit()
    db.refresh(tenant)
    return tenant
