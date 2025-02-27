import pytest
from httpx import AsyncClient
from backend.common.crud import role as role_crud, tenant as tenant_crud, user as user_crud
from backend.common.core.config import settings

@pytest.fixture(scope="module")
async def cached_data(request):
    """
    Cache frequently used database values for performance.
    """

    session = request.getfixturevalue("session")  # ✅ Retrieve session dynamically

    data = {}
    data["role"] = await role_crud.get_role_by_name(name="user", db_session=session)
    data["tenant"] = await tenant_crud.get_tenant_by_name(name="tenant1", db_session=session)
    data["admin_user"] = await user_crud.get_by_email(email=settings.FIRST_SUPERUSER_EMAIL, db_session=session)

    assert data["role"], "Default role 'user' not found in DB"
    assert data["tenant"], "Default tenant 'tenant1' not found in DB"
    assert data["admin_user"], "Superuser not found in DB"
    return data

@pytest.mark.parametrize("authenticated_client", ["admin", "manager"], indirect=True)
async def test_read_users_list(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/user/list")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]["items"]) > 0  # Ensure users exist

@pytest.mark.parametrize("authenticated_client", ["user"], indirect=True)
async def test_read_users_list_forbidden(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/user/list")
    assert response.status_code == 403  # Users cannot list users

@pytest.mark.parametrize("authenticated_client", ["admin", "manager"], indirect=True)
async def test_get_user_by_id(authenticated_client: AsyncClient, session):
    """
    Retrieve the first superuser's ID from the database before testing.
    """

    from backend.common.crud import user as user_crud  # Import CRUD functions

    # Fetch the first superuser from the database
    admin_user = await user_crud.get_by_email(
        email=settings.FIRST_SUPERUSER_EMAIL, db_session=session
    )
    assert admin_user, "Superuser not found in the database"

    response = await authenticated_client.get(f"/user/{admin_user.id}")
    assert response.status_code == 200
    user_data = response.json()["data"]
    assert user_data["id"] == str(admin_user.id)

@pytest.mark.parametrize("authenticated_client", ["admin"], indirect=True)
async def test_create_user(authenticated_client: AsyncClient, session):
    """
    Retrieve role_id and tenant_id dynamically instead of assuming settings values.
    """

    from backend.common.crud import role as role_crud, tenant as tenant_crud

    role = await role_crud.get_role_by_name(name="user", db_session=session)
    tenant = await tenant_crud.get_tenant_by_name(name="tenant1", db_session=session)

    assert role, "Default role 'user' not found in DB"
    assert tenant, "Default tenant 'tenant1' not found in DB"

    new_user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "newuser@example.com",
        "password": "securepassword",
        "role_id": str(role.id),
        "tenant_id": str(tenant.id),
        "is_superuser": False
    }

    response = await authenticated_client.post("/user", json=new_user_data)
    assert response.status_code == 201
    created_user = response.json()["data"]
    assert created_user["email"] == new_user_data["email"]

@pytest.mark.parametrize("authenticated_client", ["manager", "user"], indirect=True)
async def test_create_user_forbidden(authenticated_client: AsyncClient):
    response = await authenticated_client.post("/user", json={})
    assert response.status_code == 403  # Only admins can create users

@pytest.mark.parametrize("authenticated_client", ["admin"], indirect=True)
async def test_delete_user(authenticated_client: AsyncClient, session):
    """
    Retrieve the user ID dynamically before deleting.
    """

    from backend.common.crud import role as role_crud, tenant as tenant_crud

    role = await role_crud.get_role_by_name(name="user", db_session=session)
    tenant = await tenant_crud.get_tenant_by_name(name="tenant1", db_session=session)

    assert role, "Default role 'user' not found in DB"
    assert tenant, "Default tenant 'tenant1' not found in DB"

    # Create a user first
    new_user_data = {
        "first_name": "Temp",
        "last_name": "Delete",
        "email": "deleteuser@example.com",
        "password": "securepassword",
        "role_id": str(role.id),
        "tenant_id": str(tenant.id),
        "is_superuser": False
    }
    create_response = await authenticated_client.post("/user", json=new_user_data)
    assert create_response.status_code == 201
    created_user_id = create_response.json()["data"]["id"]

    # Now delete the user
    delete_response = await authenticated_client.delete(f"/user/{created_user_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "User removed"

@pytest.mark.parametrize("authenticated_client", ["manager", "user"], indirect=True)
async def test_delete_user_forbidden(authenticated_client: AsyncClient, session):
    """
    Retrieve admin user ID before testing deletion permissions.
    """

    from backend.common.crud import user as user_crud

    # Get admin user ID dynamically
    admin_user = await user_crud.get_by_email(
        email=settings.FIRST_SUPERUSER_EMAIL, db_session=session
    )
    assert admin_user, "Superuser not found in DB"

    response = await authenticated_client.delete(f"/user/{admin_user.id}")
    assert response.status_code == 403
