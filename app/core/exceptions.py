from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.logger import logger

def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail} at {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "failed",
            "message": exc.detail,
            "path": request.url.path
        }
    )

def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unexpected error at {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "failed",
            "message": "Internal server error",
            "path": request.url.path
        }
    )