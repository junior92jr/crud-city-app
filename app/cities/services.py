from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import Session

from app.cities.exceptions import (
    CityNotFoundException,
    DatabaseOperationException,
    InvalidAllyException,
)
from app.cities.models import City
from app.cities.schemas import CityCreate, CityInDB, CityUpdate


class CityService:
    """Service class to handle city-related operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_city(self, city_data: CityCreate) -> CityInDB:
        """Create a new city with optional allied cities, ensuring atomicity."""
        try:
            with self.db.begin():
                city_uuid = self._insert_city(city_data)

                if city_data.allied_cities:
                    ally_uuids = [str(uuid) for uuid in city_data.allied_cities]
                    self._validate_allied_cities(ally_uuids)

                    self._insert_allied_cities(city_uuid, ally_uuids)

                self.db.commit()

            return CityInDB(
                city_uuid=city_uuid,
                name=city_data.name,
                beauty=city_data.beauty,
                population=city_data.population,
                geo_location_latitude=city_data.geo_location_latitude,
                geo_location_longitude=city_data.geo_location_longitude,
                allied_cities=city_data.allied_cities or [],
            )
        except InvalidAllyException as e:
            self.db.rollback()
            raise e

        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationException(f"Unexpected Error: {e}") from e

    def _insert_city(self, city_data: CityCreate) -> str:
        """Insert the city into the database and return the generated UUID."""
        result = self.db.execute(
            text(
                """
                INSERT INTO city (
                    city_uuid, name, beauty, population, geo_location_latitude, geo_location_longitude
                )
                VALUES (
                    gen_random_uuid(), :name, :beauty, :population, :geo_location_latitude, :geo_location_longitude
                )
                RETURNING city_uuid;
                """
            ),
            {
                "name": city_data.name,
                "beauty": city_data.beauty,
                "population": city_data.population,
                "geo_location_latitude": city_data.geo_location_latitude,
                "geo_location_longitude": city_data.geo_location_longitude,
            },
        )

        created_city_uuid = result.scalar()
        if created_city_uuid is None:
            raise DatabaseOperationException("Failed to create city or retrieve UUID.")
        return created_city_uuid

    def _validate_allied_cities(self, ally_uuids: List[str]) -> None:
        """Validate that all provided allies exist in the city table."""
        result = self.db.execute(
            text(
                """
                SELECT city_uuid FROM city WHERE city_uuid IN :ally_uuids
                """
            ),
            {
                "ally_uuids": tuple(ally_uuids),
            },
        )

        existing_ally_uuids = {str(row.city_uuid) for row in result.fetchall()}
        missing_allies = set(ally_uuids) - existing_ally_uuids

        if missing_allies:
            raise InvalidAllyException([UUID(ally) for ally in missing_allies])

    def _insert_allied_cities(self, city_uuid: str, ally_uuids: List[str]) -> None:
        """Bulk insert allied cities to optimize performance."""
        values = [{"city_uuid": city_uuid, "ally_uuid": ally} for ally in ally_uuids]
        values += [{"city_uuid": ally, "ally_uuid": city_uuid} for ally in ally_uuids]

        self.db.execute(
            text(
                """
                INSERT INTO allied_city (city_uuid, ally_uuid)
                VALUES (:city_uuid, :ally_uuid)
                ON CONFLICT (city_uuid, ally_uuid) DO NOTHING;
                """
            ),
            values,
        )

    def get_cities(self, skip: int = 0, limit: int = 100) -> List[CityInDB]:
        """Get cities with pagination."""
        rows = self._fetch_cities_data(skip, limit)
        return [
            CityInDB(
                city_uuid=row.city_uuid,
                name=row.name,
                beauty=row.beauty,
                population=row.population,
                geo_location_latitude=row.geo_location_latitude,
                geo_location_longitude=row.geo_location_longitude,
                allied_cities=row.allied_cities,
            )
            for row in rows
        ]

    def _fetch_cities_data(self, skip: int, limit: int) -> Sequence[Row]:
        """Fetch raw city data from the database."""
        sql = text(
            """
            SELECT 
                c.city_uuid,
                c.name,
                c.beauty,
                c.population,
                c.geo_location_latitude,
                c.geo_location_longitude,
                COALESCE(array_agg(ac.ally_uuid) FILTER (WHERE ac.ally_uuid IS NOT NULL), '{}') AS allied_cities
            FROM city c
            LEFT JOIN allied_city ac ON c.city_uuid = ac.city_uuid
            GROUP BY c.city_uuid
            ORDER BY c.name
            LIMIT :limit OFFSET :skip
            """
        )

        result = self.db.execute(sql, {"limit": limit, "skip": skip})
        return result.fetchall()

    def _fetch_city_by_uuid(self, city_uuid: UUID) -> CityInDB:
        """Fetch a city by its UUID from the database (raw row)."""

        result = self.db.execute(
            text(
                """
                SELECT 
                    c.city_uuid, 
                    c.name, 
                    c.beauty, 
                    c.population, 
                    c.geo_location_latitude, 
                    c.geo_location_longitude, 
                    COALESCE(array_agg(ac.ally_uuid) FILTER (WHERE ac.ally_uuid IS NOT NULL), '{}') AS allied_cities
                FROM city c
                LEFT JOIN allied_city ac ON c.city_uuid = ac.city_uuid
                WHERE c.city_uuid = :city_uuid
                GROUP BY c.city_uuid
                """
            ),
            {"city_uuid": str(city_uuid)},
        )
        row = result.fetchone()

        if not row:
            raise CityNotFoundException(city_uuid)

        return CityInDB(
            city_uuid=row.city_uuid,
            name=row.name,
            beauty=row.beauty,
            population=row.population,
            geo_location_latitude=row.geo_location_latitude,
            geo_location_longitude=row.geo_location_longitude,
            allied_cities=row.allied_cities,
        )

    def get_city(self, city_uuid: UUID) -> CityInDB:
        """Retrieve a city by its UUID, including its alliances."""

        try:
            return self._fetch_city_by_uuid(city_uuid)

        except CityNotFoundException as e:
            raise e from e
        except Exception as e:
            raise DatabaseOperationException(f"Unexpected Error: {e}") from e

    def update_city(self, city_uuid: str, city_data: CityUpdate) -> CityInDB:
        """Update a city's details and fully replace its alliances within a transaction."""
        try:
            with self.db.begin():
                existing_city = self._fetch_city_by_uuid(city_uuid)

                updated_city = self._update_city_fields(
                    city_uuid, city_data, existing_city
                )

                if city_data.allied_cities:
                    self._replace_city_alliances(city_uuid, city_data.allied_cities)

            return CityInDB(
                city_uuid=updated_city.city_uuid,
                name=updated_city.name,
                beauty=updated_city.beauty,
                population=updated_city.population,
                geo_location_latitude=updated_city.geo_location_latitude,
                geo_location_longitude=updated_city.geo_location_longitude,
                allied_cities=(
                    city_data.allied_cities if city_data.allied_cities else []
                ),
            )
        except CityNotFoundException as e:
            raise e
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationException(f"Database error: {str(e)}") from e

    def _update_city_fields(
        self, city_uuid: str, city_data: CityUpdate, existing_city: CityInDB
    ) -> Row:
        """Update city fields and return the updated city."""

        update_fields = {
            "name": (
                city_data.name if city_data.name is not None else existing_city.name
            ),
            "beauty": (
                city_data.beauty
                if city_data.beauty is not None
                else existing_city.beauty
            ),
            "population": (
                city_data.population
                if city_data.population is not None
                else existing_city.population
            ),
            "geo_location_latitude": (
                city_data.geo_location_latitude
                if city_data.geo_location_latitude is not None
                else existing_city.geo_location_latitude
            ),
            "geo_location_longitude": (
                city_data.geo_location_longitude
                if city_data.geo_location_longitude is not None
                else existing_city.geo_location_longitude
            ),
        }

        result = self.db.execute(
            text(
                """
            UPDATE city
            SET
                name = :name,
                beauty = :beauty,
                population = :population,
                geo_location_latitude = :geo_location_latitude,
                geo_location_longitude = :geo_location_longitude
            WHERE city_uuid = :city_uuid
            RETURNING city_uuid, name, beauty, population, geo_location_latitude, geo_location_longitude;
            """
            ),
            {"city_uuid": city_uuid, **update_fields},
        )

        updated_city = result.fetchone()
        if not updated_city:
            raise DatabaseOperationException(f"Failed to update city {city_uuid}.")

        return updated_city

    def _replace_city_alliances(
        self, city_uuid: str, allied_cities: Optional[list[str]]
    ):
        """Delete old alliances and insert new ones."""
        self._delete_alliances(city_uuid)

        if allied_cities:
            self._insert_allied_cities(city_uuid, allied_cities)

    def _delete_alliances(self, city_uuid: str):
        """Delete alliances for a given city."""
        self.db.execute(
            text(
                """
                DELETE FROM allied_city
                WHERE city_uuid = :city_id OR ally_uuid = :city_id;
                """
            ),
            {"city_id": city_uuid},
        )

    def delete_city(self, city_uuid: UUID) -> CityInDB:
        """Delete a city and remove its alliances."""

        try:
            with self.db.begin():
                city = self._fetch_city_by_uuid(city_uuid)
                self._delete_alliances(city_uuid)
                self._delete_city_record(city_uuid)

            return city

        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationException(f"Failed to delete city: {str(e)}") from e

    def _delete_city_record(self, city_uuid: UUID) -> None:
        """Execute SQL to delete a city from the database."""
        self.db.execute(
            text(
                """
                DELETE FROM city
                WHERE city_uuid = :city_uuid;
                """
            ),
            {"city_uuid": str(city_uuid)},
        )
