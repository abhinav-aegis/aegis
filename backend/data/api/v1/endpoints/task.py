
from fastapi import APIRouter, Depends
from fastapi_pagination import Params
from backend.common.deps import service_deps
from backend.gateway.models.user_model import User

router = APIRouter()

@router.get("")
async def get_tasks_list(
    params: Params = Depends(),
    current_user: User = Depends(service_deps.get_current_client()),
):
    return {"message": "Hello World"}
