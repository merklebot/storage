from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from storage.web.schemas import tenant as schemas

router = APIRouter()


db = {}


@router.get("/", response_model=list[schemas.Tenant])
async def read_tenants():
    return list(db.values())


@router.post("/", response_model=schemas.Tenant)
async def create_tenant(tenant_in: schemas.TenantCreate):
    print(f"create_tenant, {tenant_in=}")
    tenant = schemas.Tenant(
        id=max(db.keys()) + 1 if db.keys() else 0,
        **tenant_in.dict(),
    )
    db[tenant.id] = tenant.dict()
    return tenant


@router.get("/{tenant_id}", response_model=schemas.Tenant)
async def read_tenant_by_id(tenant_id: int):
    print(f"read_tenant_by_id, {tenant_id=}")
    try:
        return db[tenant_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Tenant not found")


@router.put("/{tenant_id}", response_model=schemas.Tenant)
async def update_tenant(tenant_id: int, tenant_in: schemas.TenantUpdate):
    print(f"update_tenant, {tenant_id=}, {tenant_in=}")
    if tenant_id not in db:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant = db[tenant_id]
    tenant.update(tenant_in.dict())
    db[tenant_id] = tenant
    return tenant
