from backend.common.models.group_model import Group
from backend.common.models.user_model import User
from backend.gateway.schema.group_schema import IGroupCreate, IGroupUpdate
from backend.common.crud.base_crud import CRUDBase
from sqlmodel import select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

class CRUDGroup(CRUDBase[Group, IGroupCreate, IGroupUpdate, Group]):
    async def get_group_by_name(
        self, *, name: str, db_session: AsyncSession | None = None
    ) -> Optional[Group]:
        db_session = db_session or super().get_db_session()
        group = await db_session.execute(select(Group).where(Group.name == name))
        return group.scalar_one_or_none()

    async def add_user_to_group(self, *, user: User, group_id: UUID) -> Group:
        db_session = super().get_db_session()
        group = await super().get(id=group_id)
        if not group:
            raise ValueError(f"Group with id {group_id} not found")

        group.users.append(user)
        db_session.add(group)
        await db_session.commit()
        await db_session.refresh(group)
        return group

    async def add_users_to_group(
        self,
        *,
        users: list[User],
        group_id: UUID,
        db_session: AsyncSession | None = None,
    ) -> Group:
        db_session = db_session or super().get_db_session()
        group = await super().get(id=group_id, db_session=db_session)
        if not group:
            raise ValueError(f"Group with id {group_id} not found")

        group.users.extend(users)
        db_session.add(group)
        await db_session.commit()
        await db_session.refresh(group)
        return group


group = CRUDGroup(Group)
