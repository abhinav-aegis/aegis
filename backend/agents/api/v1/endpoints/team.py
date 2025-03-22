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
)
from backend.common.deps import service_deps
from backend.common.models.m2m_client_model import M2MClient
from backend.agents.schemas import ITeamCreate, ITeamRead, ITeamUpdate
from backend.agents import crud
from backend.agents.models import Team

router = APIRouter()

@router.get("")
async def get_teams(
    params: Params = Depends(),
    current_client: M2MClient = Depends(service_deps.get_current_api_key),
) -> IGetResponsePaginated[ITeamRead]:
    teams = await crud.team.get_multi_paginated(params=params)
    return create_response(data=teams) # type: ignore

@router.get("/{team_id}")
async def get_team_by_id(
    team_id: UUID,
    current_client: M2MClient = Depends(service_deps.get_current_api_key),
) -> IGetResponseBase[ITeamRead]:
    team = await crud.team.get(id=team_id)
    if not team:
        raise IdNotFoundException(Team, team_id)
    return create_response(data=team) # type: ignore

@router.post("")
async def create_team(
    team_in: ITeamCreate,
    current_client: M2MClient = Depends(service_deps.get_current_api_key),
) -> IPostResponseBase[ITeamRead]:
    team = await crud.team.create(obj_in=team_in)
    return create_response(data=team, message="Team created.") # type: ignore

@router.put("/{team_id}")
async def update_team(
    team_id: UUID,
    team_in: ITeamUpdate,
    current_client: M2MClient = Depends(service_deps.get_current_api_key),
) -> IPutResponseBase[ITeamRead]:
    team = await crud.team.get(id=team_id)
    if not team:
        raise IdNotFoundException(Team, team_id)
    team = await crud.team.update(obj_current=team, obj_new=team_in)
    return create_response(data=team, message="Team updated.") # type: ignore

@router.delete("/{team_id}")
async def delete_team(
    team_id: UUID,
    current_client: M2MClient = Depends(service_deps.get_current_api_key),
) -> IGetResponseBase[ITeamRead]:
    team = await crud.team.get(id=team_id)
    if not team:
        raise IdNotFoundException(Team, team_id)
    team = await crud.team.remove(id=team_id)
    return create_response(data=team, message="Team deleted.")  # type: ignore
