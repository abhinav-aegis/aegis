from fastapi import HTTPException
from typing import Any, Generic, TypeVar
from uuid import UUID
from backend.common.schemas.common_schema import IOrderEnum
from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_async_sqlalchemy import db
from fastapi_pagination import Params, Page
from pydantic import BaseModel
from sqlmodel import SQLModel, select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select
from sqlalchemy import exc
from typing import Sequence

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
ModelListReadType = TypeVar("ModelListReadType", bound=SQLModel)
T = TypeVar("T", bound=SQLModel)

def handle_integrity_error(e: exc.IntegrityError) -> None:
    error_message = str(e.orig) if e.orig else str(e)
    if "duplicate key" in error_message:
        raise HTTPException(
            status_code=409,
            detail="Resource already exists (duplicate key constraint violation)."
        )
    elif "foreign key constraint" in error_message:
        raise HTTPException(
            status_code=400,
            detail="Invalid foreign key reference (missing related record)."
        )
    elif "null value in column" in error_message:
        raise HTTPException(
            status_code=400,
            detail="Missing required field (null value constraint violation)."
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Database integrity error: {error_message}"
        )


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ModelListReadType]):
    def __init__(self, model: type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**
        * `model`: A SQLModel model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.db = db

    def get_db_session(self) -> AsyncSession:
        return self.db.session

    async def get(
        self, *, id: UUID | str, db_session: AsyncSession | None = None
    ) -> ModelType | None:
        db_session = db_session or self.db.session
        query = select(self.model).where(self.model.id == id) # type: ignore
        response = await db_session.execute(query)
        return response.scalar_one_or_none()

    async def get_by_ids(
        self,
        *,
        list_ids: list[UUID | str],
        db_session: AsyncSession | None = None,
    ) -> Sequence[ModelType] | None:
        db_session = db_session or self.db.session
        response = await db_session.execute(
            select(self.model).where(self.model.id.in_(list_ids)) # type: ignore
        )
        return response.scalars().all()

    async def get_count(
        self, db_session: AsyncSession | None = None
    ) -> ModelType | None:
        db_session = db_session or self.db.session
        response = await db_session.execute(
            select(func.count()).select_from(select(self.model).subquery())
        )
        return response.scalar_one()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        query: Select[ModelType] | None = None,
        db_session: AsyncSession | None = None,
    ) -> Sequence[ModelListReadType]:
        db_session = db_session or self.db.session
        if query is None:
            query = select(self.model).offset(skip).limit(limit).order_by(self.model.id) # type: ignore

        if query is None:
            raise AssertionError("Query is None")

        response = await db_session.execute(query)
        return response.scalars().all()

    async def get_multi_paginated(
        self,
        *,
        params: Params | None = Params(),
        query: Select[ModelType] | None = None,
        db_session: AsyncSession | None = None,
    ) -> Page[ModelListReadType]:
        db_session = db_session or self.db.session
        if query is None:
            query = select(self.model) # type: ignore

        output = await paginate(db_session, query, params) # type: ignore
        return output

    async def get_multi_paginated_ordered(
        self,
        *,
        params: Params | None = Params(),
        order_by: str | None = None,
        order: IOrderEnum | None = IOrderEnum.ascendent,
        query: T | Select[T] | None = None,
        db_session: AsyncSession | None = None,
    ) -> Page[ModelListReadType]:
        db_session = db_session or self.db.session

        columns = self.model.__table__.columns # type: ignore

        if order_by is None or order_by not in columns:
            order_by = "id"

        if query is None:
            if order == IOrderEnum.ascendent:
                query = select(self.model).order_by(columns[order_by].asc())  # type: ignore
            else:
                query = select(self.model).order_by(columns[order_by].desc()) # type: ignore

        return await paginate(db_session, query, params) # type: ignore

    async def get_multi_ordered(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order: IOrderEnum | None = IOrderEnum.ascendent,
        db_session: AsyncSession | None = None,
    ) -> list[ModelListReadType]:
        db_session = db_session or self.db.session

        columns = self.model.__table__.columns # type: ignore

        if order_by is None or order_by not in columns:
            order_by = "id"

        if order == IOrderEnum.ascendent:
            query = (
                select(self.model)
                .offset(skip)
                .limit(limit)
                .order_by(columns[order_by].asc())
            )
        else:
            query = (
                select(self.model)
                .offset(skip)
                .limit(limit)
                .order_by(columns[order_by].desc())
            )

        response = await db_session.execute(query)
        return response.scalars().all() # type: ignore

    async def create(
        self,
        *,
        obj_in: CreateSchemaType | ModelType,
        created_by_id: UUID | str | None = None,
        db_session: AsyncSession | None = None,
    ) -> ModelType:
        db_session = db_session or self.db.session
        db_obj = self.model.model_validate(obj_in)  # type: ignore

        if created_by_id:
            db_obj.created_by_id = created_by_id

        try:
            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError as e:
            db_session.rollback()
            handle_integrity_error(e)

        await db_session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        *,
        obj_current: ModelType,
        obj_new: UpdateSchemaType | dict[str, Any] | ModelType,
        db_session: AsyncSession | None = None,
    ) -> ModelType:
        db_session = db_session or self.db.session
        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.dict(
                exclude_unset=True
            )  # This tells Pydantic to not include the values that were not sent
        for field in update_data:
            setattr(obj_current, field, update_data[field])

        db_session.add(obj_current)
        await db_session.commit()
        await db_session.refresh(obj_current)
        return obj_current

    async def remove(
        self, *, id: UUID | str, db_session: AsyncSession | None = None
    ) -> ModelType:
        db_session = db_session or self.db.session
        response = await db_session.execute(
            select(self.model).where(self.model.id == id) # type: ignore
        )
        obj = response.scalar_one()
        await db_session.delete(obj)
        await db_session.commit()
        return obj
