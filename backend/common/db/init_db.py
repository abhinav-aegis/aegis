from sqlmodel.ext.asyncio.session import AsyncSession
from backend.common import crud
from backend.common.schemas.user_schema import IUserCreate
from backend.common.schemas.role_schema import IRoleCreate
from backend.common.schemas.tenant_schema import ITenantCreate
from backend.common.schemas.m2m_client_schema import IM2MClientCreate
from backend.common.core.config import settings
from typing import List, Dict


# Predefined Tenants and Roles
tenants: List[ITenantCreate] = [
    ITenantCreate(name="root", customer_id="root", is_root=True),
    ITenantCreate(name="tenant1", customer_id="tenant_1"),
]

roles: List[IRoleCreate] = [
    IRoleCreate(name="admin", description="This the Admin role"),
    IRoleCreate(name="manager", description="Manager role"),
    IRoleCreate(name="data", description="Data Engineer role to manage data pipeline"),
    IRoleCreate(name="agent", description="Agent Manager role to manage agents"),
    IRoleCreate(name="user", description="User role"),
]

raw_users = [
    {"first_name": "Admin", "last_name": "FastAPI", "email": settings.FIRST_SUPERUSER_EMAIL, "role": "admin", "tenant": "root", "is_superuser": True},
    {"first_name": "Manager", "last_name": "FastAPI", "email": "manager@example.com", "role": "manager", "tenant": "root", "is_superuser": False},
    {"first_name": "User", "last_name": "FastAPI", "email": "user@example.com", "role": "user", "tenant": "tenant1", "is_superuser": False},
]

m2m_clients: List[IM2MClientCreate] = [
    IM2MClientCreate(
        client_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
        client_name="test_client",
        service_description="Test client service",
        secret=settings.M2M_CLIENT_SECRET
    )
]

async def init_db(db_session: AsyncSession) -> None:
    """
    Initialize tenants, roles, and users while resolving tenant_id before user creation.
    """

    tenant_ids: Dict[str, str] = {}

    for tenant in tenants:
        existing_tenant = await crud.tenant.get_tenant_by_name(
            name=tenant.name, db_session=db_session
        )
        if not existing_tenant:
            new_tenant = await crud.tenant.create(obj_in=tenant, db_session=db_session)
            tenant_ids[tenant.name] = str(new_tenant.id)
        else:
            tenant_ids[tenant.name] = str(existing_tenant.id)

    role_ids: Dict[str, str] = {}

    for role in roles:
        existing_role = await crud.role.get_role_by_name(
            name=role.name, db_session=db_session
        )
        if not existing_role:
            new_role = await crud.role.create(obj_in=role, db_session=db_session)
            role_ids[role.name] = str(new_role.id)
        else:
            role_ids[role.name] = str(existing_role.id)

    for raw_user in raw_users:
        tenant_id = tenant_ids.get(raw_user["tenant"]) # type: ignore
        role_id = role_ids.get(raw_user["role"]) # type: ignore

        if not tenant_id or not role_id:
            raise ValueError(f"Invalid tenant or role for user {raw_user['email']}")

        existing_user = await crud.user.get_by_email(
            email=raw_user["email"], db_session=db_session # type: ignore
        )
        if not existing_user:
            user_create = IUserCreate(
                first_name=raw_user["first_name"],
                last_name=raw_user["last_name"],
                password=settings.FIRST_SUPERUSER_PASSWORD,
                email=raw_user["email"],
                is_superuser=raw_user["is_superuser"],
                tenant_id=tenant_id,
                role_id=role_id,
            )
            await crud.user.create_with_role(obj_in=user_create, db_session=db_session)

    for m2m_client in m2m_clients:
        existing_client = await crud.m2m_client.get_by_client_id(
            client_id=m2m_client.client_id, db_session=db_session
        )
        if not existing_client:
            await crud.m2m_client.create_with_hashed_secret(obj_in=m2m_client, db_session=db_session)
