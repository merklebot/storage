from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_camelcase import CamelModel as BaseModel

from storage.db.models.tenant import Tenant
from storage.db.multitenancy import tenant_create
from storage.db.session import with_db
from storage.web import deps

router = APIRouter()


class NewTenantSchema(BaseModel):
    tenant_name: str
    merklebot_user_id: str


@router.post(".add")
async def add_tenant(
    new_tenant: NewTenantSchema, authed=Depends(deps.get_app_by_admin_token)
):
    with with_db() as db:
        tenant = db.query(Tenant).filter(Tenant.name == new_tenant.tenant_name).first()
    if tenant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Tenant already exists"
        )

    tenant = Tenant(
        name=new_tenant.tenant_name,
        schema=new_tenant.tenant_name,
        host=new_tenant.tenant_name.replace("_", "-"),
        merklebot_user_id=new_tenant.merklebot_user_id,
    )
    tenant = tenant_create(tenant)
    return {"status": "ok", "result": tenant}


@router.get(".list")
async def list_tenants(authed=Depends(deps.get_app_by_admin_token)):
    with with_db() as db:
        tenants = db.query(Tenant).all()
    return {"status": "ok", "tenants": tenants}
