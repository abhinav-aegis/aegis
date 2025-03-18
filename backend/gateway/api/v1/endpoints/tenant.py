from backend.common.utils.exceptions import (
    ContentNoChangeException,
    NameExistException,
    IdNotFoundException,
)
from fastapi import APIRouter, Depends, status
from fastapi_pagination import Params
from backend.gateway import crud
from backend.gateway.api import deps
from backend.gateway.deps import tenant_deps
from backend.common.models.tenant_model import Tenant
from backend.common.models.user_model import User
from backend.common.schemas.response_schema import (
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from backend.gateway.schema.tenant_schema import ITenantCreate, ITenantRead, ITenantUpdate
from backend.gateway.schema.role_schema import IRoleEnum
from uuid import UUID

router = APIRouter()

@router.get("")
async def get_tenants(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[ITenantRead]:
    """
    Gets a paginated list of tenants.
    """
    tenants = await crud.tenant.get_multi_paginated(params=params)
    return create_response(data=tenants) # type: ignore


@router.get("/{tenant_id}")
async def get_tenant_by_id(
    tenant: Tenant = Depends(tenant_deps.get_user_tenant_by_id),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[ITenantRead]:
    """
    Gets a tenant by its id.
    """
    return create_response(data=tenant) # type: ignore


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant: ITenantCreate,
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IPostResponseBase[ITenantRead]:
    """
    Create a new Tenant.

    Required roles:
    - admin
    """
    tenant_current = await crud.tenant.get_tenant_by_name(name=tenant.name)
    if tenant_current:
        raise NameExistException(Tenant, name=tenant_current.name)

    new_tenant = await crud.tenant.create(obj_in=tenant)
    return create_response(data=new_tenant) # type: ignore


@router.put("/{tenant_id}")
async def update_tenant(
    tenant: ITenantUpdate,
    current_tenant: Tenant = Depends(tenant_deps.get_user_tenant_by_id),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IPutResponseBase[ITenantRead]:
    """
    Updates a tenant by its id.

    Required roles:
    - admin
    """
    if current_tenant.name == tenant.name and current_tenant.customer_id == tenant.customer_id:
        raise ContentNoChangeException()

    exits_tenant = await crud.tenant.get_tenant_by_name(name=tenant.name)
    if exits_tenant:
        raise NameExistException(Tenant, name=tenant.name)

    updated_tenant = await crud.tenant.update(obj_current=current_tenant, obj_new=tenant)
    return create_response(data=updated_tenant) # type: ignore


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: UUID,
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IGetResponseBase[ITenantRead]:
    """
    Deletes a tenant by its id.

    Required roles:
    - admin
    """
    current_tenant = await crud.tenant.get(id=tenant_id)
    if not current_tenant:
        raise IdNotFoundException(Tenant, id=tenant_id)
    tenant = await crud.tenant.remove(id=tenant_id)
    return create_response(data=tenant) # type: ignore
