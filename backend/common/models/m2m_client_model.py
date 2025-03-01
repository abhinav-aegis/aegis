from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from backend.common.models.base_uuid_model import BaseUUIDModel

class M2MClientBase(SQLModel):
    client_id: UUID = Field(default_factory=uuid4, index=True, unique=True)
    client_name: str | None = Field(default=None)
    service_description: str | None = Field(default=None)
    is_active: bool = Field(default=True)

class M2MClient(BaseUUIDModel, M2MClientBase, table=True):
    hashed_secret: str | None = Field(default=None, nullable=False, index=True)
