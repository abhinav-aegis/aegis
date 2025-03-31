from uuid import UUID
from sqlmodel import (
    SQLModel, Field, Column, Float,
    String, Boolean
)
from typing import Optional
from backend.common.models.base_uuid_model import BaseUUIDModel


class LLMAPIKeyBase(SQLModel):
    """
    Stores API keys issued for authentication, linked to a tenant and optionally a user or group.
    """
    tenant_id: UUID = Field(nullable=False)  # Required for multi-tenancy
    user_id: Optional[UUID] = Field(default=None, nullable=True)  # Optional, per user
    group_id: Optional[UUID] = Field(default=None, nullable=True)  # Optional, per group
    provider: str = Field(nullable=False)  # Provider (e.g., "openai", "anthropic")
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))

    # Aggregated usage tracking
    total_input_tokens: int = Field(default=0, nullable=False)
    total_output_tokens: int = Field(default=0, nullable=False)
    total_cost: float = Field(default=0.0, sa_column=Column(Float, nullable=False))

class LLMAPIKey(BaseUUIDModel, LLMAPIKeyBase, table=True):
    api_key: str = Field(
        sa_column=Column(String, unique=True, nullable=False, index=True)
    )
