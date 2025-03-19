from backend.common.utils.exceptions import (
    IdNotFoundException,
)
from fastapi import APIRouter, Depends, status
from fastapi_pagination import Params
from backend.common import crud
from backend.gateway.api import deps
from backend.common.models.m2m_client_model import M2MClient
from backend.gateway.models.user_model import User
from backend.common.schemas.response_schema import (
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    create_response,
)
from backend.common.schemas.m2m_client_schema import IM2MClientCreate, IM2MClientRead
from uuid import UUID
from backend.gateway.schema.role_schema import IRoleEnum

router = APIRouter()

@router.get("/list")
async def get_m2m_clients(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])),
) -> IGetResponsePaginated[IM2MClientRead]:
    """
    Gets a paginated list of m2m_clients.
    """
    m2m_clients = await crud.m2m_client.get_multi_paginated(params=params)
    return create_response(data=m2m_clients) # type: ignore

@router.get("/{client_id}")
async def get_m2m_client_by_id(
    client_id: UUID,
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])),
) -> IGetResponseBase[IM2MClientRead]:
    """
    Gets a m2m_client by its id.
    """
    m2m_client = await crud.m2m_client.get_by_client_id(client_id=client_id)
    if not m2m_client:
        raise IdNotFoundException(M2MClient, id=client_id)
    return create_response(data=m2m_client) # type: ignore

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_m2m_client(
    m2m_client: IM2MClientCreate,
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IPostResponseBase[IM2MClientRead]:
    """
    Create a new M2MClient.

    Required roles:
    - admin
    """
    new_m2m_client = await crud.m2m_client.create_with_hashed_secret(obj_in=m2m_client)
    return create_response(data=new_m2m_client) # type: ignore

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_m2m_client(
    client_id: UUID,
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> None:
    """
    Remove a M2MClient by its id.

    Required roles:
    - admin
    """
    m2m_client = await crud.m2m_client.remove_by_client_id(client_id=client_id)
    if not m2m_client:
        raise IdNotFoundException(M2MClient, id=client_id)
    return create_response(data=m2m_client) # type: ignore
