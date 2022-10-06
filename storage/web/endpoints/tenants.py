from fastapi import APIRouter

from storage.web.schemas import tenant as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Tenant])
async def read_tenants():
    return []


@router.post("/", response_model=schemas.Tenant)
async def create_tenant(tenant_in: schemas.TenantCreate):
    print(f"create_tenant, {tenant_in=}")
    return schemas.Tenant(id=1)


@router.get("/{tenant_id}", response_model=schemas.Tenant)
async def read_tenant_by_id(tenant_id: int):
    print(f"read_tenant_by_id, {tenant_id=}")
    return schemas.Tenant(id=tenant_id)


@router.put("/{tenant_id}", response_model=schemas.Tenant)
async def update_tenant(tenant_id: int, tenant_in: schemas.TenantUpdate):
    print(f"update_tenant, {tenant_id=}, {tenant_in=}")
    return schemas.Tenant(id=tenant_id)
