from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from backend.common.schemas.m2m_client_schema import (
    IM2MClientCreate, IM2MClientUpdate, IAPIKeyCreate, IAPIKeyUpdate, APIKeyPrefix
)
from backend.common.models.m2m_client_model import M2MClient, APIKey
from backend.common.core.security import verify_password, get_password_hash
from backend.common.crud.base_crud import CRUDBase
from backend.common.core.security import hash_secret_sha256, validate_api_key_format, get_key_preview

class CRUDM2MClient(CRUDBase[M2MClient, IM2MClientCreate, IM2MClientUpdate, M2MClient]):
    async def get_by_client_id(
        self, *, client_id: UUID, db_session: AsyncSession | None = None
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

    async def authenticate(self, *, client_id: UUID, client_secret: str) -> M2MClient | None:
        client = await self.get_by_client_id(client_id=client_id)
        if not client or not client.hashed_secret:
            return None
        if not verify_password(client_secret, client.hashed_secret):
            return None
        return client

    async def remove_by_client_id(
        self, *, client_id: UUID , db_session: AsyncSession | None = None
    ) -> M2MClient:
        db_session = db_session or super().get_db_session()
        response = await db_session.execute(
            select(M2MClient).where(M2MClient.client_id == client_id)
        )

        obj = response.scalar_one_or_none()

        if obj:
            await db_session.delete(obj)
            await db_session.commit()

        return obj




class CRUDAPIKey(CRUDBase[APIKey, IAPIKeyCreate, IAPIKeyUpdate, APIKey]):
    def validate_key_format(self, raw_key: str) -> None:
        valid_prefixes = [p.value for p in APIKeyPrefix]
        validate_api_key_format(raw_key, valid_prefixes)

    async def get_by_raw_key(
        self, *, raw_key: str, db_session: AsyncSession | None = None
    ) -> APIKey | None:
        hashed_key = hash_secret_sha256(raw_key)
        db_session = db_session or super().get_db_session()
        result = await db_session.execute(
            select(APIKey).where(APIKey.hashed_key == hashed_key, APIKey.is_active)
        )
        return result.scalar_one_or_none()

    async def create_with_hashed_key(
        self, *, obj_in: IAPIKeyCreate, db_session: AsyncSession | None = None
    ) -> APIKey:
        db_session = db_session or super().get_db_session()
        self.validate_key_format(obj_in.raw_key)
        hashed_key = hash_secret_sha256(obj_in.raw_key)
        preview = get_key_preview(obj_in.raw_key)
        db_obj = APIKey.model_validate(obj_in, update={"hashed_key": hashed_key, "preview": preview})

        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def revoke(
        self, *, key_id: UUID, db_session: AsyncSession | None = None
    ) -> APIKey | None:
        db_session = db_session or super().get_db_session()
        result = await db_session.execute(
            select(APIKey).where(APIKey.key_id == key_id)
        )
        obj = result.scalar_one_or_none()
        if obj:
            obj.is_active = False
            await db_session.commit()
            await db_session.refresh(obj)
        return obj

m2m_client = CRUDM2MClient(M2MClient)
api_key = CRUDAPIKey(APIKey)
