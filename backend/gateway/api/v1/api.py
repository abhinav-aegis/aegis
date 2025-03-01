from fastapi import APIRouter
from backend.gateway.api.v1.endpoints import (
    natural_language,
    user,
    team,
    login,
    role,
    group,
    cache,
    tenant,
    m2m_client
    # weather,
    # periodic_tasks,
)

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(role.router, prefix="/role", tags=["role"])
api_router.include_router(tenant.router, prefix="/tenant", tags=["tenant"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(group.router, prefix="/group", tags=["group"])
api_router.include_router(team.router, prefix="/team", tags=["team"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
api_router.include_router(m2m_client.router, prefix="/m2m_client", tags=["m2m_client"])
api_router.include_router(
    natural_language.router, prefix="/natural_language", tags=["natural_language"]
)
