from fastapi import APIRouter
from backend.agents.api.v1.endpoints import (
    auth,
    task,
    team,
    session,
    run
)

api_router = APIRouter()
api_router.include_router(task.router, prefix="/task", tags=["task"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(team.router, prefix="/team", tags=["team"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(run.router, prefix="/run", tags=["run"])
