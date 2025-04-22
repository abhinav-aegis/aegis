import inspect
from typing import Optional
from httpx import Request
from litellm import LITELLM_EXCEPTION_TYPES
from pydantic import BaseModel, field_validator
from openai import APIError

# Map class name to class
EXCEPTION_CLASS_MAP = {v.__name__: v for v in LITELLM_EXCEPTION_TYPES}

class SerializedException(BaseModel):
    message: str
    body: object | None
    code: Optional[str] = None
    param: Optional[str] = None
    type: Optional[str] = None
    model: Optional[str] = None
    llm_provider: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in EXCEPTION_CLASS_MAP:
            raise ValueError(f"Invalid exception type: '{v}'. Must be one of: {list(EXCEPTION_CLASS_MAP.keys())}")
        return v

def serialize_exception(exc: APIError) -> SerializedException:
    return SerializedException(
        type=type(exc).__name__,
        message=getattr(exc, "message", str(exc)),
        body=getattr(exc, "body", None),
        param=getattr(exc, "param", None),
        code=getattr(exc, "code", None),
        model=getattr(exc, "model", None),
        llm_provider=getattr(exc, "llm_provider", None),
    )

def raise_from_serialized_exception(data: SerializedException, request: Optional[Request] = None) -> None:
    exc_class = EXCEPTION_CLASS_MAP.get(data.type)
    if not exc_class:
        raise APIError(message=f"Unknown mock exception type: {data.type}")

    # Build a mock request if needed
    request = request or Request("POST", "https://api.mocked-llm.com/v1/completions")

    # Use introspection to get accepted args for the constructor
    sig = inspect.signature(exc_class.__init__)
    accepted_args = sig.parameters.keys()

    # Filter known fields from SerializedException to match constructor
    all_data = {
        "message": data.message,
        "model": data.model or "stub-model",
        "llm_provider": data.llm_provider or "stub-provider",
        "response": None,
        "request": request,
        "body": data.body,
        "code": data.code,
        "param": data.param,
        "litellm_debug_info": None,
        "max_retries": None,
        "num_retries": None,
    }

    kwargs = {k: v for k, v in all_data.items() if k in accepted_args and v is not None}

    # Attempt to raise the exception
    try:
        raise exc_class(**kwargs)
    except TypeError as e:
        raise RuntimeError(f"Error instantiating {exc_class.__name__}: {e}") from e
