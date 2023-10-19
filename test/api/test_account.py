import pytest
from datetime import timedelta

from starlette import status
from calendar import timegm

from typing import TYPE_CHECKING

from app.conf.config import settings, jwt_settings

from app.utils.datetime.timezone import now
from app.utils.security import lazy_jwt_settings

if TYPE_CHECKING:
    from app.contrib.account.models import User
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_token_api(
        async_client: "AsyncClient",
        simple_user: "User",
) -> None:
    data = {
        'username': simple_user.email,
        'password': "test_secret",
    }
    response = await async_client.post(f'{settings.API_V1_STR}/auth/get-token/', data=data)
    assert response.status_code == status.HTTP_200_OK

    response = await async_client.post(
        f'{settings.API_V1_STR}/auth/get-token/',
        data={
            'username': "invalid@example.com",
            'password': "test_secret",
        }
    )
    result = response.json()
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert result == {'detail': [{'input': 'invalid@example.com',
                                  'loc': ['body', 'username'],
                                  'msg': 'Incorrect email or password',
                                  'type': 'value_error'}]}


@pytest.mark.asyncio
async def test_expired_auth_token_api(
        async_client: "AsyncClient",
        get_user_token_headers,
        simple_user,
) -> None:
    iat = now() - timedelta(days=10)
    expire = iat + timedelta(minutes=jwt_settings.JWT_EXPIRATION_MINUTES)

    payload = {
        'user_id': simple_user.id,
        'aud': "test" if settings.MULTI_TENANCY_DB else lazy_jwt_settings.JWT_AUDIENCE,
        'iat': timegm(iat.utctimetuple()),
        "exp": timegm(expire.utctimetuple()),
        'iss': jwt_settings.JWT_ISSUER,
    }
    jwt_token = lazy_jwt_settings.JWT_ENCODE_HANDLER(payload)
    headers = {
        'Authorization': f'Bearer {jwt_token}'
    }
    response = await async_client.get(
        f'{settings.API_V1_STR}/auth/me/',
        headers=headers,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_verify_token_api(async_client: "AsyncClient", simple_user_token_headers):
    response = await async_client.post(
        f'{settings.API_V1_STR}/auth/verify-token/',
        json={"token": simple_user_token_headers.get("Authorization")}
    )

    assert response.status_code == status.HTTP_200_OK
