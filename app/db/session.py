from pydantic import MySQLDsn
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.conf.config import settings


def get_database_uri(database: str):
    return MySQLDsn.build(
        scheme='mysql+aiomysql',
        host=settings.DATABASE_HOST,
        username=settings.DATABASE_USER,
        port=settings.DATABASE_PORT,
        password=settings.DATABASE_PASSWORD,
        path=database,
    )


def get_async_session(database: str):
    database_uri = str(get_database_uri(database))
    async_engine = create_async_engine(database_uri, pool_pre_ping=True, echo=False)

    db_uri = database_uri.replace('+aiomysql', '+pymysql')
    engine = create_engine(db_uri, pool_pre_ping=True, echo=False)

    session_local = sessionmaker(
        expire_on_commit=True,
        autocommit=False,
        autoflush=False,
        # twophase=True,
        bind=engine
    )

    async_session_local = async_sessionmaker(
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        sync_session_class=session_local
    )
    return async_session_local, async_engine
