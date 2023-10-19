
import pytest
from starlette import status

from typing import TYPE_CHECKING

from app.conf.config import settings
from app.contrib.school.repository import school_repo

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_school_apis(async_client: "AsyncClient", async_db) -> None:
    data = {
        'name': "schoolname",
        'address_line_1': "address_line_1",
        'address_line_2': "address_line_2",
        'web_site': "http://example.com",
        'latitude': 123456789.987654321,
        'longitude': 123456789.987654321,
        'pin_code': 1234,
    }
    response = await async_client.post(f'{settings.API_V1_STR}/school/create/', json=data)

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    result_data = result.get('data')
    school_id = result_data.get("id")
    assert result_data.get('name') == result_data.get('name')

    response = await async_client.get(f'{settings.API_V1_STR}/school/')
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result.get("rows")) > 0

    response = await async_client.get(f'{settings.API_V1_STR}/school/{school_id}/detail/')
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result.get('id') == school_id

    data = {
        'name': "schoolname_updated",
        'address_line_1': "address_line_1_updated",
        'address_line_2': "address_line_2_updated",
        'web_site': "http://updated.example.com",
        'latitude': 987654321.123456789,
        'longitude': 987654321.123456789,
    }
    response = await async_client.patch(f'{settings.API_V1_STR}/school/{school_id}/update/', json=data)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    result_data = result.get('data')
    assert result_data.get("name") == data.get("name")

    response = await async_client.get(f'{settings.API_V1_STR}/school/{school_id}/delete/')
    assert response.status_code == status.HTTP_200_OK
    is_exists = await school_repo.exists(async_db=async_db, params={'id': school_id})
    assert is_exists is False
