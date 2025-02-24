from sqlmodel import SQLModel, Relationship
from backend.common.models.base_uuid_model import BaseUUIDModel
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.common.models.user_model import User

class RoleBase(SQLModel):
    name: str
    description: str


class Role(BaseUUIDModel, RoleBase, table=True):
    users: list["User"] = Relationship(  # noqa: F821
        back_populates="role", sa_relationship_kwargs={"lazy": "selectin"}
    )
