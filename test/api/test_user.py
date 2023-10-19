from pprint import pprint

import pytest
from starlette import status

from typing import TYPE_CHECKING

from app.conf.config import settings
from app.contrib.user.repository import user_repo, group_repo

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_apis(async_client: "AsyncClient", async_db) -> None:
    data = {
        'name': "username",
        'first_name': "First",
        'middle_name': "Middle",
        'last_name': "Last",
        'date_of_birth': "2000-01-01",
        'date_of_join': "2023-01-01",
        'date_of_left': "2023-12-01",
        'business_email': "business@example.com",
        'personal_email': "personal@example.com",
        'is_active': True,
    }
    response = await async_client.post(f'{settings.API_V1_STR}/user/create/', json=data)

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    result_data = result.get('data')
    user_id = result_data.get("id")
    assert result_data.get('name') == result_data.get('name')

    response = await async_client.get(f'{settings.API_V1_STR}/user/')
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result.get("rows")) > 0

    response = await async_client.get(f'{settings.API_V1_STR}/user/{user_id}/detail/')
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result.get('id') == user_id

    data = {
        'name': "username_updated",
        'first_name': "First2",
        'middle_name': "Middle2",
        'last_name': "Last2",
        'date_of_birth': "2000-01-02",
        'date_of_join': "2023-01-02",
        'date_of_left': "2023-12-02",
        'business_email': "business@example.com",
        'personal_email': "personal@example.com",
        'is_active': False,
    }
    response = await async_client.patch(f'{settings.API_V1_STR}/user/{user_id}/update/', json=data)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    result_data = result.get('data')
    assert result_data.get("name") == data.get("name")
    assert result_data.get("first_name") == data.get("first_name")
    assert result_data.get("middle_name") == data.get("middle_name")
    assert result_data.get("last_name") == data.get("last_name")
    assert result_data.get("date_of_birth") == data.get("date_of_birth")
    assert result_data.get("date_of_join") == data.get("date_of_join")
    assert result_data.get("date_of_left") == data.get("date_of_left")
    assert result_data.get("business_email") == data.get("business_email")
    assert result_data.get("is_active") == data.get("is_active")

    response = await async_client.get(f'{settings.API_V1_STR}/user/{user_id}/delete/')
    assert response.status_code == status.HTTP_200_OK
    is_exists = await user_repo.exists(async_db=async_db, params={'id': user_id})
    assert is_exists is False


@pytest.mark.asyncio
async def test_group_apis(async_client: "AsyncClient", async_db) -> None:
    data = {
        'name': "groupname",
    }
    response = await async_client.post(f'{settings.API_V1_STR}/group/create/', json=data)

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    result_data = result.get('data')
    group_id = result_data.get("id")
    assert result_data.get('name') == result_data.get('name')

    response = await async_client.get(f'{settings.API_V1_STR}/group/')
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result.get("rows")) > 0

    response = await async_client.get(f'{settings.API_V1_STR}/group/{group_id}/detail/')
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result.get('id') == group_id

    data = {
        'name': "groupname_updated",
    }
    response = await async_client.patch(f'{settings.API_V1_STR}/group/{group_id}/update/', json=data)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    result_data = result.get('data')
    assert result_data.get("name") == data.get("name")

    response = await async_client.get(f'{settings.API_V1_STR}/group/{group_id}/delete/')
    assert response.status_code == status.HTTP_200_OK
    is_exists = await group_repo.exists(async_db=async_db, params={'id': group_id})
    assert is_exists is False
