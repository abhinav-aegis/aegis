from backend.common import crud
from backend.common.models.tenant_model import Tenant
from backend.common.utils.exceptions.common_exception import (
    NameNotFoundException,
    IdNotFoundException,
)
from uuid import UUID
from fastapi import Query, Path
from typing_extensions import Annotated


async def get_user_tenant_by_name(
    tenant_name: Annotated[str, Query(title="String compare with name or last name")] = ""
) -> str:
    tenant = await crud.tenant.get_tenant_by_name(name=tenant_name)
    if not tenant:
        raise NameNotFoundException(Tenant, name=tenant_name)
    return tenant_name


async def get_user_tenant_by_id(
    tenant_id: Annotated[UUID, Path(title="The UUID id of the role")]
) -> Tenant:
    tenant = await crud.tenant.get(id=tenant_id)
    if not tenant:
        raise IdNotFoundException(Tenant, id=tenant_id)
    return tenant
