from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import CityCreate, CityInDB, CityUpdate
from app.crud.cities import (
    create_city,
    get_cities,
    get_city,
    update_city,
    delete_city
)
from app.database import get_session
from app.utils.decorators import sqlalchemy_error_handler


router = APIRouter()


@router.post("/cities/", response_model=CityInDB)
@sqlalchemy_error_handler
async def create_new_city(city: CityCreate, db: Session = Depends(get_session)):
    """Create a new city."""
    return create_city(db=db, city=city)


@router.get("/cities/", response_model=list[CityInDB])
@sqlalchemy_error_handler
async def list_cities(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    """Get all cities."""
    return get_cities(db=db, skip=skip, limit=limit)


@router.get("/cities/{city_id}", response_model=CityInDB)
@sqlalchemy_error_handler
async def read_city(city_id: UUID, db: Session = Depends(get_session)):
    db_city = get_city(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city


@router.put("/cities/{city_id}", response_model=CityInDB)
@sqlalchemy_error_handler
async def modify_city(city_id: UUID, city: CityUpdate, db: Session = Depends(get_session)):
    db_city = update_city(db=db, city_id=city_id, city_data=city)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city


@router.delete("/cities/{city_id}", response_model=CityInDB)
@sqlalchemy_error_handler
async def destroy_city(city_id: UUID, db: Session = Depends(get_session)):
    db_city = delete_city(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city
