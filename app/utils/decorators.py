from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from typing import Callable, Any


def sqlalchemy_error_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to handle SQLAlchemy errors with proper typing."""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    return wrapper
