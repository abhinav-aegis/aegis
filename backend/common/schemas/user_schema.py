from backend.common.utils.partial import optional
from backend.common.models.user_model import UserBase
from backend.common.models.group_model import GroupBase
from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from .image_media_schema import IImageMediaRead
from .role_schema import IRoleRead
from .tenant_schema import ITenantRead


class IUserCreate(UserBase):
    password: str
    class Config:
        hashed_password = None

# All these fields are optional
@optional()
class IUserUpdate(UserBase):
    pass


# This schema is used to avoid circular import
class IGroupReadBasic(GroupBase):
    id: UUID


class IUserRead(UserBase):
    id: UUID
    tenant: ITenantRead
    role: IRoleRead | None = None
    groups: list[IGroupReadBasic] | None = []
    image: IImageMediaRead | None


class IUserReadWithoutGroups(UserBase):
    id: UUID
    tenant: ITenantRead
    role: IRoleRead | None = None
    image: IImageMediaRead | None


class IUserBasicInfo(BaseModel):
    id: UUID
    tenant: ITenantRead
    first_name: str
    last_name: str

class IUserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
