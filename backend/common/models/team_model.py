from backend.common.models.user_model import User
from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID
from backend.common.models.base_uuid_model import BaseUUIDModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.common.models.hero_model import Hero

class TeamBase(SQLModel):
    name: str = Field(index=True)
    headquarters: str


class Team(BaseUUIDModel, TeamBase, table=True):
    heroes: list["Hero"] = Relationship(  # noqa: F821
        back_populates="team", sa_relationship_kwargs={"lazy": "selectin"}
    )
    created_by_id: UUID | None = Field(default=None, foreign_key="User.id")
    created_by: User | None = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Team.created_by_id==User.id",
        }
    )
