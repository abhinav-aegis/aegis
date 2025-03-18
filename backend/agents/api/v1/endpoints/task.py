from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi_pagination import Params
from backend.common.schemas.response_schema import (
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from backend.common.utils.exceptions import (
    IdNotFoundException,
    NameExistException,
)
from backend.common.deps import service_deps
from backend.common.models.m2m_client_model import M2MClient
from backend.agents.schemas import ITaskCreate, ITaskRead, ITaskUpdate
from backend.agents import crud
from backend.agents.models import Task

router = APIRouter()

@router.get("")
async def get_tasks(
    params: Params = Depends(),
    current_client: M2MClient = Depends(service_deps.get_current_client()),
) -> IGetResponsePaginated[ITaskRead]:
    tasks = await crud.task.get_multi_paginated(params=params)
    return create_response(data=tasks) # type: ignore


@router.get("/{task_id}")
async def get_task_by_id(
    task_id: UUID,
    current_client: M2MClient = Depends(service_deps.get_current_client()),
) -> IGetResponseBase[ITaskRead]:
    task = await crud.task.get(id=task_id)
    if not task:
        raise IdNotFoundException(Task, task_id)
    return create_response(data=task) # type: ignore

@router.post("")
async def create_task(
    task_in: ITaskCreate,
    current_client: M2MClient = Depends(service_deps.get_current_client()),
) -> IPostResponseBase[ITaskRead]:
    task = await crud.task.get_task_by_name(name=task_in.name)
    if task:
        raise NameExistException(Task, task_in.name)
    task = await crud.task.create(obj_in=task_in)
    return create_response(data=task, message="Task created.") # type: ignore

@router.put("/{task_id}")
async def update_task(
    task_id: UUID,
    task_in: ITaskUpdate,
    current_client: M2MClient = Depends(service_deps.get_current_client()),
) -> IPutResponseBase[ITaskRead]:
    task = await crud.task.get(id=task_id)
    if not task:
        raise IdNotFoundException(Task, task_id)
    task = await crud.task.update(obj_current=task, obj_new=task_in)
    return create_response(data=task, message="Task updated.") # type: ignore

@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    current_client: M2MClient = Depends(service_deps.get_current_client()),
) -> IGetResponseBase[ITaskRead]:
    task = await crud.task.get(id=task_id)
    if not task:
        raise IdNotFoundException(Task, task_id)
    task = await crud.task.remove(id=task_id)
    return create_response(data=task, message="Task deleted.") # type: ignore
