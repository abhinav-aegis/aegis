from sqlmodel import Field, Relationship, SQLModel
from .links_model import LinkGroupUser
from backend.common.models.base_uuid_model import BaseUUIDModel
from uuid import UUID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.common.models.user_model import User


class GroupBase(SQLModel):
    name: str
    description: str


class Group(BaseUUIDModel, GroupBase, table=True):
    created_by_id: UUID | None = Field(default=None, foreign_key="User.id")
    created_by: "User" = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Group.created_by_id==User.id",
        }
    )
    users: list["User"] = Relationship(
        back_populates="groups",
        link_model=LinkGroupUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
