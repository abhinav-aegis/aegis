from datetime import timedelta
from uuid import UUID
from redis.asyncio import Redis
from backend.common.models.user_model import User
from backend.common.models.m2m_client_model import M2MClient
from backend.gateway.schema.common_schema import TokenType, TokenSubjectType


async def add_token_to_redis(
    redis_client: Redis,
    user: User | M2MClient,
    token: str,
    token_type: TokenType,
    expire_time: float,
    token_subject_type: TokenSubjectType = TokenSubjectType.USER
):
    if token_subject_type == TokenSubjectType.USER:
        token_key = f"user:{user.id}:{token_type}"
    else:
        token_key = f"client:{user.id}:{token_type}"

    valid_tokens = await get_valid_tokens(redis_client, user.id, token_type)
    await redis_client.sadd(token_key, token)
    if not valid_tokens:
        await redis_client.expire(token_key, timedelta(minutes=expire_time))


async def get_valid_tokens(redis_client: Redis, user_id: UUID, token_type: TokenType, token_subject_type: TokenSubjectType = TokenSubjectType.USER):
    if token_subject_type == TokenSubjectType.USER:
        token_key = f"user:{user_id}:{token_type}"
    else:
        token_key = f"client:{user_id}:{token_type}"

    valid_tokens = await redis_client.smembers(token_key)
    return valid_tokens


async def delete_tokens(redis_client: Redis, user: User | M2MClient, token_type: TokenType, token_subject_type: TokenSubjectType = TokenSubjectType.USER):
    if token_subject_type == TokenSubjectType.USER:
        token_key = f"user:{user.id}:{token_type}"
    else:
        token_key = f"client:{user.id}:{token_type}"

    valid_tokens = await redis_client.smembers(token_key)
    if valid_tokens is not None:
        await redis_client.delete(token_key)
