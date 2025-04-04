from collections.abc import AsyncGenerator
from typing import Callable, Optional, Awaitable, List
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, OAuthFlowClientCredentials

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, status, Header, Security
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from jwt import DecodeError, ExpiredSignatureError, MissingRequiredClaimError
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.common import crud
from backend.common.core.config import settings
from backend.common.core.security import decode_token, http_bearer_scheme
from backend.common.db.session import SessionLocalCelery
from backend.common.models.m2m_client_model import M2MClient, APIKey
from backend.common.schemas.common_schema import TokenType, TokenSubjectType
from backend.gateway.utils.token import get_valid_tokens


class Oauth2ClientCredentials(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            clientCredentials=OAuthFlowClientCredentials(tokenUrl=tokenUrl, scopes=scopes)
        )

        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str | None = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

reusable_oauth2 = Oauth2ClientCredentials(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token"
)

async def get_redis_client() -> Redis:
    redis = await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )
    return redis


async def get_jobs_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocalCelery() as session:
        yield session

def get_current_client(required_roles: Optional[list[str]] = None) -> Callable[[], Awaitable[M2MClient]]:
    async def current_client(
        access_token: str = Depends(reusable_oauth2),
        redis_client: Redis = Depends(get_redis_client),
    ) -> M2MClient:
        try:
            payload = decode_token(access_token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your token has expired. Please log in again.",
            )
        except DecodeError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Error when decoding the token. Please check your request.",
            )
        except MissingRequiredClaimError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="There is no required field in your token. Please contact the administrator.",
            )

        id = payload["sub"]
        valid_access_tokens = await get_valid_tokens(
            redis_client, id, TokenType.ACCESS, token_subject_type=TokenSubjectType.CLIENT
        )
        if valid_access_tokens and access_token not in valid_access_tokens:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        client: M2MClient | None = await crud.m2m_client.get(id=id)
        if not client:
            raise HTTPException(status_code=404, detail="User not found")

        if not client.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        return client

    return current_client

async def get_current_api_key(
    credentials = Security(http_bearer_scheme),
) -> APIKey:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header",
        )

    raw_key = credentials.credentials.strip()
    api_key_obj = await crud.api_key.get_by_raw_key(raw_key=raw_key)

    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API key",
        )

    return api_key_obj


async def get_request_context(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    x_groups: Optional[str] = Header(None, alias="X-Groups"),
) -> dict:
    groups: List[str] = [grp.strip() for grp in x_groups.split(",")] if x_groups else []
    return {"user_id": x_user_id, "tenant_id": x_tenant_id, "groups": groups}
