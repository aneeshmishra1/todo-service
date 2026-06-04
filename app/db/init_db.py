from sqlalchemy.ext.asyncio import AsyncEngine
from app.models.models import Base
import logging

logger = logging.getLogger(__name__)


async def init_db(engine: AsyncEngine):
    logger.info("Creating database tables...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialization completed")


async def seed_db(session):
    # insert default admin user, roles, etc
    pass
