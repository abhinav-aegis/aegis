from uuid import UUID
import json
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi_pagination import Params, Page
from backend.common.crud.base_crud import CRUDBase
from backend.proxy.models import LLMAPIKey, LLMUsage, LLMErrorLog, LLMStubReplaySequence, LLMStubRequestResponse
from backend.proxy.schema import (
    ILLMAPIKeyCreate, ILLMAPIKeyUpdate, ILLMAPIKeyRead,
    ILLMUsageCreate, ILLMUsageUpdate, ILLMUsageList,
    ILLMErrorLogCreate, ILLMErrorUpdate, ILLMErrorLogList,
    ILLMStubReplaySequenceCreate, ILLMStubReplaySequenceUpdate, ILLMStubReplaySequenceRead,
    ILLMStubRequestResponseCreate, ILLMStubRequestResponseUpdate, ILLMStubRequestResponseRead
)
from datetime import datetime
from backend.common.schemas.common_schema import IOrderEnum
from litellm.types.utils import ModelResponse
import hashlib
from openai.types.chat import completion_create_params
from typing import Any
from collections.abc import Mapping
from backend.proxy.utils.exceptions import SerializedException, raise_from_serialized_exception
from pydantic import ValidationError


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

class CRUDLLMStubReplaySequence(CRUDBase[LLMStubReplaySequence, ILLMStubReplaySequenceCreate, ILLMStubReplaySequenceUpdate, ILLMStubReplaySequenceRead]):
    async def get_next_response(
        self,
        *,
        id: UUID,
        db_session: AsyncSession | None = None
    ) -> ModelResponse | None:
        db_session = db_session or self.get_db_session()
        result = await db_session.execute(select(LLMStubReplaySequence).where(LLMStubReplaySequence.id == id))
        sequence = result.scalar_one_or_none()

        if sequence and sequence.responses:
            index = getattr(sequence, 'current_index', 0)
            response = sequence.responses[index % len(sequence.responses)]
            sequence.current_index = (index + 1) % len(sequence.responses)
            db_session.add(sequence)
            await db_session.commit()
            return response

        return None

    async def reset_sequence_by_id(
        self,
        *,
        id: UUID,
        db_session: AsyncSession | None = None
    ) -> LLMStubReplaySequence | None:
        db_session = db_session or self.get_db_session()
        result = await db_session.execute(select(LLMStubReplaySequence).where(LLMStubReplaySequence.id == id))
        sequence = result.scalar_one_or_none()

        if sequence:
            sequence.current_index = 0
            db_session.add(sequence)
            await db_session.commit()
            await db_session.refresh(sequence)
            return sequence

        return None

    async def get_next_response_by_model(
        self,
        *,
        model: str,
        tenant_id: UUID | None = None,
        db_session: AsyncSession | None = None
    ) -> ModelResponse | None:
        db_session = db_session or self.get_db_session()

        if tenant_id is None:
            result = await db_session.execute(
                select(LLMStubReplaySequence).where(LLMStubReplaySequence.model == model)
            )
        else:
            result = await db_session.execute(
                select(LLMStubReplaySequence)
                .where(LLMStubReplaySequence.tenant_id == tenant_id)
                .where(LLMStubReplaySequence.model == model)
            )

        sequence = result.scalar_one_or_none()

        if sequence and sequence.responses:
            index = getattr(sequence, 'current_index', 0)
            response = sequence.responses[index % len(sequence.responses)]
            sequence.current_index = (index + 1) % len(sequence.responses)
            db_session.add(sequence)
            await db_session.commit()

            if "type" in response and response.get("message"):
                # Likely a SerializedException, not a ModelResponse
                try:
                    response = SerializedException.model_validate(response)
                    raise_from_serialized_exception(response)
                except ValidationError as e:
                    return ModelResponse.model_validate(e)
            else:
                return ModelResponse.model_validate(response)

        return None


    async def create(
        self,
        *,
        obj_in: ILLMStubReplaySequenceCreate | LLMStubReplaySequence,
        created_by_id: UUID | str | None = None,
        db_session: AsyncSession | None = None,
    ) -> LLMStubReplaySequence:
        db_session = db_session or self.get_db_session()
        db_obj = LLMStubReplaySequence.model_validate(obj_in)

        # Normalize the responses to ensure they are JSON-safe
        db_obj.responses = [response.model_dump() if isinstance(response, ModelResponse) else response for response in db_obj.responses]

        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj


def _normalize(obj: Any) -> Any:
    """
    Recursively convert TypedDicts and other nested objects into JSON-safe primitives.

    Converts:
    - TypedDicts → dict
    - lists/tuples/iterables → list
    - other custom objects → str or primitive
    """
    if isinstance(obj, Mapping):
        return {k: _normalize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)) or hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [_normalize(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        return _normalize(vars(obj))
    return obj  # primitive type

def _compute_request_hash(request: dict) -> str:
    """
    Compute a stable hash for a request by canonicalizing it first.
    """
    canonical_json = json.dumps(request, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


class CRUDLLMStubRequestResponse(CRUDBase[LLMStubRequestResponse, ILLMStubRequestResponseCreate, ILLMStubRequestResponseUpdate, ILLMStubRequestResponseRead]):
    async def get_response_by_request(
        self,
        *,
        model: str,
        request_body: completion_create_params.CompletionCreateParamsNonStreaming,
        tenant_id: UUID | None = None,
        db_session: AsyncSession | None = None
    ) -> ModelResponse | None:
        db_session = db_session or self.get_db_session()
        request_hash = _compute_request_hash(request_body)

        result = await db_session.execute(
            select(LLMStubRequestResponse)
            .where(LLMStubRequestResponse.tenant_id == tenant_id)
            .where(LLMStubRequestResponse.model == model)
            .where(LLMStubRequestResponse.request_hash == request_hash)
        )
        stub = result.scalar_one_or_none()
        return stub.response if stub else None

    async def create(
        self,
        *,
        obj_in: ILLMStubRequestResponseCreate, # type: ignore
        created_by_id: UUID | str | None = None,
        db_session: AsyncSession | None = None,
    ) -> LLMStubRequestResponse:
        db_session = db_session or self.get_db_session()
        db_obj = LLMStubRequestResponse.model_validate(obj_in)

        db_obj.response = db_obj.response.model_dump() if isinstance(db_obj.response, ModelResponse) else db_obj.response
        db_obj.request_params = _normalize(db_obj.request_params)
        db_obj.request_hash = _compute_request_hash(db_obj.request_params)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

# ✅ Initialize CRUD classes
api_key = CRUDAPIKey(LLMAPIKey)
llm_usage = CRUDLLMUsage(LLMUsage)
llm_error_log = CRUDLLMErrorLog(LLMErrorLog)
stub_replay = CRUDLLMStubReplaySequence(LLMStubReplaySequence)
stub_response = CRUDLLMStubRequestResponse(LLMStubRequestResponse)
