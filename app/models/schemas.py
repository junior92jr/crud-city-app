"""Module that contains Schemas that validates fields from database tables."""

import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.common import constants
from app.models.validators import CreateValidations, UpdateValidations


class BeautyChoices(str, Enum):
    """Beauty attribute choice enum class."""

    UGLY_CHOICE = constants.UGLY_CHOICE
    AVERAGE_CHOICE = constants.AVERAGE_CHOICE
    GORGEOUS_CHOICE = constants.GORGEOUS_CHOICE


@dataclass
class CreateCitySchema(CreateValidations):
    """Schema to create a City Object."""

    name: str
    beauty: BeautyChoices
    population: int
    geo_location_latitude: float
    geo_location_longitude: float
    allied_cities: Optional[List[uuid.UUID]] = None


@dataclass
class UpdateCitySchema(UpdateValidations):
    """Schema to update a City Object."""

    name: Optional[str] = None
    beauty: Optional[BeautyChoices] = None
    population: Optional[int] = None
    geo_location_latitude: Optional[float] = None
    geo_location_longitude: Optional[float] = None
    allied_cities: Optional[List[uuid.UUID]] = None


@dataclass
class CitySchema:
    """Schema to visualize a City Object."""

    city_uuid: uuid.UUID
    name: str
    beauty: str
    population: int
    geo_location_latitude: float
    geo_location_longitude: float
    allied_cities: List[uuid.UUID]

    def to_dict(self):
        """kmnasdkasmndklmasdlas."""

        return dict(asdict(self).items())


@dataclass
class CitySchemaWithAllyForce(CitySchema):
    """Schema to visualize a City Object with ally power."""

    allied_power: int
