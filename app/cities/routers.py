from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.cities.exceptions import InvalidAllyException
from app.cities.schemas import CityCreate, CityInDB, CityUpdate
from app.cities.services import CityService, delete_city, get_city, update_city
from app.database import get_session
from app.utils.decorators import sqlalchemy_error_handler

router = APIRouter()


class CityRouter:
    """City router class."""

    def __init__(self, db: Session):
        self.db = db
        self.city_service = CityService(db)

    def create_new_city(self, city: CityCreate) -> CityInDB:
        """Create a new city."""
        try:
            db_city = self.city_service.create_city(city)
            return CityInDB(
                city_uuid=db_city.city_uuid,
                name=db_city.name,
                beauty=db_city.beauty,
                population=db_city.population,
                geo_location_latitude=db_city.geo_location_latitude,
                geo_location_longitude=db_city.geo_location_longitude,
                allied_cities=db_city.allied_cities,
            )
        except InvalidAllyException as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/cities/", response_model=CityInDB, status_code=201)
def create_new_city(city: CityCreate, db: Session = Depends(get_session)):
    """Create a new city."""

    city_router = CityRouter(db)
    return city_router.create_new_city(city)


@router.get("/cities/", response_model=list[CityInDB])
@sqlalchemy_error_handler
async def list_cities(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_session)
):
    """Get all cities."""

    city_service = CityService(db)
    return city_service.get_cities(skip=skip, limit=limit)


@router.get("/cities/{city_id}", response_model=CityInDB)
@sqlalchemy_error_handler
async def read_city(city_id: UUID, db: Session = Depends(get_session)):
    db_city = get_city(db=db, city_uuid=city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city


@router.put("/cities/{city_id}", response_model=CityInDB)
@sqlalchemy_error_handler
async def modify_city(
    city_id: UUID, city: CityUpdate, db: Session = Depends(get_session)
):
    db_city = update_city(db=db, city_uuid=city_id, city=city)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city


@router.delete("/cities/{city_id}", response_model=CityInDB)
@sqlalchemy_error_handler
async def destroy_city(city_id: UUID, db: Session = Depends(get_session)):
    db_city = delete_city(db=db, city_uuid=city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city
