from sqlmodel import SQLModel, Field, Relationship
from backend.common.models.base_uuid_model import BaseUUIDModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.gateway.models.user_model import User
    from backend.gateway.models.group_model import Group

class TenantBase(SQLModel):
    """
    Represents a customer or organization using the platform.
    """
    name: str = Field(index=True, unique=True)
    customer_id: str | None = Field(index=True, unique=True, nullable=True)  # External customer reference
    is_root: bool = Field(default=False)  # Is the root tenant

class Tenant(BaseUUIDModel, TenantBase, table=True):
    users: list["User"] = Relationship(
        back_populates="tenant", sa_relationship_kwargs={"lazy": "selectin"}
    )
    groups: list["Group"] = Relationship(
        back_populates="tenant", sa_relationship_kwargs={"lazy": "selectin"}
    )
