import pytest
import asyncio
import sys
from typing import TYPE_CHECKING, Generator, Any, Iterator

from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from app.main import app

if TYPE_CHECKING:
    from fastapi import FastAPI
    from sqlalchemy.ext.asyncio import AsyncSession


def get_current_event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Yield an event loop.
    This is necessary because pytest-asyncio needs an event loop with a with an equal or higher
    pytest fixture scope as any of the async fixtures. And remember, pytest-asyncio is what allows us
    to have async pytest fixtures.
    """
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        # Avoid "RuntimeError: Event loop is closed" on Windows when tearing down tests
        # https://github.com/encode/httpx/issues/914
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:

        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


event_loop = pytest.fixture(fixture_function=get_current_event_loop, scope='session', name="event_loop")


@pytest.fixture(scope="session")
async def async_db():
    from app.db.session import get_async_session
    from app.db.models import metadata
    from sqlalchemy_utils import database_exists, create_database, drop_database

    test_session, test_async_engine = get_async_session("test")
    database_uri = test_async_engine.url.render_as_string(hide_password=False).replace('+aiomysql', '+pymysql')
    if not database_exists(database_uri):
        create_database(database_uri)
    # connect to the database
    is_echo = test_async_engine.echo
    test_async_engine.echo = False
    async with test_async_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)  # Create the tables.
    test_async_engine.echo = is_echo

    async with test_async_engine.connect() as conn:
        async with test_session(bind=conn) as session:
            yield session

        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        # await conn.rollback()

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await test_async_engine.dispose()

    # Drop test database
    if database_exists(database_uri):
        drop_database(database_uri)


@pytest.fixture(autouse=True)
async def application() -> Generator["FastAPI", Any, None]:
    yield app


@pytest.fixture
async def async_client(
        application: "FastAPI", async_db: "AsyncSession",
) -> Generator[AsyncClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    from app.routers import dependency

    async def _get_test_async_db():
        return async_db

    async def _test_get_audience() -> dict:
        return "test"

    application.dependency_overrides[dependency.get_async_db] = _get_test_async_db
    application.dependency_overrides[dependency.get_audience] = _test_get_audience

    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as _client:
            try:
                yield _client
            except Exception as exc:  # pylint: disable=broad-except
                print(exc)
