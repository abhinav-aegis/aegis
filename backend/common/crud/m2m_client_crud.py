from backend.common.schemas.m2m_client_schema import IM2MClientCreate, IM2MClientUpdate
from backend.common.models.m2m_client_model import M2MClient
from backend.common.core.security import verify_password, get_password_hash
from backend.common.crud.base_crud import CRUDBase
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

class CRUDM2MClient(CRUDBase[M2MClient, IM2MClientCreate, IM2MClientUpdate]):
    async def get_by_client_id(
        self, *, client_id: UUID | str, db_session: AsyncSession | None = None
    ) -> M2MClient | None:
        db_session = db_session or super().get_db_session()
        clients = await db_session.execute(select(M2MClient).where(M2MClient.client_id == client_id))
        return clients.scalar_one_or_none()

    async def create_with_hashed_secret(
        self, *, obj_in: IM2MClientCreate, db_session: AsyncSession | None = None
    ) -> M2MClient:
        db_session = db_session or super().get_db_session()
        db_obj = M2MClient.model_validate(obj_in)
        db_obj.hashed_secret = get_password_hash(obj_in.secret)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def authenticate(self, *, client_id: str, secret: str) -> M2MClient | None:
        client = await self.get_by_client_id(client_id=client_id)
        if not client or not client.hashed_secret:
            return None
        if not verify_password(secret, client.hashed_secret):
            return None
        return client

    async def remove_by_client_id(
        self, *, client_id: UUID | str, db_session: AsyncSession | None = None
    ) -> M2MClient:
        db_session = db_session or super().get_db_session()
        response = await db_session.execute(
            select(M2MClient).where(M2MClient.client_id ==client_id)
        )

        obj = response.scalar_one_or_none()

        if obj:
            await db_session.delete(obj)
            await db_session.commit()

        return obj

m2m_client = CRUDM2MClient(M2MClient)
