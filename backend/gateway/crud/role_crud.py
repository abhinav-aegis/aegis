from backend.gateway.schema.role_schema import IRoleCreate, IRoleUpdate
from backend.gateway.models.role_model import Role
from backend.gateway.models.user_model import User
from backend.common.crud.base_crud import CRUDBase
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import UUID
from typing import Optional


class CRUDRole(CRUDBase[Role, IRoleCreate, IRoleUpdate, Role]):
    async def get_role_by_name(
        self, *, name: str, db_session: AsyncSession | None = None
    ) -> Optional[Role]:
        db_session = db_session or super().get_db_session()
        role = await db_session.execute(select(Role).where(Role.name == name))
        return role.scalar_one_or_none()

    async def add_role_to_user(self, *, user: User, role_id: UUID) -> Optional[Role]:
        db_session = super().get_db_session()
        role = await super().get(id=role_id)
        role.users.append(user) # type: ignore[union-attr]
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)
        return role

role = CRUDRole(Role)
