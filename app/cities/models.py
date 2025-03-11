import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, Enum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class BeautyChoice(str, PyEnum):
    Ugly = "Ugly"
    Average = "Average"
    Gorgeous = "Gorgeous"


class City(Base):
    __tablename__ = 'city'

    city_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(64), nullable=False)
    beauty = Column(Enum(BeautyChoice, name="beautychoice"), nullable=True)
    population = Column(Integer, nullable=False)
    geo_location_latitude = Column(Numeric(9, 6), nullable=False)
    geo_location_longitude = Column(Numeric(9, 6), nullable=False)

    allied_cities = relationship("AlliedCity", back_populates="city")


class AlliedCity(Base):
    __tablename__ = 'allied_city'

    city_uuid = Column(UUID(as_uuid=True), ForeignKey(
        'city.city_uuid'), primary_key=True)
    ally_uuid = Column(UUID(as_uuid=True), primary_key=True)

    city = relationship("City", back_populates="allied_cities")

    # Explicit Index on city_uuid to improve join performance
    __table_args__ = (
        Index('idx_alliedcity_city_uuid', 'city_uuid'),
        Index('idx_alliedcity_ally_uuid', 'ally_uuid'),
    )
