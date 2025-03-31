from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.common.crud.base_crud import CRUDBase
from backend.storage.models import LLMAPIKey
from backend.storage.schema import (
    ILLMAPIKeyCreate, ILLMAPIKeyUpdate, ILLMAPIKeyRead,
)

class CRUDAPIKey(CRUDBase[LLMAPIKey, ILLMAPIKeyCreate, ILLMAPIKeyUpdate, ILLMAPIKeyRead]):
    """
    Custom CRUD for APIKey to handle masking.
    """

    async def get(self, *, id: UUID | str, db_session: AsyncSession | None = None):
        raise NotImplementedError("Direct access to full model is disabled. Use `get_read_model()` instead.")


    async def get_read_model(
        self, *, id: UUID | str, db_session: AsyncSession | None = None
    ) -> ILLMAPIKeyRead | None:
        """
        Fetch an API key and return it with a **masked** key.
        """
        db_session = db_session or self.get_db_session()
        db_obj = await db_session.execute(select(LLMAPIKey).where(LLMAPIKey.id == id))
        api_key = db_obj.scalar_one_or_none()

        if api_key:
            return ILLMAPIKeyRead(
                id=api_key.id,
                tenant_id=api_key.tenant_id,
                user_id=api_key.user_id,
                group_id=api_key.group_id,
                provider=api_key.provider,
                is_active=api_key.is_active,
                total_input_tokens=api_key.total_input_tokens,
                total_output_tokens=api_key.total_output_tokens,
                total_cost=api_key.total_cost,
                masked_api_key=self.mask_api_key(api_key.api_key),
            )

        return None

    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """
        Utility function to mask API keys.
        """
        return api_key[:4] + "****" + api_key[-4:]


# ✅ Initialize CRUD classes
api_key = CRUDAPIKey(LLMAPIKey)
