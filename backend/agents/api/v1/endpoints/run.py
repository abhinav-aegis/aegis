from uuid import UUID
from datetime import datetime
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
)
from backend.common.deps import service_deps
from backend.common.models.m2m_client_model import M2MClient
from backend.agents.schemas import IRunCreate, IRunRead, IRunUpdate, IRunList
from backend.agents import crud
from backend.agents.models import Run
from backend.agents.tasks.run import run_team

router = APIRouter()

@router.get("")
async def get_runs(
    params: Params = Depends(),
    session_id: UUID | None = None,
    task_id: UUID | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    archived: bool | None = None,
    current_client: M2MClient = Depends(service_deps.get_current_api_key),
) -> IGetResponsePaginated[IRunList]:
    runs = await crud.run.get_filtered_runs(
        session_id=session_id,
        task_id=task_id,
        created_after=created_after,
        created_before=created_before,
        archived=archived,
        params=params
    )
    return create_response(data=runs) # type: ignore

@router.get("/{run_id}")
async def get_run_by_id(
    run_id: UUID,
    current_client: M2MClient = Depends(service_deps.get_current_api_key),
) -> IGetResponseBase[IRunRead]:
    run = await crud.run.get(id=run_id)

    if not run:
        raise IdNotFoundException(Run, run_id)

    run = await run_team(run_id)

    return create_response(data=run) # type: ignore

@router.post("")
async def create_run(
    run_in: IRunCreate,
    current_client: M2MClient = Depends(service_deps.get_current_api_key),
) -> IPostResponseBase[IRunRead]:
    run = await crud.run.create(obj_in=run_in)
    return create_response(data=run, message="Run created.") # type: ignore

@router.put("/{run_id}")
async def update_run(
    run_id: UUID,
    run_in: IRunUpdate,
    current_client: M2MClient = Depends(service_deps.get_current_api_key),
) -> IPutResponseBase[IRunRead]:
    run = await crud.run.get(id=run_id)
    if not run:
        raise IdNotFoundException(Run, run_id)
    run = await crud.run.update(obj_current=run, obj_new=run_in)
    return create_response(data=run, message="Run updated.") # type: ignore

@router.put("/{run_id}/archive")
async def archive_run(
    run_id: UUID,
    current_client: M2MClient = Depends(service_deps.get_current_api_key),
) -> IPutResponseBase[IRunRead]:
    """
    Archives a run by setting `archived=True`.
    """
    run = await crud.run.get(id=run_id)
    if not run:
        raise IdNotFoundException(Run, run_id)

    run = await crud.run.update(obj_current=run, obj_new={"archived": True})
    return create_response(data=run, message="Run archived.") # type: ignore
