from uuid import UUID
from backend.common.utils.partial import optional
from backend.evals.models import LLMAPIKeyBase


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
