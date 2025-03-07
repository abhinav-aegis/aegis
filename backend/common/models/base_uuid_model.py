from uuid import UUID
from backend.common.utils.uuid6 import uuid7
from sqlmodel import SQLModel as _SQLModel, Field, DateTime
from sqlalchemy.orm import declared_attr
from datetime import datetime, timezone
from pydantic import types as pydantic_types

# id: implements proposal uuid7 draft4
class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__

class BaseUUIDModel(SQLModel):
    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: pydantic_types.AwareDatetime | None = Field( # type: ignore
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=DateTime(timezone=True),
    )
    created_at: pydantic_types.AwareDatetime | None = Field( # type: ignore
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
