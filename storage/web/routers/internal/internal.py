from fastapi import APIRouter

import storage.web.routers.internal.filecoin as filecoin
import storage.web.routers.internal.tenants as tenants
import storage.web.routers.internal.users as users

router = APIRouter()
router.include_router(users.router, prefix="/users")
router.include_router(tenants.router, prefix="/tenants")
router.include_router(filecoin.router, prefix="/filecoin")
