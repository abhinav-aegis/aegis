from uuid import UUID
from backend.common.utils.uuid6 import uuid7
from sqlmodel import SQLModel as _SQLModel, Field, DateTime
from sqlalchemy.types import TypeDecorator, String
from sqlalchemy.orm import declared_attr
from datetime import datetime, timezone
from pydantic import types as pydantic_types
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from backend.common.core.config import ModeEnum, settings


class SQLiteUUID(TypeDecorator):
    """
    Custom TypeDecorator to convert UUIDs to TEXT for SQLite.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """
        Convert UUID to string before storing in SQLite.
        """
        if value is not None:
            return str(value)  # ✅ Convert UUID → string
        return None

    def process_result_value(self, value, dialect):
        """
        Convert string back to UUID when retrieving from SQLite.
        """
        if value is not None:
            return UUID(value)  # ✅ Convert string → UUID
        return None

def UUIDType():
    """
    Returns the correct UUID storage type:
    - PostgreSQL: `UUID`
    - SQLite: `TEXT` (converted automatically)
    """
    return PG_UUID(as_uuid=True) if settings.MODE != ModeEnum.testing else SQLiteUUID  # ✅ SQLite stores as TEXT

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
        sa_type=UUIDType(),
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
