from sqlmodel import Field, Relationship, SQLModel
from backend.common.models.base_uuid_model import BaseUUIDModel
from uuid import UUID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.common.models.user_model import User
    from backend.common.models.team_model import Team

class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    team_id: UUID | None = Field(default=None, foreign_key="Team.id")


class Hero(BaseUUIDModel, HeroBase, table=True):
    team: "Team" = Relationship(  # noqa: F821
        back_populates="heroes", sa_relationship_kwargs={"lazy": "joined"}
    )
    created_by_id: UUID | None = Field(default=None, foreign_key="User.id")
    created_by: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Hero.created_by_id==User.id",
        }
    )
