from backend.gateway import crud
from backend.common.models.role_model import Role
from backend.common.models.user_model import User
from backend.gateway.schema.user_schema import IUserCreate
from backend.common.utils.exceptions.common_exception import IdNotFoundException
from uuid import UUID
from fastapi import HTTPException, Path, status
from typing_extensions import Annotated


async def user_exists(new_user: IUserCreate) -> IUserCreate:
    user = await crud.user.get_by_email(email=new_user.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same email",
        )

    if not new_user.role_id:
        raise IdNotFoundException(Role, id=new_user.role_id)

    role = await crud.role.get(id=new_user.role_id)
    if not role:
        raise IdNotFoundException(Role, id=new_user.role_id)

    return new_user

async def is_valid_user(
    user_id: Annotated[UUID, Path(title="The UUID id of the user")]
) -> User:
    user = await crud.user.get(id=user_id)
    if not user:
        raise IdNotFoundException(User, id=user_id)

    return user

async def is_valid_user_id(
    user_id: Annotated[UUID, Path(title="The UUID id of the user")]
) -> UUID:
    user = await crud.user.get(id=user_id)
    if not user:
        raise IdNotFoundException(User, id=user_id)

    return user_id
