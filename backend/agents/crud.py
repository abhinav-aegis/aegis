from typing import Optional, Any
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from autogen_core import ComponentModel
from sqlalchemy import exc
from fastapi import HTTPException
from fastapi_pagination import Params, Page
from datetime import datetime
from backend.common.crud.base_crud import CRUDBase
from backend.agents.models import Team, Message, Task, Session, Run, Registry
from backend.agents.schemas import (
    ITeamCreate, ITeamUpdate, ITaskCreate, ITaskUpdate,
    ISessionCreate, ISessionList, ISessionUpdate,
    IRunCreate, IRunList, IRunUpdate,
    IMessageCreate, IMessageUpdate,
    IRegistryCreate, IRegistryUpdate
)
from backend.agents.types import MessageConfig
from backend.common.schemas.common_schema import IOrderEnum

class CRUDTask(CRUDBase[Task, ITaskCreate, ITaskUpdate, Task]):
    async def get_task_by_name(
        self, *, name: str, db_session: AsyncSession | None = None
    ) -> Optional[Task]:
        db_session = db_session or super().get_db_session()
        task = await db_session.execute(select(Task).where(Task.name == name))
        return task.scalar_one_or_none()


class CRUDTeam(CRUDBase[Team, ITeamCreate, ITeamUpdate, Team]):
    async def create(
        self,
        *,
        obj_in: ITeamCreate | Team,
        created_by_id: UUID | str | None = None,
        db_session: AsyncSession | None = None,
    ) -> Team:
        db_session = db_session or super().get_db_session()
        db_obj = Team.model_validate(obj_in)  # type: ignore

        if isinstance(db_obj.component, ComponentModel):
            db_obj.component = db_obj.component.model_dump()

        try:
            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError:
            await db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Resource already exists",
            )
        await db_session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        *,
        obj_current: Team,
        obj_new: ITeamUpdate | dict[str, Any] | Team,
        db_session: AsyncSession | None = None,
    ) -> Team:
        db_session = db_session or super().get_db_session()

        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.dict(
                exclude_unset=True
            )
        if "component" in update_data and isinstance(update_data["component"], ComponentModel):
            update_data["component"] = update_data["component"].model_dump()

        for field in update_data:
            setattr(obj_current, field, update_data[field])

        db_session.add(obj_current)
        await db_session.commit()
        await db_session.refresh(obj_current)
        return obj_current

class CRUDSession(CRUDBase[Session, ISessionCreate, ISessionUpdate, ISessionList]):
    async def get_by_task_id(
        self,
        *,
        task_id: UUID,
        params: Params | None = Params(),
        db_session: AsyncSession | None = None
    ) -> Page[ISessionList]:
        """
        Get paginated sessions by task_id, ordered by created_at (latest first).
        """
        query = select(Session).where(Session.task_id == task_id)
        return await self.get_multi_paginated_ordered( # type: ignore
            params=params, order_by="created_at", order=IOrderEnum.descendent, query=query, db_session=db_session # type: ignore
        )

    async def get_by_team_id(
        self,
        *,
        team_id: UUID,
        params: Params | None = Params(),
        db_session: AsyncSession | None = None
    ) -> Page[ISessionList]:
        """
        Get paginated sessions by team_id, ordered by created_at (latest first).
        """
        query = select(Session).where(Session.team_id == team_id)
        return await self.get_multi_paginated_ordered(  # type: ignore
            params=params, order_by="created_at", order=IOrderEnum.descendent, query=query, db_session=db_session   # type: ignore
        )

    # async def get_latest_by_task(
    #     self, *, task_id: UUID, db_session: AsyncSession | None = None
    # ) -> Optional[ISessionRead]:
    #     """
    #     Get the latest session for a given task.
    #     """
    #     query = (
    #         select(Session)
    #         .where(Session.task_id == task_id)
    #         .order_by(nulls_last(Session.created_at.desc()))
    #         .limit(1)
    #     )
    #     result = await db_session.execute(query)
    #     return result.scalar_one_or_none()

    # async def get_latest_by_team(
    #     self, *, team_id: UUID, db_session: AsyncSession | None = None
    # ) -> Optional[ISessionRead]:
    #     """
    #     Get the latest session for a given team.
    #     """
    #     query = (
    #         select(Session)
    #         .where(Session.team_id == team_id)
    #         .order_by(nulls_last(Session.created_at.desc()))
    #         .limit(1)
    #     )
    #     result = await db_session.execute(query)
    #     return result.scalar_one_or_none()

    async def get_filtered_sessions(
        self,
        *,
        task_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        archived: Optional[bool] = None,
        params: Params | None = Params(),
        db_session: AsyncSession | None = None
    ) -> Page[ISessionList]:
        """
        Get filtered sessions with optional task_id, team_id, and created_at range.
        """
        query = select(Session)

        if task_id:
            query = query.where(Session.task_id == task_id)
        if team_id:
            query = query.where(Session.team_id == team_id)
        if created_after:
            query = query.where(Session.created_at >= created_after) # type: ignore
        if created_before:
            query = query.where(Session.created_at <= created_before) # type: ignore
        if archived is not None:
            query = query.where(Session.archived == archived)

        result = await self.get_multi_paginated_ordered( # type: ignore
            params=params, order_by="created_at", order=IOrderEnum.descendent, query=query, db_session=db_session # type: ignore
        )
        return result

