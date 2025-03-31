from fastapi import APIRouter
from backend.evals.api.v1.endpoints import (
    auth,
    chat
)

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
