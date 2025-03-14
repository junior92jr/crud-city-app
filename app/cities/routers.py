from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.cities.exceptions import CityNotFoundException, InvalidAllyException
from app.cities.schemas import CityCreate, CityInDB, CityUpdate
from app.cities.services import CityService
from app.database import get_session

router = APIRouter()


@router.post("/cities/", response_model=CityInDB, status_code=201)
def create_new_city(city: CityCreate, db: Session = Depends(get_session)):
    """Create a new city."""
    try:
        city_service = CityService(db)
        db_city = city_service.create_city(city)
        return db_city
    except InvalidAllyException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/cities/", response_model=list[CityInDB], status_code=200)
def list_cities(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    """Get all cities."""
    try:
        city_service = CityService(db)
        return city_service.get_cities(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/cities/{city_id}", response_model=CityInDB, status_code=200)
def read_city(city_id: UUID, db: Session = Depends(get_session)):
    """Read a city."""
    try:
        city_service = CityService(db)
        return city_service.get_city(city_uuid=city_id)
    except CityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/cities/{city_id}", response_model=CityInDB, status_code=200)
def modify_city(city_id: UUID, city: CityUpdate, db: Session = Depends(get_session)):
    """Update a city."""
    try:
        city_service = CityService(db)
        return city_service.update_city(city_uuid=str(city_id), city_data=city)
    except CityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except InvalidAllyException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/cities/{city_id}", status_code=204)
def destroy_city(city_id: UUID, db: Session = Depends(get_session)):
    """Delete a city."""
    try:
        city_service = CityService(db)

        city_service.delete_city(city_uuid=city_id)
    except CityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
