from backend.common.utils.partial import optional
from uuid import UUID
from backend.common.models.m2m_client_model import M2MClientBase, APIKeyBase
from enum import Enum

class IM2MClientCreate(M2MClientBase):
    secret: str
    class Config:
        hashed_secret = None

@optional()
class IM2MClientUpdate(M2MClientBase):
    pass

class IM2MClientRead(M2MClientBase):
    id: UUID
    client_id: UUID
    client_name: str | None = None
    service_description: str | None = None

class APIKeyPrefix(str, Enum):
    SERVICE = "svc_"
    INTERNAL = "int_"
    USER = "usr_"
    TEST = "test_"


class IAPIKeyCreate(APIKeyBase):
    raw_key: str

    class Config:
        hashed_key = None


@optional()
class IAPIKeyUpdate(APIKeyBase):
    pass

class IAPIKeyRead(APIKeyBase):
    id: UUID
    preview: str
