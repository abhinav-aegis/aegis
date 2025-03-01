from backend.common.utils.partial import optional
from uuid import UUID
from backend.common.models.m2m_client_model import M2MClientBase

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
