import logging

from app.core.config import settings


def setup_logging():
    """
    Sets up structured logging for local and Cloud Run environments.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.propagate = False  # prevent double logs

    if settings.ENV == "local":
        # Local structured JSON logging
        from pythonjsonlogger import jsonlogger
        handler = logging.StreamHandler()

        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d "
            "%(path)s %(method)s %(status_code)s %(duration_ms)s %(start_time)s %(message)s"
        )
        handler.setFormatter(formatter)
    else:
        # Cloud Logging structured handler
        from google.cloud.logging.handlers import StructuredLogHandler
        handler = StructuredLogHandler()

    root_logger.addHandler(handler)

    # Remove default Uvicorn handlers to avoid duplicate logs
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "gunicorn", "gunicorn.error", "gunicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = False
        # uvicorn_logger.addFilter(RequestIDFilter())  # propagate request_id here too
