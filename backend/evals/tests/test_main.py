import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root(unversioned_client: AsyncClient):
    response = await unversioned_client.get('/')
    assert response is not None
    assert response.status_code == 200
    assert response.json() == {"evals": True}
