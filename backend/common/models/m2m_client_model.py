from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from backend.common.models.base_uuid_model import BaseUUIDModel
from typing import Optional
from datetime import datetime

class M2MClientBase(SQLModel):
    client_id: UUID = Field(default_factory=uuid4, index=True, unique=True)
    client_name: str | None = Field(default=None)
    service_description: str | None = Field(default=None)
    is_active: bool = Field(default=True)

class M2MClient(BaseUUIDModel, M2MClientBase, table=True):
    hashed_secret: str | None = Field(default=None, nullable=False, index=True)

class APIKeyBase(SQLModel):
    key_id: UUID = Field(default_factory=uuid4, index=True, unique=True)
    name: str = Field(index=True)  # e.g. "pipeline-service"
    preview: Optional[str] = Field(default=None, index=True)  # e.g. "svc_xxx...zzz"
    service_description: Optional[str] = Field(default=None)
    created_by: Optional[str] = Field(default=None)  # email/username of issuer
    is_active: bool = Field(default=True, index=True)
    last_used_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)


class APIKey(BaseUUIDModel, APIKeyBase, table=True):
    hashed_key: str | None = Field(default=None, nullable=False, index=True)
