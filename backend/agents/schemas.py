from typing import Optional, List, Dict
from uuid import UUID
from backend.common.utils.partial import optional
from backend.agents.models import (
    TeamBase,
    MessageBase,
    TaskBase,
    SessionBase,
    RunBase,
    RegistryBase,
    RunStatus
)
from pydantic import types as pydantic_types
from datetime import datetime
from .types import TeamResult
from typing import Union

# --- Team Schemas ---
class ITeamCreate(TeamBase):
    pass

@optional()
class ITeamUpdate(TeamBase):
    pass

class ITeamRead(TeamBase):
    id: UUID

# --- Task Schemas ---
class ITaskCreate(TaskBase):
    pass

@optional()
class ITaskUpdate(TaskBase):
    pass

class ITaskRead(TaskBase):
    id: UUID

# --- Message Schemas ---
class IMessageCreate(MessageBase):
    pass

class IMessageRead(MessageBase):
    id: UUID
    status: RunStatus
    team_result: Union[TeamResult, dict]
    error_message: Optional[str]
    created_at: pydantic_types.AwareDatetime | None
    estimated_completion_time: Optional[datetime]

@optional()
class IMessageUpdate(IMessageRead):
    pass

# --- Session Schemas ---
class ISessionCreate(SessionBase):
    pass

class ISessionRead(SessionBase):
    id: UUID
    messages: Optional[List[IMessageRead]] = []
    runs: Optional[List["IRunRead"]] = []  # Forward reference

class ISessionList(SessionBase):
    id: UUID

@optional()
class ISessionUpdate(SessionBase):  # Internal update schema
    pass

# --- Run Schemas ---
class IRunCreate(RunBase):
    pass

class IRunRead(RunBase):
    id: UUID
    status: RunStatus
    team_result: Optional[Union[TeamResult, dict]]
    error_message: Optional[str]
    error_details: Optional[Dict[str, str | None]]
    created_at: Optional[datetime]
    estimated_completion_time: Optional[datetime]

class IRunList(RunBase):
    id: UUID


@optional()
class IRunUpdate(RunBase):  # Internal update schema
    pass

# --- Registry Schemas ---
class IRegistryCreate(RegistryBase):
    pass

@optional()
class IRegistryUpdate(RegistryBase):
    pass

class IRegistryRead(RegistryBase):
    id: UUID
