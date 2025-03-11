from typing import List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.cities.exceptions import DatabaseOperationException, InvalidAllyException
from app.cities.models import City
from app.cities.schemas import CityCreate, CityInDB, CityUpdate


class CityService:
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

                return CityInDB(
                    city_uuid=city_uuid,
                    name=city_data.name,
                    beauty=city_data.beauty,
                    population=city_data.population,
                    geo_location_latitude=city_data.geo_location_latitude,
                    geo_location_longitude=city_data.geo_location_longitude,
                    allied_cities=city_data.allied_cities or [],
                )

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Transaction failed: {e}")

    def _insert_city(self, city_data: CityCreate) -> str:
        """Insert the city into the database and return the generated UUID."""
        result = self.db.execute(
            text(
                """
            INSERT INTO city (
                name, beauty, population, geo_location_latitude, geo_location_longitude
            ) 
            VALUES (
                :name, :beauty, :population, :geo_location_latitude, :geo_location_longitude
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
            {"ally_uuids": tuple(ally_uuids)},
        )

        existing_ally_uuids = {str(row.city_uuid) for row in result.fetchall()}
        missing_allies = set(ally_uuids) - existing_ally_uuids

        if missing_allies:
            raise InvalidAllyException(list(missing_allies))

    def _insert_allied_cities(self, city_uuid: str, ally_uuids: List[str]) -> None:
        """Insert the allied cities into the allied_city table."""
        self.db.execute(
            text(
                """
            INSERT INTO allied_city (city_uuid, ally_uuid)
            SELECT :city_uuid, ally_uuid FROM unnest(:allied_cities) AS ally_uuid
            UNION ALL
            INSERT INTO allied_city (city_uuid, ally_uuid)
            SELECT ally_uuid, :city_uuid FROM unnest(:allied_cities) AS ally_uuid
            ON CONFLICT (city_uuid, ally_uuid) DO NOTHING;
        """
            ),
            {"city_uuid": city_uuid, "allied_cities": ally_uuids},
        )


def create_city(db: Session, city: CityCreate) -> CityInDB:
    """Create a new city with optional allied cities, ensuring atomicity."""
    try:
        result = db.execute(
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
                "name": city.name,
                "beauty": city.beauty,
                "population": city.population,
                "geo_location_latitude": city.geo_location_latitude,
                "geo_location_longitude": city.geo_location_longitude,
            },
        )

        created_city_uuid = result.scalar()

        if created_city_uuid is None:
            raise Exception("Failed to create city or retrieve UUID.")

        # Now check if all allied cities exist in the 'city' table
        if city.allied_cities:
            ally_uuids = [str(uuid) for uuid in city.allied_cities]

            # Query the city table to check if all allies exist
            result = db.execute(
                text(
                    """
                SELECT city_uuid FROM city WHERE city_uuid IN :ally_uuids
            """
                ),
                {"ally_uuids": tuple(ally_uuids)},
            )

            existing_ally_uuids = {str(row.city_uuid) for row in result.fetchall()}
            missing_allies = set(ally_uuids) - existing_ally_uuids

            if missing_allies:
                raise InvalidAllyException(missing_allies)

            # Insert the alliances if all allies are valid
            db.execute(
                text(
                    """
                INSERT INTO allied_city (city_uuid, ally_uuid)
                SELECT :city_uuid, ally_uuid FROM unnest(:allied_cities) AS ally_uuid
                ON CONFLICT (city_uuid, ally_uuid) DO NOTHING;

                INSERT INTO allied_city (city_uuid, ally_uuid)
                SELECT ally_uuid, :city_uuid FROM unnest(:allied_cities) AS ally_uuid
                ON CONFLICT (city_uuid, ally_uuid) DO NOTHING;
            """
                ),
                {"city_uuid": str(created_city_uuid), "allied_cities": ally_uuids},
            )

        # Return the created city data as response
        return CityInDB(
            city_uuid=created_city_uuid,
            name=city.name,
            beauty=city.beauty,
            population=city.population,
            geo_location_latitude=city.geo_location_latitude,
            geo_location_longitude=city.geo_location_longitude,
            allied_cities=city.allied_cities or [],
        )

    except InvalidAllyException as e:
        db.rollback()  # Rollback if there is an invalid ally
        raise e  # Raise the custom exception

    except Exception as e:
        db.rollback()  # Rollback in case of any other failure
        raise Exception(f"Transaction failed: {e}")


def get_cities(db: Session, skip: int = 0, limit: int = 100) -> List[CityInDB]:
    """Get cities with pagination using a single optimized SQL query."""
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

    result = db.execute(sql, {"limit": limit, "skip": skip})
    rows = result.fetchall()

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


def get_city(db: Session, city_uuid: UUID) -> Optional[CityInDB]:
    """Retrieve a city by its UUID, including its alliances."""
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
        WHERE c.city_uuid = :city_uuid
        GROUP BY c.city_uuid
    """
    )

    result = db.execute(sql, {"city_uuid": str(city_uuid)})
    row = result.fetchone()

    if not row:
        return None

    return CityInDB(
        city_uuid=row.city_uuid,
        name=row.name,
        beauty=row.beauty,
        population=row.population,
        geo_location_latitude=row.geo_location_latitude,
        geo_location_longitude=row.geo_location_longitude,
        allied_cities=row.allied_cities,
    )


def update_city(db: Session, city_uuid: UUID, city: CityUpdate) -> CityInDB:
    """Update a city's details and fully replace its alliances within a transaction."""

    try:
        with db.begin():  # This starts a transaction
            # Step 1: Retrieve existing city details
            existing_city = db.execute(
                text(
                    """
                    SELECT name, beauty, population, geo_location_latitude, geo_location_longitude 
                    FROM city WHERE city_uuid = :city_uuid
                """
                ),
                {"city_uuid": str(city_uuid)},
            ).fetchone()

            if not existing_city:
                raise Exception(f"City with UUID {city_uuid} does not exist.")

            existing_city_data = dict(
                zip(
                    [
                        "name",
                        "beauty",
                        "population",
                        "geo_location_latitude",
                        "geo_location_longitude",
                    ],
                    existing_city,
                )
            )

            # Step 2: Update city details
            sql_query = text(
                """
                UPDATE city
                SET 
                    name = :name,
                    beauty = :beauty,
                    population = :population,
                    geo_location_latitude = :geo_location_latitude,
                    geo_location_longitude = :geo_location_longitude
                WHERE city_uuid = :city_uuid
                RETURNING city_uuid;
            """
            )

            result = db.execute(
                sql_query,
                {
                    "city_uuid": city_uuid,
                    "name": (
                        city.name
                        if city.name is not None
                        else existing_city_data["name"]
                    ),
                    "beauty": (
                        city.beauty
                        if city.beauty is not None
                        else existing_city_data["beauty"]
                    ),
                    "population": (
                        city.population
                        if city.population is not None
                        else existing_city_data["population"]
                    ),
                    "geo_location_latitude": (
                        city.geo_location_latitude
                        if city.geo_location_latitude is not None
                        else existing_city_data["geo_location_latitude"]
                    ),
                    "geo_location_longitude": (
                        city.geo_location_longitude
                        if city.geo_location_longitude is not None
                        else existing_city_data["geo_location_longitude"]
                    ),
                },
            )

            updated_city_uuid = result.scalar()
            if updated_city_uuid is None:
                raise Exception("Failed to update the city.")

            # Step 3: Update alliances if provided
            if city.allied_cities is not None:
                db.execute(
                    text(
                        """
                    DELETE FROM allied_city
                    WHERE city_uuid = :city_uuid OR ally_uuid = :city_uuid;
                """
                    ),
                    {"city_uuid": str(city_uuid)},
                )

                if city.allied_cities:
                    db.execute(
                        text(
                            """
                        INSERT INTO allied_city (city_uuid, ally_uuid)
                        SELECT :city_uuid, ally_uuid::UUID FROM unnest(:allied_cities) AS ally_uuid(ally_uuid)
                        ON CONFLICT (city_uuid, ally_uuid) DO NOTHING;
                        
                        INSERT INTO allied_city (city_uuid, ally_uuid)
                        SELECT ally_uuid::UUID, :city_uuid FROM unnest(:allied_cities) AS ally_uuid(ally_uuid)
                        ON CONFLICT (city_uuid, ally_uuid) DO NOTHING;
                    """
                        ),
                        {
                            "city_uuid": str(city_uuid),
                            "allied_cities": [str(uuid) for uuid in city.allied_cities],
                        },
                    )

        # If all statements succeed, commit automatically (with db.begin())
        return CityInDB(
            city_uuid=updated_city_uuid,
            name=city.name if city.name is not None else existing_city_data["name"],
            beauty=(
                city.beauty if city.beauty is not None else existing_city_data["beauty"]
            ),
            population=(
                city.population
                if city.population is not None
                else existing_city_data["population"]
            ),
            geo_location_latitude=(
                city.geo_location_latitude
                if city.geo_location_latitude is not None
                else existing_city_data["geo_location_latitude"]
            ),
            geo_location_longitude=(
                city.geo_location_longitude
                if city.geo_location_longitude is not None
                else existing_city_data["geo_location_longitude"]
            ),
            allied_cities=city.allied_cities if city.allied_cities is not None else [],
        )

    except Exception as e:
        db.rollback()  # Ensure rollback in case of any failure
        raise Exception(f"Database error: {str(e)}")


def delete_city(db: Session, city_uuid: UUID) -> Optional[City]:
    """Delete a city and remove its alliances."""
    db_city = db.query(City).get(city_uuid)

    if not db_city:
        return None  # City not found

    try:
        # Remove the city from all alliances
        db.execute(
            text(
                """
            DELETE FROM allied_city
            WHERE city_uuid = :city_id OR ally_uuid = :city_id;
        """
            ),
            {"city_id": str(city_uuid)},
        )

        # Delete the city itself
        db.delete(db_city)

        db.commit()  # Commit the transaction
        return db_city  # Return deleted city info

    except Exception as e:
        db.rollback()  # Rollback in case of an error
        raise Exception(f"Failed to delete city: {str(e)}")
