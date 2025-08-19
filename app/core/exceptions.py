"""自定義異常處理"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException):
    """處理 HTTP 異常"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
        },
    )


async def value_error_handler(request: Request, exc: ValueError):
    """處理值錯誤"""
    logger.error(f"Value Error: {str(exc)}")

    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "detail": str(exc),
            "status_code": 400,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """處理一般異常"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "伺服器發生未預期的錯誤",
            "status_code": 500,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
        },
    )
