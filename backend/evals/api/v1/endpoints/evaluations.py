from fastapi import APIRouter, Depends, HTTPException

from backend.common.deps.service_deps import get_current_api_key
from backend.common.models.m2m_client_model import APIKey

from backend.evals.schema import EvaluationRequest

router = APIRouter()


@router.post("/evaluate")
async def evaluate_metric(
    request: EvaluationRequest,
    api_key: APIKey = Depends(get_current_api_key)
):
    try:
        return {"result": None}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
