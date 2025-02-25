from backend.common.models.user_model import User
from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID
from backend.common.models.base_uuid_model import BaseUUIDModel

class TeamBase(SQLModel):
    name: str = Field(index=True)
    headquarters: str


class Team(BaseUUIDModel, TeamBase, table=True):
    created_by_id: UUID | None = Field(default=None, foreign_key="User.id")
    created_by: User | None = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Team.created_by_id==User.id",
        }
    )
