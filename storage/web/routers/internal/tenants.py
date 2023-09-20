from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_camelcase import CamelModel as BaseModel
from sqlalchemy.sql import func

from storage.db.models import Content
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
    tenant_name = new_tenant.tenant_name.lower()
    with with_db() as db:
        tenant = db.query(Tenant).filter(Tenant.name == tenant_name).first()
    if tenant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Tenant already exists"
        )

    tenant = Tenant(
        name=tenant_name,
        schema=tenant_name,
        host=tenant_name.replace("_", "-"),
        merklebot_user_id=new_tenant.merklebot_user_id,
    )
    tenant = tenant_create(tenant)
    return {"status": "ok", "result": tenant}


@router.get(".list")
async def list_tenants(authed=Depends(deps.get_app_by_admin_token)):
    with with_db() as db:
        tenants = db.query(Tenant).all()
    return {"status": "ok", "tenants": tenants}


@router.get(".getStats")
async def get_stats(tenant_name: str, authed=Depends(deps.get_app_by_admin_token)):
    with with_db(tenant_schema=tenant_name) as db:
        contents_number = db.query(Content).count()
        contents_funcs = db.query(
            func.sum(Content.ipfs_file_size).label("sum_ipfs_file_size")
        ).first()
    return {
        "contents_number": contents_number,
        "contents_size": contents_funcs["sum_ipfs_file_size"],
    }
