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
from backend.agents.schemas import ISessionCreate, ISessionRead, ISessionUpdate
from backend.agents import crud
from backend.agents.models import Session

router = APIRouter()

@router.get("")
async def get_sessions(
    params: Params = Depends(),
    task_id: UUID | None = None,
    team_id: UUID | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    archived: bool | None = None,
    current_client: M2MClient = Depends(service_deps.get_current_client()),
) -> IGetResponsePaginated[ISessionRead]:
    sessions = await crud.session.get_filtered_sessions(
        task_id=task_id,
        team_id=team_id,
        created_after=created_after,
        created_before=created_before,
        archived=archived,
        params=params
    )
    return create_response(data=sessions) # type: ignore

@router.get("/{session_id}")
async def get_session_by_id(
    session_id: UUID,
    current_client: M2MClient = Depends(service_deps.get_current_client()),
) -> IGetResponseBase[ISessionRead]:
    session = await crud.session.get(id=session_id)
    if not session:
        raise IdNotFoundException(Session, session_id)
    return create_response(data=session) # type: ignore

@router.post("")
async def create_session(
    session_in: ISessionCreate,
    current_client: M2MClient = Depends(service_deps.get_current_client()),
) -> IPostResponseBase[ISessionRead]:
    session = await crud.session.create(obj_in=session_in)
    return create_response(data=session, message="Session created.") # type: ignore

@router.put("/{session_id}")
async def update_session(
    session_id: UUID,
    session_in: ISessionUpdate,
    current_client: M2MClient = Depends(service_deps.get_current_client()),
) -> IPutResponseBase[ISessionRead]:
    session = await crud.session.get(id=session_id)
    if not session:
        raise IdNotFoundException(Session, session_id)
    session = await crud.session.update(obj_current=session, obj_new=session_in)
    return create_response(data=session, message="Session updated.") # type: ignore

@router.put("/{session_id}/archive")
async def archive_session(
    session_id: UUID,
    current_client: M2MClient = Depends(service_deps.get_current_client()),
) -> IPutResponseBase[ISessionRead]:
    """
    Archives a session by setting `archived=True`.
    """
    session = await crud.session.get(id=session_id)
    if not session:
        raise IdNotFoundException(Session, session_id)

    session = await crud.session.update(obj_current=session, obj_new={"archived": True})
    return create_response(data=session, message="Session archived.") # type: ignore
