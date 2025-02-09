from sqlalchemy.orm import Session
from app.models import City
from app.schemas import CityCreate, CityUpdate
from uuid import UUID
from typing import Optional, List


def create_city(db: Session, city: CityCreate) -> City:
    """Create a new city in the database."""
    db_city = City(
        name=city.name,
        beauty=city.beauty,
        population=city.population,
        geo_location_latitude=city.geo_location_latitude,
        geo_location_longitude=city.geo_location_longitude,
    )
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


def get_cities(db: Session, skip: int = 0, limit: int = 100) -> List[City]:
    """Get cities with pagination."""
    return db.query(City).offset(skip).limit(limit).all()


def get_city(db: Session, city_id: UUID) -> Optional[City]:
    """Retrieve a city by its ID. """
    return db.query(City).get(city_id)


def update_city(db: Session, city_id: UUID, city_data: CityUpdate) -> Optional[City]:
    """Update a city's data."""
    db_city = db.query(City).get(city_id)

    if db_city:
        for field, value in city_data.model_dump(exclude_unset=True).items():
            setattr(db_city, field, value)

        db.commit()
        db.refresh(db_city)
        return db_city
    return None


def delete_city(db: Session, city_id: UUID) -> Optional[City]:
    """Delete a city by ID."""
    db_city = db.query(City).get(city_id)

    if db_city:
        db.delete(db_city)
        db.commit()
        return db_city
    return None
