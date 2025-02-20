from datetime import datetime, timezone
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from .utils.uuid6 import uuid7

# -------------------------------------
# Base Models
# -------------------------------------

# class SQLModel(_SQLModel):
#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()


class BaseUUIDModel(SQLModel):
    """
    Common Base Model for all tables with a UUID primary key.
    """

    id: UUID = Field(default_factory=uuid7, primary_key=True, index=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )

class BaseTenantModel(BaseUUIDModel):
    """
    Base Model for multi-tenant scoped data.
    """

    tenant_id: UUID = Field(index=True, nullable=False, foreign_key="tenant.id")


# -------------------------------------
# Enums for Roles & Audit Actions
# -------------------------------------

class Role(str, Enum):
    """
    Roles in the system.
    """
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    DATA_ENGINEER = "data_engineer"


class AuditAction(str, Enum):
    """
    Actions that trigger audit logs.
    """
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ACCESS = "access"
    EXECUTE = "execute"


# -------------------------------------
# Tenant Management
# -------------------------------------

class Tenant(BaseUUIDModel, table=True):
    """
    Represents a customer or organization using the platform.
    """

    name: str = Field(index=True, unique=True)
    customer_id: str | None = Field(index=True, unique=True, nullable=True)  # External customer reference

    users: list["User"] = Relationship(back_populates="tenant")


# -------------------------------------
# User Management (Now Supports Multiple Roles)
# -------------------------------------

class User(BaseUUIDModel, table=True):
    """
    User Model with role-based multi-tenant access control.
    """

    email: str = Field(index=True, unique=True)
    tenant_id: UUID | None = Field(index=True, nullable=True, foreign_key="tenant.id")
    multi_tenant_access: bool = Field(default=False)  # Vendor users have this set to True
    is_active: bool = Field(default=True)

    # Relationships
    tenant: "Tenant" = Relationship(back_populates="users")
    roles: list["UserRole"] = Relationship(back_populates="user")


class UserRole(BaseUUIDModel, table=True):
    """
    Association table for many-to-many User <-> Role mapping.
    """

    user_id: UUID = Field(index=True, nullable=False, foreign_key="user.id")
    role: Role = Field(sa_column_kwargs={"nullable": False})

    # Relationships
    user: "User" = Relationship(back_populates="roles")


# -------------------------------------
# Teams & Membership
# -------------------------------------

class Team(BaseTenantModel, table=True):
    """
    Teams within a tenant.
    """

    name: str = Field(index=True, unique=False)
    description: str | None = None


class TeamMember(BaseUUIDModel, table=True):
    """
    Associates users with teams.
    """

    team_id: UUID = Field(index=True, nullable=False, foreign_key="team.id")
    user_id: UUID = Field(index=True, nullable=False, foreign_key="user.id")


# -------------------------------------
# Audit Logs
# -------------------------------------

class AuditLog(BaseTenantModel, table=True):
    """
    System-wide audit logs to track actions performed.
    """

    user_id: UUID = Field(index=True, nullable=False, foreign_key="user.id")
    action: AuditAction = Field(sa_column_kwargs={"nullable": False})
    resource: str = Field(index=True)  # API endpoint, object name, etc.
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: str | None = None
