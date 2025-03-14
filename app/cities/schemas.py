from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class BeautyChoice(str, Enum):
    """Enum for city beauty choices."""

    Ugly = "Ugly"
    Average = "Average"
    Gorgeous = "Gorgeous"


class CityBase(BaseModel):
    """Base model for city data."""

    name: str
    beauty: BeautyChoice
    population: int
    geo_location_latitude: Decimal
    geo_location_longitude: Decimal
    allied_cities: Optional[List[UUID]] = None

    @field_validator("name")
    def name_not_empty(cls, value: str) -> str:
        """Ensure city name is not an empty string."""
        if not value.strip():
            raise ValueError("City Name cannot be an empty string.")
        return value

    @field_validator("population")
    def population_non_negative(cls, value: int) -> int:
        """Ensure population is a non-negative integer."""
        if value is not None and value < 0:
            raise ValueError("Population cannot be a negative value.")
        return value

    @field_validator("geo_location_latitude")
    def latitude_in_range(cls, value: Decimal) -> Decimal:
        """Ensure latitude is within the -90 to 90 range."""
        if value is not None and (value < -90.0 or value > 90.0):
            raise ValueError("Latitude needs to be in -90.0 - 90.0 range.")
        return value

    @field_validator("geo_location_longitude")
    def longitude_in_range(cls, value: Decimal) -> Decimal:
        """Ensure longitude is within the -180 to 180 range."""
        if value is not None and (value < -180.0 or value > 180.0):
            raise ValueError("Longitude needs to be in -180.0 - 180.0 range.")
        return value


class CityCreate(CityBase):
    """Model for creating a city."""

    pass


class CityUpdate(CityBase):
    """Model for updating a city (all fields optional)."""

    name: Optional[str] = None
    beauty: Optional[BeautyChoice] = None
    population: Optional[int] = None
    geo_location_latitude: Optional[Decimal] = None
    geo_location_longitude: Optional[Decimal] = None
    allied_cities: Optional[List[UUID]] = None


class CityInDB(CityBase):
    """Model for returning city data from the database."""

    city_uuid: UUID


class CityInDBWithAllyForce(CityInDB):
    """Model for returning city data with allied power."""

    allied_power: int
