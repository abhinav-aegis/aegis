from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials

from fastapi.param_functions import Form
from jwt import DecodeError, ExpiredSignatureError, MissingRequiredClaimError
from redis.asyncio import Redis
from fastapi.security import HTTPBasic

from backend.gateway import crud
from backend.common.deps.service_deps import get_redis_client
from backend.common.core import security
from backend.common.core.config import settings
from backend.common.core.security import decode_token
from backend.gateway.schema.common_schema import TokenType, TokenSubjectType
from backend.common.schemas.response_schema import IPostResponseBase, create_response
from backend.common.utils.token import add_token_to_redis, get_valid_tokens
from uuid import UUID
from pydantic import BaseModel

router = APIRouter()

class TokenRead(BaseModel):
    access_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class OAuth2ClientCredentialsRequestForm:
    def __init__(
        self,
        grant_type: str = Form(None, pattern="^(client_credentials|refresh_token)$"),
        scope: str = Form(""),
        client_id: UUID | None = Form(None),
        client_secret: str | None = Form(None),
    ):
        self.grant_type = grant_type
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


@router.post(
        "/new_access_token",
        status_code=201,
        include_in_schema=False,
    )
async def get_new_access_token(
    body: RefreshToken = Body(...),
    redis_client: Redis = Depends(get_redis_client),
) -> IPostResponseBase[TokenRead]:
    """
    Gets a new access token using the refresh token for future requests.
    """
    if not body:
        raise HTTPException(status_code=400, detail="No token provided")
    try:
        payload = decode_token(body.refresh_token)
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

    if payload["type"] == "refresh":
        id = payload["sub"]
        valid_refresh_tokens = await get_valid_tokens(
            redis_client, id, TokenType.REFRESH
        )
        if valid_refresh_tokens and body.refresh_token not in valid_refresh_tokens:
            raise HTTPException(status_code=403, detail="Refresh token invalid")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        client = await crud.m2m_client.get(id=id)
        if client and client.is_active:
            access_token = security.create_access_token(
                payload["sub"], expires_delta=access_token_expires
            )
            valid_access_get_valid_tokens = await get_valid_tokens(
                redis_client, client.id, TokenType.ACCESS
            )
            if valid_access_get_valid_tokens:
                await add_token_to_redis(
                    redis_client,
                    client,
                    access_token,
                    TokenType.ACCESS,
                    settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                    TokenSubjectType.CLIENT
                )
            return create_response( # type: ignore
                data=TokenRead(access_token=access_token, token_type="bearer"), # nosec
                message="Access token generated correctly",
            )
        else:
            raise HTTPException(status_code=404, detail="User inactive")
    else:
        raise HTTPException(status_code=404, detail="Incorrect token")

token_scheme = HTTPBasic(auto_error=False)

@router.post("/access-token", include_in_schema=False)
async def login_access_token(
    form_data: OAuth2ClientCredentialsRequestForm = Depends(),
    redis_client: Redis = Depends(get_redis_client),
    basic_credentials: Optional[HTTPBasicCredentials] = Depends(token_scheme),
) -> TokenRead:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    if form_data.client_id and form_data.client_secret:
        client_id = form_data.client_id
        client_secret = form_data.client_secret
    elif basic_credentials:
        try:
            client_id = UUID(basic_credentials.username)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid client_id")
        client_secret = basic_credentials.password
    else:
        raise HTTPException(status_code=400, detail="Client credentials not found")

    client = await crud.m2m_client.authenticate(
        client_id=client_id, client_secret=client_secret
    )
    if not client:
        raise HTTPException(status_code=400, detail="Incorrect client_id or client_secret")
    elif not client.is_active:
        raise HTTPException(status_code=400, detail="Inactive client")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        client.id, expires_delta=access_token_expires
    )
    valid_access_tokens = await get_valid_tokens(
        redis_client, client.id, TokenType.ACCESS, token_subject_type=TokenSubjectType.CLIENT
    )
    if valid_access_tokens:
        await add_token_to_redis(
            redis_client,
            client,
            access_token,
            TokenType.ACCESS,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            TokenSubjectType.CLIENT
        )
    return TokenRead(access_token=access_token, token_type="bearer") # nosec
