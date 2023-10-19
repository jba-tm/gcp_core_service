from typing import Generator, Optional

from fastapi import Depends, Request, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED

from sqlalchemy.ext.asyncio import AsyncSession

from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest

from app.conf.config import settings, jwt_settings
from app.core.exceptions import HTTPInvalidToken
from app.core.schema import CommonsModel
from app.db.session import get_async_session


async def get_google_id_token(request: Request):
    header_authorization: str = request.headers.get(jwt_settings.JWT_GIT_HEADER_NAME)
    cookie_authorization: str = request.cookies.get(jwt_settings.JWT_GIT_COOKIE_NAME)
    header_scheme, header_param = get_authorization_scheme_param(header_authorization)
    cookie_scheme, cookie_param = get_authorization_scheme_param(cookie_authorization)
    if header_scheme.lower() == "bearer":
        authorization = True
        scheme = header_scheme
        param = header_param
    elif cookie_scheme.lower() == "bearer":
        authorization = True
        scheme = cookie_scheme
        param = cookie_param
    else:
        authorization = False
        scheme = ''
        param = None

    if not authorization or scheme.lower() != "bearer":
        if settings.MULTI_TENANCY_DB:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid Google ID token",
                headers={f"WWW-{jwt_settings.JWT_GIT_HEADER_NAME}": "Bearer"},
            )
        else:
            return None
    return param


async def get_audience(token: str = Depends(get_google_id_token)) -> Optional[str]:
    if not settings.MULTI_TENANCY_DB:
        return lazy_jwt_settings.JWT_AUDIENCE
    try:
        id_info = id_token.verify_oauth2_token(token, GoogleRequest())
    except GoogleAuthError as e:
        raise HTTPInvalidToken(detail=str(e))
    audience = id_info.get('aud')
    if not audience:
        raise HTTPInvalidToken(detail="Invalid token audience")
    return audience


async def get_async_db(audience: str = Depends(get_audience)) -> Generator[AsyncSession]:
    async_session_local, _ = get_async_session(audience)
    try:
        async with async_session_local() as session:
            yield session
    except Exception as e:
        raise HTTPInvalidToken(detail=str(e), status_code=500)
    finally:
        await session.close()


async def get_commons(
        page: Optional[int] = 1,
        limit: Optional[int] = settings.PAGINATION_MAX_SIZE,
) -> CommonsModel:
    """

    Get commons dict for list pagination
    :param limit:
    :param page:
    :return:
    """
    if not page or not isinstance(page, int):
        page = 1
    elif page < 0:
        page = 1
    offset = (page - 1) * limit
    return CommonsModel(
        limit=limit,
        offset=offset,
        page=page,
    )
