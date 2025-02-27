from backend.common.models.tenant_model import TenantBase
from backend.common.utils.partial import optional
from uuid import UUID


class ITenantCreate(TenantBase):
    pass


# All these fields are optional
@optional()
class ITenantUpdate(TenantBase):
    pass


class ITenantRead(TenantBase):
    id: UUID
