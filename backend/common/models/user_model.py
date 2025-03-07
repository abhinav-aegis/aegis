from backend.common.models.base_uuid_model import BaseUUIDModel
from backend.common.models.links_model import LinkGroupUser
from backend.common.schemas.common_schema import IGenderEnum
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, Column, DateTime, String, ForeignKey
from typing import Optional
from sqlalchemy_utils import ChoiceType # type: ignore
from pydantic import EmailStr
from uuid import UUID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.common.models.group_model import Group
    from backend.common.models.role_model import Role
    from backend.common.models.tenant_model import Tenant

class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr = Field(sa_column=Column(String, index=True, unique=True))
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    birthdate: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )  # birthday with timezone
    role_id: UUID | None = Field(default=None, foreign_key="Role.id")
    tenant_id: UUID = Field(
        sa_column=Column(ForeignKey("Tenant.id"), nullable=False, index=True)
    )
    phone: str | None = None
    gender: IGenderEnum | None = Field(
        default=IGenderEnum.other,
        sa_column=Column(ChoiceType(IGenderEnum, impl=String())),
    )
    state: str | None = None
    country: str | None = None
    address: str | None = None


class User(BaseUUIDModel, UserBase, table=True):
    hashed_password: str | None = Field(default=None, nullable=False, index=True)
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"lazy": "joined"}
    )
    tenant: Optional["Tenant"] = Relationship(
        back_populates="users", sa_relationship_kwargs={"lazy": "joined"}
    )
    groups: list["Group"] = Relationship(  # noqa: F821
        back_populates="users",
        link_model=LinkGroupUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
