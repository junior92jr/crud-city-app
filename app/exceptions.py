import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

# Custom exception for invalid allies


class InvalidAllyException(Exception):
    def __init__(self, invalid_allies: List[UUID]):
        self.invalid_allies = invalid_allies
        super().__init__(
            f"Invalid ally UUIDs: {', '.join(str(ally) for ally in invalid_allies)}")

# Custom handler for SQLAlchemy errors


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logging.error(f"SQLAlchemy error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred. Please try again later."}
    )

# Custom handler for invalid ally exceptions


async def invalid_ally_exception_handler(request: Request, exc: InvalidAllyException) -> JSONResponse:
    logging.error(f"Invalid ally exception: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": f"Invalid ally UUIDs: {', '.join(str(ally) for ally in exc.invalid_allies)}"}
    )
