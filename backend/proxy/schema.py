from uuid import UUID
from backend.common.utils.partial import optional
from backend.proxy.models import LLMAPIKeyBase, LLMUsageBase, LLMErrorLogBase


# --- 🔹 API Key Schemas ---
class ILLMAPIKeyCreate(LLMAPIKeyBase):
    """
    Request schema for creating an API key.
    """
    api_key: str  # Required for creation

@optional()
class ILLMAPIKeyUpdate(ILLMAPIKeyCreate):
    """
    Schema for updating an API key (only allow modifying `is_active`).
    """
    pass

class ILLMAPIKeyRead(LLMAPIKeyBase):
    """
    Response schema for reading an API key (does not expose `api_key`).
    """
    id: UUID
    masked_api_key: str  # Shows a masked version (e.g., sk-****abcd)

class ILLMAPIKeyList(LLMAPIKeyBase):
    """
    Lightweight response schema for listing API keys.
    """
    id: UUID
    masked_api_key: str

# --- 🔹 LLM Usage Schemas ---
class ILLMUsageCreate(LLMUsageBase):
    """
    Request schema for logging LLM usage.
    """
    pass  # All fields from `LLMUsageBase` are required

@optional()
class ILLMUsageUpdate(LLMUsageBase):
    """
    Request schema for logging LLM usage.
    """
    pass  # All fields from `LLMUsageBase` are required

class ILLMUsageRead(LLMUsageBase):
    """
    Response schema for retrieving LLM usage.
    """
    id: UUID

class ILLMUsageList(LLMUsageBase):
    """
    Paginated response schema for listing LLM usage logs.
    """
    id: UUID


# --- 🔹 LLM Error Log Schemas ---
class ILLMErrorLogCreate(LLMErrorLogBase):
    """
    Request schema for logging LLM API errors.
    """
    pass  # All fields from `LLMErrorLogBase` are required

@optional()
class ILLMErrorUpdate(LLMUsageBase):
    """
    Request schema for logging LLM usage.
    """
    pass  # All fields from `LLMUsageBase` are required

class ILLMErrorLogRead(LLMErrorLogBase):
    """
    Response schema for retrieving LLM error logs.
    """
    id: UUID

class ILLMErrorLogList(LLMErrorLogBase):
    """
    Paginated response schema for listing LLM error logs.
    """
    id: UUID
