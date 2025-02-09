"""Module that implements Util queries for Controllers."""

import uuid
from typing import List

from app.common.utils import calculate_distance
from app.common import constants
from app.common.queries import QueryCompositionMixin
from app.models_.connections import PgDatabase
from app.models_.schemas import CitySchema


class CityAppUtils(QueryCompositionMixin):
    """Class that implements util queries from the database."""

    def peform_retrieve_city_by_id(self, city_uuid: uuid.UUID) -> CitySchema:
        """Perform sql retrieve of a city by uuid."""

        retrieve_city_by_id_query = self.build_retrieve_city_by_id_query(
            constants.CITY_TABLE_NAME)

        with PgDatabase() as db:
            db.cursor.execute(retrieve_city_by_id_query, (city_uuid,))
            result = db.cursor.fetchone()

            if result is None:
                return None

        return CitySchema(**{
            "city_uuid": result[0],
            "name": result[1],
            "beauty": result[2],
            "population": result[3],
            "geo_location_latitude": result[4],
            "geo_location_longitude": result[5],
            "allied_cities": result[6]
        })

    def city_exists_by_coordinates(
            self, latitude: float, longitude: float) -> bool:
        """Check if coordinates already exits."""

        check_city_exits_query = self.build_city_exists_query_coordinates(
            constants.CITY_TABLE_NAME)

        with PgDatabase() as db:
            db.cursor.execute(check_city_exits_query, (latitude, longitude))
            exists = db.cursor.fetchone()[0]

            if exists is None:
                return False

        return exists

    def city_exists(self, city_uuid: uuid.UUID) -> bool:
        """Check if a city exists in the database."""

        check_city_exits_query = self.build_city_exists_query(
            constants.CITY_TABLE_NAME)

        with PgDatabase() as db:
            db.cursor.execute(check_city_exits_query, (city_uuid,))
            exists = db.cursor.fetchone()[0]

            if exists is None:
                return False

        return exists

    def check_city_uuids_exists(self, city_uuid_list: List) -> List:
        """Check if the cities in a lists exists in the database."""

        if not city_uuid_list:
            return False

        return [
            c_uuid for c_uuid in city_uuid_list if not self.city_exists(c_uuid)
        ]

    def is_city_in_request(
            self, city_uuid: uuid.UUID, city_uuid_list: List) -> bool:
        """Check if main city uuid is passed in the body request."""

        if not city_uuid_list:
            return False

        return city_uuid in city_uuid_list

    def select_allied_cities(self, city_uuid: uuid.UUID) -> List[uuid.UUID]:
        """Select allied cities from the database."""

        retrieve_allies_sql_query = self.build_retrieve_allies_query(
            constants.ALLY_TABLE_NAME)

        with PgDatabase() as db:
            db.cursor.execute(retrieve_allies_sql_query, (city_uuid,))
            allied_cities = [item[0] for item in db.cursor.fetchall()]

        return allied_cities

    def perform_update_allies(
            self, city_uuid: uuid.UUID,
            allied_cities: List[uuid.UUID]) -> List[uuid.UUID]:
        """Update List with allies UUIDs."""

        perform_update_allies_query = self.build_perform_update_allies_query(
            constants.ALLY_TABLE_NAME)

        if allied_cities:
            with PgDatabase() as db:
                for ally_uuid in allied_cities:
                    db.cursor.execute(
                        perform_update_allies_query, (city_uuid, ally_uuid,))
                    db.cursor.execute(
                        perform_update_allies_query, (ally_uuid, city_uuid,))
                    db.connection.commit()

        return self.select_allied_cities(city_uuid)

    def update_current_allied_city_uuids(
            self, city_uuid: uuid.UUID,
            allied_cities: List[uuid.UUID]) -> None:
        """Update Current alliend city list."""

        current_allied_cities = self.select_allied_cities(city_uuid)

        if allied_cities:
            for ally in allied_cities:
                self.update_current_ally_uuids(
                    ally, self.select_allied_cities(ally))

        self.update_current_ally_uuids(city_uuid, current_allied_cities)

        for ally in current_allied_cities:
            self.update_current_ally_uuids(
                ally, self.select_allied_cities(ally))

    def update_current_ally_uuids(
            self, city_uuid: uuid.UUID,
            allied_cities: List[uuid.UUID]) -> None:
        """Perform SQL update for array field."""

        query_sql = self.build_update_current_allies_query(
            constants.CITY_TABLE_NAME)

        with PgDatabase() as db:
            db.cursor.execute(query_sql, (allied_cities, city_uuid))
            db.connection.commit()

    def calculate_allied_force(
            self, geo_location_latitude: float,
            geo_location_longitude: float,
            allied_cities: List[uuid.UUID]) -> int:
        """Calculates the total alliend power by distance in km."""

        allied_force = 0

        for ally in allied_cities:
            ally_object = self.peform_retrieve_city_by_id(ally)

            distance_in_km = calculate_distance(
                (
                    geo_location_latitude,
                    geo_location_longitude
                ),
                (
                    ally_object.geo_location_latitude,
                    ally_object.geo_location_longitude
                )
            )

            if 1000 <= distance_in_km < 10000:
                allied_force += int(ally_object.population / 2)
            elif distance_in_km >= 10000:
                allied_force += int(ally_object.population / 4)
            else:
                allied_force += ally_object.population

        return allied_force
