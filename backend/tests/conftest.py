from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import ASGITransport, AsyncClient
from backend.gateway.main import app
from backend.agents.main import app as app_agents
from backend.common.db.session import SessionLocal, engine as async_engine
from backend.common.db.init_db import init_db
from backend.common.core.config import settings
from sqlmodel import SQLModel
import os
from sqlalchemy import event

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    os.environ["MODE"] = "testing"  # Ensure test DB is used

    async with async_engine.begin() as async_conn:
        await async_conn.run_sync(SQLModel.metadata.create_all)  # ✅ Direct table creation

    # Initialize test data
    async with SessionLocal() as session:
        await init_db(session)

    yield  # Run tests

    # Cleanup: Drop tables after tests
    async with async_engine.begin() as async_conn:
        await async_conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def session():
    """
    SqlAlchemy testing suite.

    Using ORM while rolling back changes after commit to have independant test cases.

    Implementation of "Joining a Session into an External Transaction (such as for test suite)"
    recipe from sqlalchemy docs :
    https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites

    Inspiration also found on:
    https://github.com/sqlalchemy/sqlalchemy/issues/5811#issuecomment-756269881
    """
    async with async_engine.connect() as conn:

        await conn.begin()
        await conn.begin_nested()

        async_session = AsyncSession(
            conn,
            expire_on_commit=False
        )

        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(session, transaction):
            if conn.closed:
                return
            if not conn.in_nested_transaction():
                conn.sync_connection.begin_nested()

        yield async_session

        await async_session.close()
        await conn.rollback()

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


@pytest.fixture
async def client() -> AsyncGenerator:
    """
    Fixture for an HTTP client accessing the `/v1` API (automatically versioned).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://{settings.API_V1_STR}"  # ✅ Automatically adds `/v1` or other API version
    ) as c:
        yield c

@pytest.fixture
async def app_client() -> AsyncGenerator:
    """
    Fixture for an HTTP client accessing the `/v1` API (automatically versioned).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app_agents),
        base_url=f"http://{settings.API_V1_STR}"  # ✅ Automatically adds `/v1` or other API version
    ) as c:
        yield c


@pytest.fixture
async def admin(versioned_client: AsyncClient) -> AsyncGenerator:
    """
    Fixture for a logged-in superuser client using the pre-existing user from init_db.
    """

    login_data = {
        "email": settings.FIRST_SUPERUSER_EMAIL,  # The pre-existing superuser
        "password": settings.FIRST_SUPERUSER_PASSWORD
    }

    response = await client.post("/login", json=login_data)
    assert response.status_code == 200, "Superuser login failed in test setup"

    access_token = response.json()["data"]["access_token"]

    client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield client

    client.headers.pop("Authorization", None)  # Cleanup after test


@pytest.fixture
async def manager(client: AsyncClient) -> AsyncGenerator:
    """
    Fixture for a logged-in manager user.
    """

    login_data = {
        "email": "manager@example.com",  # Pre-created manager user
        "password": settings.FIRST_SUPERUSER_PASSWORD  # Adjust if password differs
    }

    response = await client.post("/login", json=login_data)
    assert response.status_code == 200, "Manager login failed in test setup"

    access_token = response.json()["data"]["access_token"]

    client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield client

    client.headers.pop("Authorization", None)


@pytest.fixture
async def user(client: AsyncClient) -> AsyncGenerator:
    """
    Fixture for a logged-in normal user.
    """

    login_data = {
        "email": "user@example.com",  # Pre-created normal user
        "password": settings.FIRST_SUPERUSER_PASSWORD
    }

    response = await client.post("/login", json=login_data)
    assert response.status_code == 200, "User login failed in test setup"

    access_token = response.json()["data"]["access_token"]

    client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield client

    client.headers.pop("Authorization", None)

@pytest.fixture
async def authenticated_client(client: AsyncClient, request) -> AsyncGenerator:
    role = request.param  # Role passed from parametrize

    role_emails = {
        "admin": settings.FIRST_SUPERUSER_EMAIL,
        "manager": "manager@example.com",
        "user": "user@example.com",
    }

    login_data = {"email": role_emails[role], "password": settings.FIRST_SUPERUSER_PASSWORD}

    response = await client.post("/login", json=login_data)
    assert response.status_code == 200, f"Login failed for {role}"

    access_token = response.json()["data"]["access_token"]

    client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield client  # Provide authenticated client

    client.headers.pop("Authorization", None)  # Cleanup after test
