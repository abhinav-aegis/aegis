from fastapi import APIRouter
from backend.evals.api.v1.endpoints import (
    auth,
    evaluations
)

api_router = APIRouter()
api_router.include_router(evaluations.router, prefix="/evals", tags=["evals"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
