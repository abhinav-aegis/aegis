from fastapi import APIRouter, Depends
from backend.common.deps.service_deps import get_current_api_key
from backend.common.models.m2m_client_model import APIKey

router = APIRouter()

@router.get("/whoami")
async def whoami(api_key: APIKey = Depends(get_current_api_key)):
    """
    Returns information about the current API key.
    """
    return {
        "id": str(api_key.id),
        "name": api_key.name,
        "preview": api_key.preview,
        "created_by": api_key.created_by,
        "service_description": api_key.service_description,
    }
