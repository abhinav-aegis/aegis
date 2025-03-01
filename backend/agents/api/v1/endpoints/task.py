
from fastapi import APIRouter, Depends
from fastapi_pagination import Params
from backend.agents.api import deps
from backend.common.models.user_model import User

router = APIRouter()

@router.get("")
async def get_tasks_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
):
    return {"message": "Hello World"}
