import gc
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
)
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
#from transformers import pipeline

from backend.common.deps.service_deps import get_redis_client
from backend.template.api.v1.api import api_router as api_router_v1
from backend.common.core.config import ModeEnum
from backend.template.core.config import settings
from backend.common.utils.fastapi_globals import GlobalsMiddleware, g


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    redis_client = await get_redis_client()
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    yield
    # shutdown
    await FastAPICache.clear()
    # models.clear()
    g.cleanup()
    gc.collect()

# Core Application Instance
app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=str(settings.ASYNC_DATABASE_URI) if settings.MODE != ModeEnum.testing else str(settings.ASYNC_TEST_DATABASE_URI),
    engine_args={
        "echo": False,
        "poolclass": NullPool
        if settings.MODE == ModeEnum.testing
        else AsyncAdaptedQueuePool
        # "pool_pre_ping": True,
        # "pool_size": settings.POOL_SIZE,
        # "max_overflow": 64,
    },
)

app.add_middleware(GlobalsMiddleware)


class CustomException(Exception):
    http_code: int
    code: str
    message: str

    def __init__(
        self,
        http_code: int = 500,
        code: str | None = None,
        message: str = "This is an error message",
    ):
        self.http_code = http_code
        self.code = code if code else str(self.http_code)
        self.message = message


@app.get("/")
async def root():
    return {settings.SERVICE_NAME: True}


# Add Routers
app.include_router(api_router_v1, prefix=settings.API_V1_STR)
