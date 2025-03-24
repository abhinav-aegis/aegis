# defines how core data types in autogenstudio are serialized and stored in the database

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID
from pydantic import types as pydantic_types
from autogen_core import ComponentModel
from pydantic import ConfigDict

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlmodel import JSON, Column, Field, SQLModel, Relationship, DateTime, Boolean, ForeignKey
from datetime import timezone
from backend.common.models.base_uuid_model import BaseUUIDModel

from .types import RegistryConfig, MessageConfig, MessageMeta, TeamResult, RegistryMetadata, RegistryComponents

class TaskBase(SQLModel):
    """
    Represents a reusable task template.
    """
    version: Optional[str] = "0.0.1"
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = None
    created_by_user_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(SQLAlchemyUUID, nullable=True),  # Nullable for M2M applications
    )

class Task(TaskBase, BaseUUIDModel, table=True):
    pass

class TeamBase(SQLModel):
    """
    Represents a reusable team of (Autogen) agents.
    """
    version: Optional[str] = "0.0.1"
    component: Union[ComponentModel, dict] = Field(sa_column=Column(JSON))
    created_by_user_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(SQLAlchemyUUID, nullable=True),  # Nullable for M2M applications
    )

class Team(TeamBase, BaseUUIDModel, table=True):
    pass

class MessageBase(SQLModel):
    """
    Represents messages exchanged during a run.
    """
    config: Union[MessageConfig, dict] = Field(
        default_factory=lambda: MessageConfig(source="", content=""), sa_column=Column(JSON)
    )

    session_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("Session.id", ondelete="CASCADE"), index=True)
    )
    run_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("Run.id", ondelete="CASCADE"), index=True)
    )
    message_meta: Optional[Union[MessageMeta, dict]] = Field(default={}, sa_column=Column(JSON))

class Message(MessageBase, BaseUUIDModel, table=True):
    session: Optional["Session"] = Relationship(
        back_populates="messages", sa_relationship_kwargs={"lazy": "joined"}
    )
    run: Optional["Run"] = Relationship(
        back_populates="messages", sa_relationship_kwargs={"lazy": "joined"}
    )

class SessionBase(SQLModel):
    """
    Represents a single session within a task execution for a specific tenant/group/user.
    """
    task_id: UUID = Field(
        sa_column=Column(ForeignKey("Task.id", ondelete="CASCADE"), index=True)
    )
    team_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("Team.id", ondelete="CASCADE"))
    )
    tenant_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(SQLAlchemyUUID, nullable=True)
    )
    group_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(SQLAlchemyUUID, nullable=True)
    )
    created_by_user_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(SQLAlchemyUUID, nullable=True)
    )
    created_at: pydantic_types.AwareDatetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )
    archived: Optional[bool] = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default="false")
    )
    team_metadata: Optional[Union[MessageMeta, dict]] = Field(default=None, sa_column=Column(JSON))

class Session(SessionBase, BaseUUIDModel, table=True):
    runs: List["Run"] = Relationship(
        back_populates="session", sa_relationship_kwargs={"lazy": "selectin"}
    )
    task: Optional["Task"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}  # Joins the task when fetching a session
    )
    messages: List["Message"] = Relationship(
        back_populates="session", sa_relationship_kwargs={"lazy": "selectin"}
    )
    team: Optional["Team"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}  # Joins the team when fetching a session
    )

class RunStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    COMPLETE = "complete"
    ERROR = "error"
    STOPPED = "stopped"

class RunBase(SQLModel):
    """
    Represents a single execution run within a session.
    """

    session_id: UUID = Field(
        sa_column=Column(ForeignKey("Session.id", ondelete="CASCADE"), index=True)
    )
    task_id: UUID = Field(
        sa_column=Column(ForeignKey("Task.id", ondelete="CASCADE"), index=True)
    )


    # Note: This is the specifc task that is being run - this is different from the task_id in the session whcih
    # represents the task template
    run_task: Union[MessageConfig, dict] = Field(
        default_factory=lambda: MessageConfig(source="", content=""), sa_column=Column(JSON)
    )

    batch_mode: Optional[bool] = False

    created_by_user_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(SQLAlchemyUUID, nullable=True)  # Nullable for M2M executions
    )

    archived: Optional[bool] = Field(default=False)

class Run(RunBase, BaseUUIDModel, table=True):
    status: RunStatus = Field(default=RunStatus.CREATED)
    team_result: Optional[Union[TeamResult, dict]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    error_message: Optional[str] = None
    created_at: pydantic_types.AwareDatetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )
    estimated_completion_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    task: Optional["Task"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
    session: Optional["Session"] = Relationship(
        back_populates="runs", sa_relationship_kwargs={"lazy": "joined"}
    )
    messages: List["Message"] = Relationship(
        back_populates="run", sa_relationship_kwargs={"lazy": "selectin"}
    )

class RegistryBase(SQLModel):
    """
    Represents a registry of agents, models, tools, terminations, and teams.
    """
    version: Optional[str] = "0.0.1"
    config: Union[RegistryConfig, dict] = Field(
        default_factory=lambda: RegistryConfig(
            id="",
            name="",
            metadata=RegistryMetadata(author="", version=""),
            components=RegistryComponents(agents=[], models=[], tools=[], terminations=[], teams=[]),
        ),
        sa_column=Column(JSON),
    )

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})  # type: ignore

class Registry(RegistryBase, BaseUUIDModel, table=True):
    pass
