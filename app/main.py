import logging
import time

from fastapi import FastAPI, Request
from google.cloud.sql.connector import Connector, create_async_connector

from app.core.logging_config import setup_logging
from app.db.database import create_engine_and_sessionmaker
from app.db.init_db import init_db
from app.routers import todos
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("todo-service starting up...")

    connector = await create_async_connector()
    engine, session_local = create_engine_and_sessionmaker(connector)

    app.state.engine = engine
    app.state.SessionLocal = session_local

    await init_db(engine)

    logger.info("todo-service startup completed and ready to accept requests")

    try:
        yield  # ← application runs here
    finally:
        logger.info("todo-service shutting down...")

        await engine.dispose()

        logger.info("database engine disposed")
        logger.info("todo-service shutdown completed")


app = FastAPI(lifespan=lifespan)
setup_logging()
app.include_router(todos.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request start
    logger.info(
        f"Request {request.url.path} started",
        extra={
            "path": request.url.path,
            "method": request.method,
            "start_time": start_time,
            "status_code": None,
            "duration_ms": None,
        },
    )

    response = await call_next(request)
    duration = time.time() - start_time

    # Log request completion
    logger.info(
        "Request completed",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "start_time": start_time,
        },
    )

    return response


@app.get("/health")
def healthy():
    return {"status": "health is OK"}
