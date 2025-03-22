from uuid import UUID
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi_pagination import Params, Page
from backend.common.crud.base_crud import CRUDBase
from backend.proxy.models import LLMAPIKey, LLMUsage, LLMErrorLog
from backend.proxy.schema import (
    ILLMAPIKeyCreate, ILLMAPIKeyUpdate, ILLMAPIKeyRead,
    ILLMUsageCreate, ILLMUsageUpdate, ILLMUsageList,
    ILLMErrorLogCreate, ILLMErrorUpdate, ILLMErrorLogList
)
from datetime import datetime
from backend.common.schemas.common_schema import IOrderEnum

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


class CRUDLLMUsage(CRUDBase[LLMUsage, ILLMUsageCreate, ILLMUsageUpdate, ILLMUsageList]):
    """
    Custom CRUD for LLMUsage to add aggregations and flexible filtering.
    """

    async def get_usage_summary(
        self,
        *,
        tenant_id: UUID | None = None,
        api_key_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        db_session: AsyncSession | None = None
    ) -> dict:
        """
        Returns aggregated usage (tokens & cost), optionally filtered by tenant_id, api_key_id, and time range.
        """
        db_session = db_session or self.get_db_session()
        query = select( # type: ignore
            func.sum(LLMUsage.input_tokens).label("total_input_tokens"),
            func.sum(LLMUsage.output_tokens).label("total_output_tokens"),
            func.sum(LLMUsage.cost).label("total_cost"),
        )

        if tenant_id:
            query = query.where(LLMUsage.tenant_id == tenant_id)
        if api_key_id:
            query = query.where(LLMUsage.api_key_id == api_key_id)
        if start_date:
            query = query.where(LLMUsage.timestamp >= start_date)
        if end_date:
            query = query.where(LLMUsage.timestamp <= end_date)

        result = await db_session.execute(query)
        summary = result.fetchone()

        if summary is None:
            return {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0.0,
            }

        return {
            "total_input_tokens": summary.total_input_tokens or 0,
            "total_output_tokens": summary.total_output_tokens or 0,
            "total_cost": summary.total_cost or 0.0,
        }

    async def get_filtered_usage(
        self,
        *,
        tenant_id: UUID | None = None,
        api_key_id: UUID | None = None,
        model: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        order_by: str = "timestamp",
        order: IOrderEnum = IOrderEnum.descendent,
        params: Params | None = Params(),
        db_session: AsyncSession | None = None
    ) -> Page[ILLMUsageList]:
        """
        Returns paginated LLM usage logs filtered by tenant_id, api_key_id, model, time range.

        Allows sorting by timestamp, cost, or total tokens.
        """
        db_session = db_session or self.get_db_session()
        query = select(LLMUsage)

        if tenant_id:
            query = query.where(LLMUsage.tenant_id == tenant_id)
        if api_key_id:
            query = query.where(LLMUsage.api_key_id == api_key_id)
        if model:
            query = query.where(LLMUsage.model == model)
        if start_date:
            query = query.where(LLMUsage.timestamp >= start_date)
        if end_date:
            query = query.where(LLMUsage.timestamp <= end_date)

        # Ensure ordering field is valid
        if order_by not in ["timestamp", "cost", "total_tokens"]:
            order_by = "timestamp"

        # Apply ordering
        if order == IOrderEnum.ascendent:
            query = query.order_by(getattr(LLMUsage, order_by).asc())
        else:
            query = query.order_by(getattr(LLMUsage, order_by).desc())

        return await self.get_multi_paginated_ordered(
            params=params, order_by=order_by, order=order, query=query, db_session=db_session # type: ignore
        )


class CRUDLLMErrorLog(CRUDBase[LLMErrorLog, ILLMErrorLogCreate, ILLMErrorUpdate, ILLMErrorLogList]):
    """
    Custom CRUD for LLMErrorLog with filtering.
    """

    async def get_filtered_errors(
        self,
        *,
        tenant_id: UUID | None = None,
        api_key_id: UUID | None = None,
        provider: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        params: Params | None = Params(),
        db_session: AsyncSession | None = None
    ) -> Page[ILLMErrorLogList]:
        """
        Returns paginated LLM error logs filtered by tenant_id, api_key_id, provider, and date range.
        """
        db_session = db_session or self.get_db_session()
        query = select(LLMErrorLog)

        if tenant_id:
            query = query.where(LLMErrorLog.tenant_id == tenant_id)
        if api_key_id:
            query = query.where(LLMErrorLog.api_key_id == api_key_id)
        if provider:
            query = query.where(LLMErrorLog.provider == provider)
        if start_date:
            query = query.where(LLMErrorLog.timestamp >= start_date)
        if end_date:
            query = query.where(LLMErrorLog.timestamp <= end_date)

        return await self.get_multi_paginated_ordered(
            params=params, order_by="timestamp", order=IOrderEnum.descendent, query=query, db_session=db_session # type: ignore
        )


# ✅ Initialize CRUD classes
api_key = CRUDAPIKey(LLMAPIKey)
llm_usage = CRUDLLMUsage(LLMUsage)
llm_error_log = CRUDLLMErrorLog(LLMErrorLog)
