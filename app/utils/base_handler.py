"""
Base Handler

Decorator for uniform API response formatting, and error handling for both async and sync functions.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

import functools
import inspect
from typing import Any, Callable, TypeVar

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.logger import logger
from app.models.result import UniformResponse

# --------------------------------------------------------------------------------
# CONFIGURATION

F = TypeVar("F", bound=Callable[..., Any])


# --------------------------------------------------------------------------------
# DECORATOR DEFINITION


def handle_exception(func_name: str, args: Any, kwargs: Any, e: Exception) -> UniformResponse:
    if isinstance(e, HTTPException):
        status_code = e.status_code
        error_detail = e.detail
    else:
        status_code = 502
        error_detail = str(e)

    logger.exception("Error in %s | args: %s | kwargs: %s | Exception: %s", func_name, args, kwargs, error_detail)
    return UniformResponse(status_code=status_code, result="error", data=error_detail)


def base_handler(func: F) -> Callable[..., Any]:
    """
    Wraps an endpoint function with unified exception handler and response formatter.
    """
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> JSONResponse:
            try:
                result = await func(*args, **kwargs)
                response = UniformResponse(result="success", data=result)
            except Exception as e:
                response = handle_exception(func.__name__, args, kwargs, e)
            return JSONResponse(status_code=response.status_code, content=response.dict())

        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> JSONResponse:
            try:
                result = func(*args, **kwargs)
                response = UniformResponse(result="success", data=result)
            except Exception as e:
                response = handle_exception(func.__name__, args, kwargs, e)
            return JSONResponse(status_code=response.status_code, content=response.dict())

        return sync_wrapper
