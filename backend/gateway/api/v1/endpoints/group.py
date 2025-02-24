from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi_pagination import Params
from backend.common import crud
from backend.gateway.api import deps
from backend.common.deps import group_deps, user_deps
from backend.common.models.group_model import Group
from backend.common.models.user_model import User
from backend.common.schemas.group_schema import (
    IGroupCreate,
    IGroupRead,
    IGroupReadWithUsers,
    IGroupUpdate,
)
from backend.common.schemas.response_schema import (
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from backend.common.schemas.role_schema import IRoleEnum
from backend.common.utils.exceptions import (
    IdNotFoundException,
    NameExistException,
)

router = APIRouter()


@router.get("")
async def get_groups(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IGroupRead]:
    """
    Gets a paginated list of groups.
    """
    groups = await crud.group.get_multi_paginated(params=params)
    return create_response(data=groups) # type: ignore


@router.get("/{group_id}")
async def get_group_by_id(
    group_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IGroupReadWithUsers]:
    """
    Gets a group by its id.
    """
    group = await crud.group.get(id=group_id)
    if group:
        return create_response(data=group) # type: ignore
    else:
        raise IdNotFoundException(Group, group_id)


@router.post("")
async def create_group(
    group: IGroupCreate,
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IPostResponseBase[IGroupRead]:
    """
    Creates a new group.

    Required roles:
    - admin
    - manager
    """
    group_current = await crud.group.get_group_by_name(name=group.name)
    if group_current:
        raise NameExistException(Group, name=group.name)
    new_group = await crud.group.create(obj_in=group, created_by_id=current_user.id)
    return create_response(data=new_group)  # type: ignore


@router.put("/{group_id}")
async def update_group(
    group: IGroupUpdate,
    current_group: Group = Depends(group_deps.get_group_by_id),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IPutResponseBase[IGroupRead]:
    """
    Updates a group by its id.

    Required roles:
    - admin
    - manager
    """
    group_updated = await crud.group.update(obj_current=current_group, obj_new=group)
    return create_response(data=group_updated) # type: ignore


@router.post("/add_user/{user_id}/{group_id}")
async def add_user_into_a_group(
    user: User = Depends(user_deps.is_valid_user),
    group: Group = Depends(group_deps.get_group_by_id),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IPostResponseBase[IGroupRead]:
    """
    Adds a user into a group.

    Required roles:
    - admin
    - manager
    """
    group = await crud.group.add_user_to_group(user=user, group_id=group.id)
    return create_response(message="User added to group", data=group) # type: ignore
