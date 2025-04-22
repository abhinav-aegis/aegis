from datetime import datetime, timezone
from uuid import UUID
from sqlmodel import (
    SQLModel, Field, Column, DateTime, Float,
    String, Boolean, ForeignKey, Relationship, JSON
)

from typing import Optional, List, Union, Dict, Any
from backend.common.models.base_uuid_model import BaseUUIDModel
from litellm.types.utils import ModelResponse
from openai.types.chat import completion_create_params
from enum import Enum

from backend.proxy.utils.exceptions import SerializedException

class LLMAPIKeyBase(SQLModel):
    """
    Stores API keys issued for authentication, linked to a tenant and optionally a user or group.
    """
    tenant_id: UUID = Field(nullable=False)  # Required for multi-tenancy
    user_id: Optional[UUID] = Field(default=None, nullable=True)  # Optional, per user
    group_id: Optional[UUID] = Field(default=None, nullable=True)  # Optional, per group
    provider: str = Field(nullable=False)  # Provider (e.g., "openai", "anthropic")
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))

    # Aggregated usage trackingd
    total_input_tokens: int = Field(default=0, nullable=False)
    total_output_tokens: int = Field(default=0, nullable=False)
    total_cost: float = Field(default=0.0, sa_column=Column(Float, nullable=False))

class LLMAPIKey(BaseUUIDModel, LLMAPIKeyBase, table=True):
    api_key: str = Field(
        sa_column=Column(String, unique=True, nullable=False, index=True)
    )
    llm_usage: List["LLMUsage"] = Relationship(
        back_populates="api_key",
        sa_relationship_kwargs={"lazy": "selectin"}  # Batch loads only if accessed
    )
    llm_error_log: List["LLMErrorLog"] = Relationship(
        back_populates="api_key",
        sa_relationship_kwargs={"lazy": "selectin"}  # Batch loads only if accessed
    )

class LLMUsageBase(SQLModel):
    """
    Tracks LLM API usage per request.
    """
    tenant_id: UUID = Field(nullable=False, index=True)  # Required for multi-tenancy
    user_id: Optional[UUID] = Field(default=None, nullable=True, index=True)  # Optional, per user
    group_id: Optional[UUID] = Field(default=None, nullable=True, index=True)  # Optional, per group
    api_key_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("APIKey.id", ondelete="CASCADE"), index=True)
    )

    # API Call Metadata
    provider: str = Field(nullable=False)  # Which LLM provider (e.g., OpenAI, Anthropic)
    model: str = Field(nullable=False)  # Which model was used (e.g., GPT-4, Claude-2)
    vendor_request_id: str = Field(sa_column=Column(String, index=True, nullable=True))  # LLM API request ID
    batch_job_id: str = Field(sa_column=Column(String, index=True, nullable=True))  # If part of batch processing

    # Token & Cost Tracking
    input_tokens: int = Field(default=0, nullable=False)
    output_tokens: int = Field(default=0, nullable=False)
    total_tokens: int = Field(default=0, nullable=False)
    cost: float = Field(default=0.0, sa_column=Column(Float, nullable=False))

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )

class LLMUsage(BaseUUIDModel, LLMUsageBase, table=True):
    api_key_id: UUID = Field(
        sa_column=Column(ForeignKey("LLMAPIKey.id", ondelete="CASCADE"), index=True)
    )
    api_key: Optional[LLMAPIKey] = Relationship(back_populates="llm_usage",
                                             sa_relationship_kwargs={"lazy": "selectin"})

class LLMErrorLogBase(SQLModel):
    """
    Logs errors that occur when calling the LLM API.
    """
    tenant_id: UUID = Field(nullable=False)  # Required for multi-tenancy
    user_id: UUID = Field(default=None, nullable=True)  # Optional, per user
    group_id: UUID = Field(default=None, nullable=True)  # Optional, per group
    api_key_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("LLMAPIKey.id", ondelete="CASCADE"), index=True)
    )

    # API Call Metadata
    provider: str = Field(nullable=False)  # Which LLM provider (e.g., OpenAI, Anthropic)
    model: str = Field(nullable=False)  # Which model was used (e.g., GPT-4, Claude-2)
    request_id: UUID = Field(nullable=False, index=True)  # Unique request identifier
    vendor_request_id: str = Field(sa_column=Column(String, index=True, nullable=True))  # LLM API request ID
    batch_job_id: str = Field(sa_column=Column(String, index=True, nullable=True))  # If part of batch processing

    # Error Details
    error_type: str = Field(nullable=False)  # Type of error (e.g., Timeout, InvalidResponse)
    error_message: str = Field(nullable=False)  # Detailed error message
    status_code: int = Field(default=None, nullable=True)  # HTTP status code (if applicable)
    response_data: str = Field(default=None, sa_column=Column(String, nullable=True))  # Raw response (if relevant)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )

class LLMErrorLog(BaseUUIDModel, LLMErrorLogBase, table=True):
    api_key_id: UUID = Field(
        sa_column=Column(ForeignKey("LLMAPIKey.id", ondelete="CASCADE"), index=True)
    )
    api_key: Optional[LLMAPIKey] = Relationship(
        back_populates="llm_error_log",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class LLMStubReplaySequenceBase(SQLModel):
    """
    Sequence of fake LLM responses for replay testing or mocking.
    """
    tenant_id: Optional[UUID] = Field(nullable=True)
    provider: Optional[str] = Field(nullable=True)
    model: Optional[str] = Field(nullable=True, index=True)
    responses: Union[List[ModelResponse|SerializedException], List[Dict[str, Any]]] = Field(sa_column=Column(JSON, nullable=False))
    is_active: bool = Field(default=True, nullable=False)
    current_index: int = Field(default=0, nullable=False)

class LLMStubReplaySequence(LLMStubReplaySequenceBase, BaseUUIDModel, table=True):
    pass

class MatchStrategy(str, Enum):
    exact = "exact"
    canonical_hash = "canonical_hash"

class LLMStubRequestResponseBase(SQLModel):
    """
    Caches a specific request and its corresponding LLM response for reuse.
    """
    tenant_id: Optional[UUID] = Field(nullable=True)
    provider: Optional[str] = Field(nullable=True)
    model: Optional[str] = Field(nullable=True, index=True)
    request_params: Union[completion_create_params.CompletionCreateParamsNonStreaming, Dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=False)
    )
    response: Union[ModelResponse, Dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=False)
    )
    notes: Optional[str] = Field(default=None)
    request_hash: Optional[str] = Field(default=None, index=True, nullable=True)

class LLMStubRequestResponse(LLMStubRequestResponseBase, BaseUUIDModel, table=True):
    pass
