from fastapi import APIRouter
from backend.data.api.v1.endpoints import (
    auth,
    task
)

api_router = APIRouter()
api_router.include_router(task.router, prefix="/task", tags=["task"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
