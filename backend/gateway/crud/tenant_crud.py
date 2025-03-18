from backend.gateway.schema.tenant_schema import ITenantCreate, ITenantUpdate
from backend.common.models.tenant_model import Tenant
from backend.common.crud.base_crud import CRUDBase
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Optional

class CRUDTenant(CRUDBase[Tenant, ITenantCreate, ITenantUpdate, Tenant]):
    async def get_tenant_by_name(
        self, *, name: str, db_session: AsyncSession | None = None
    ) -> Optional[Tenant]:
        db_session = db_session or super().get_db_session()
        role = await db_session.execute(select(Tenant).where(Tenant.name == name))
        return role.scalar_one_or_none()

    async def get_root_tenant(self, db_session: AsyncSession | None = None) -> Optional[Tenant]:
        db_session = db_session or super().get_db_session()
        root_t = await db_session.execute(select(Tenant).where(Tenant.is_root))
        return root_t.scalar_one_or_none()

    async def get_tenant_by_customer_id(
        self, *, customer_id: str, db_session: AsyncSession | None = None
    ) -> Optional[Tenant]:
        db_session = db_session or super().get_db_session()
        role = await db_session.execute(select(Tenant).where(Tenant.customer_id == customer_id))
        return role.scalar_one_or_none()

tenant = CRUDTenant(Tenant)
