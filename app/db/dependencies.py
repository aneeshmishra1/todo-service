from fastapi import Request
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async_session = request.app.state.SessionLocal
    async with async_session() as session:
        yield session
