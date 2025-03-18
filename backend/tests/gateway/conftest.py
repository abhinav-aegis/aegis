from typing import AsyncGenerator
import pytest
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from httpx import ASGITransport, AsyncClient
from backend.gateway.main import app
from backend.common.db.init_db import init_db
from backend.common.core.config import settings
from sqlmodel import SQLModel
import os
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

@pytest.fixture(scope="session", autouse=True)
async def setup_database() -> AsyncGenerator[sessionmaker, None]:
    """
    Sets up a **shared** database engine for tests and injects it into FastAPI's SQLAlchemyMiddleware.
    """
    os.environ["MODE"] = "testing"  # ✅ Ensure test mode is used

    # ✅ Create a single shared test database engine
    test_db_url = settings.ASYNC_TEST_DATABASE_URI
    async_engine = create_async_engine(test_db_url, connect_args={"check_same_thread": False})

    async_session = sessionmaker( # type: ignore
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:  # ✅ Correct async session usage
        await init_db(session)  # ✅ Call init_data
        await session.commit()  # ✅ Ensure data is saved

    # ✅ Inject the shared engine into FastAPI middleware
    app.add_middleware(
        SQLAlchemyMiddleware,
        custom_engine=async_engine,  # ✅ Use the shared engine
        engine_args={
            "echo": False,
            "poolclass": NullPool
        },
    )

    yield async_session
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        print("🧹 Dropped all tables after test session.")

@pytest.fixture
async def session(setup_database: sessionmaker, request) -> AsyncGenerator[AsyncSession, None]:
    async with setup_database() as session:
        try:
            yield session
        finally:
            await session.rollback()

@pytest.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture for an HTTP client accessing the `/v1` API (automatically versioned).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://{settings.API_V1_STR}",  # ✅ API version
    ) as c:
        yield c  # ✅ Return the test client

@pytest.fixture
async def authenticated_client(client: AsyncClient, request) -> AsyncGenerator[AsyncClient, None]:
    role = request.param  # Role passed from parametrize
    role_emails = {
        "admin": settings.FIRST_SUPERUSER_EMAIL,
        "manager": "manager@example.com",
        "user": "user@example.com",
    }
    login_data = {"email": role_emails[role], "password": settings.FIRST_SUPERUSER_PASSWORD}

    response = await client.post("/login", json=login_data)
    assert response.status_code == 200, f"Login failed for {role}"
    print("🔑 Authenticated as:", role)

    access_token = response.json()["data"]["access_token"]

    client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield client  # Provide authenticated client

    client.headers.pop("Authorization", None)  # Cleanup after test

@pytest.fixture
async def unversioned_client() -> AsyncGenerator:
    """
    Fixture for an HTTP client accessing the root `/` API (no versioning).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://",  # ✅ No version prefix
    ) as c:
        yield c