class CRUDRun(CRUDBase[Run, IRunCreate, IRunUpdate, IRunList]):
    async def get_filtered_runs(
        self,
        *,
        session_id: UUID | None = None,
        task_id: UUID | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        archived: bool | None = None,
        params: Params | None = Params(),
        db_session: AsyncSession | None = None
    ) -> Page[IRunList]:
        """
        Get filtered runs with optional session_id, task_id, created_at range, and archived status.
        """
        query = select(Run)

        if session_id:
            query = query.where(Run.session_id == session_id)
        if task_id:
            query = query.where(Run.task_id == task_id)
        if created_after:
            query = query.where(Run.created_at >= created_after) # type: ignore
        if created_before:
            query = query.where(Run.created_at <= created_before) # type: ignore
        if archived is not None:
            query = query.where(Run.archived == archived)

        return await self.get_multi_paginated_ordered(
            params=params, order_by="created_at", order=IOrderEnum.descendent, query=query, db_session=db_session # type: ignore
        )

    async def create(
        self,
        *,
        obj_in: IRunCreate | Run,
        created_by_id: UUID | str | None = None,
        db_session: AsyncSession | None = None,
    ) -> Run:
        db_session = db_session or super().get_db_session()
        db_obj = Run.model_validate(obj_in)  # type: ignore

        if isinstance(db_obj.run_task, MessageConfig):
            db_obj.run_task = db_obj.run_task.model_dump()

        try:
            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError:
            await db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Resource already exists",
            )
        await db_session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        *,
        obj_current: Run,
        obj_new: IRunUpdate | dict[str, Any] | Run,
        db_session: AsyncSession | None = None,
    ) -> Run:
        db_session = db_session or super().get_db_session()

        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.dict(
                exclude_unset=True
            )
        if "run_task" in update_data and isinstance(update_data["run_task"], MessageConfig):
            update_data["run_task"] = update_data["run_task"].model_dump()

        for field in update_data:
            setattr(obj_current, field, update_data[field])

        db_session.add(obj_current)
        await db_session.commit()
        await db_session.refresh(obj_current)
        return obj_current

    async def get_by_task_id(
        self,
        *,
        task_id: UUID,
        params: Params | None = Params(),
        db_session: AsyncSession | None = None
    ) -> Page[IRunList]:
        """
        Get paginated runs by task_id, ordered by created_at (latest first).
        """
        query = select(Run).where(Run.task_id == task_id)
        return await self.get_multi_paginated_ordered(
            params=params, order_by="created_at", order=IOrderEnum.descendent, query=query, db_session=db_session # type: ignore
        )

    async def get_by_session_id(
        self,
        *,
        session_id: UUID,
        params: Params | None = Params(),
        db_session: AsyncSession | None = None
    ) -> Page[IRunList]:
        """
        Get paginated runs by session_id, ordered by created_at (latest first).
        """
        query = select(Run).where(Run.session_id == session_id)
        return await self.get_multi_paginated_ordered(
            params=params, order_by="created_at", order=IOrderEnum.descendent, query=query, db_session=db_session # type: ignore
        )

    # async def get_latest_by_task(
    #     self,
    #     *,
    #     task_id: UUID,
    #     db_session: AsyncSession | None = None
    # ) -> IRunRead | None:
    #     """
    #     Get the latest run for a given task.
    #     """
    #     query = select(Run).where(Run.task_id == task_id).order_by(Run.created_at.desc()).limit(1)
    #     result = await db_session.execute(query)
    #     return result.scalar_one_or_none()

    # async def get_latest_by_session(
    #     self,
    #     *,
    #     session_id: UUID,
    #     db_session: AsyncSession | None = None
    # ) -> IRunRead | None:
    #     """
    #     Get the latest run for a given session.
    #     """
    #     query = select(Run).where(Run.session_id == session_id).order_by(Run.created_at.desc()).limit(1)
    #     result = await db_session.execute(query)
    #     return result.scalar_one_or_none()

class CRUDMessage(CRUDBase[Message, IMessageCreate, IMessageUpdate, Message]):
    pass

# class CRUDSession(CRUDBase[Session, ISessionCreate, None]):
#     async def update(self, *args, **kwargs):
#         raise NotImplementedError("Update operation is not supported for Session")

#     async def get_with_runs(self, id: UUID, db_session: AsyncSession) -> Optional[ISessionReadWithRuns]:
#         query = select(Session).where(Session.id == id)
#         result = await db_session.execute(query)
#         session = result.scalar_one_or_none()
#         if session:
#             session_data = ISessionReadWithRuns.from_orm(session)
#             runs_query = select(Run).where(Run.session_id == id)
#             runs_result = await db_session.execute(runs_query)
#             session_data.runs = runs_result.scalars().all()
#             return session_data
#         return None

# class CRUDRun(CRUDBase[Run, IRunCreate, None]):
#     async def update(self, *args, **kwargs):
#         raise NotImplementedError("Update operation is not supported for Run")

#     async def get_with_messages(self, id: UUID, db_session: AsyncSession) -> Optional[IRunReadWithMessages]:
#         query = select(Run).where(Run.id == id)
#         result = await db_session.execute(query)
#         run = result.scalar_one_or_none()
#         if run:
#             run_data = IRunReadWithMessages.from_orm(run)
#             messages_query = select(Message).where(Message.run_id == id)
#             messages_result = await db_session.execute(messages_query)
#             run_data.messages = messages_result.scalars().all()
#             return run_data
#         return None

class CRUDRegistry(CRUDBase[Registry, IRegistryCreate, IRegistryUpdate, Registry]):
    pass


team = CRUDTeam(Team)
message = CRUDMessage(Message)
task = CRUDTask(Task)
session = CRUDSession(Session)
run = CRUDRun(Run)
registry = CRUDRegistry(Registry)
