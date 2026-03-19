from fastapi import FastAPI
from logging import Logger, getLogger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
import time
from .database import SessionLocal
from sqlalchemy.orm import Session
from .models import Logs, MethodEnum
from .raw_logs import logger as file_logger
from .config import config


async def logging_middleware(request: Request, call_next: RequestResponseEndpoint):
    logger = getLogger(__name__)
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    db = SessionLocal()
    response_time = end_time - start_time
    endpoint = request.url.path
    method = request.method
    status_code = response.status_code

    try:
        logs_entry = Logs(
            service_name="API-Failure-Predictor",
            endpoint=endpoint,
            method=MethodEnum(method),
            status_code=status_code,
            response_time=response_time
        )
        db.add(logs_entry)
        db.commit()
        logger.debug(f"Logged request: {method} {endpoint} {status_code} {response_time:.4f}s")

    except Exception as e:
        logger.error(f"Error logging request to database: {e}", exc_info=True)
        db.rollback()

    finally:
        db.close()

    file_logger.info(f"API-Failure-Predictor {method} {endpoint} {status_code} {response_time:.4f}s")

    return response
