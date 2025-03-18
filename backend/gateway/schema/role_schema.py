from enum import Enum
from backend.common.models.role_model import RoleBase
from backend.common.utils.partial import optional
from uuid import UUID


class IRoleCreate(RoleBase):
    pass


# All these fields are optional
@optional()
class IRoleUpdate(RoleBase):
    pass


class IRoleRead(RoleBase):
    id: UUID


class IRoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    data = "data"
    agent = "agent"
    user = "user"
