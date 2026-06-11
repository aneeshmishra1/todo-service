import logging

from google.cloud.sql.connector import Connector
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings


DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
INSTANCE_CONNECTION_NAME = settings.INSTANCE_CONNECTION_NAME


def create_engine_and_sessionmaker(connector: Connector):
    async def getconn():
        return await connector.connect_async(
            INSTANCE_CONNECTION_NAME,
            "asyncpg",
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
        )

    engine = create_async_engine(
        "postgresql+asyncpg://",
        async_creator=getconn,
        poolclass=NullPool,
    )

    sessionmaker = async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    return engine, sessionmaker
