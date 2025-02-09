"""Module that implements controller logic for routers."""

import uuid
from dataclasses import asdict
from typing import List

import psycopg2.extras

from app.city_api import utils
from app.common import constants
from app.models_.connections import PgDatabase
from app.models_.schemas import (
    CitySchema,
    CitySchemaWithAllyForce,
    CreateCitySchema,
    UpdateCitySchema,
)

psycopg2.extras.register_uuid()


class CityAppController(utils.CityAppUtils):
    """Class that contains controllers to do actions over the databases."""

    def perform_insert_city(self, payload: CreateCitySchema) -> CitySchema:
        """Insert a city object into the database."""

        perform_insert_city_sql_query = self.build_insert_city_query(
            constants.CITY_TABLE_NAME)

        with PgDatabase() as db:
            db.cursor.execute(
                perform_insert_city_sql_query, (
                    payload.name,
                    payload.beauty,
                    payload.population,
                    payload.geo_location_latitude,
                    payload.geo_location_longitude))

            db.connection.commit()
            commited_city_uuid = db.cursor.fetchone()[0]

        if payload.allied_cities is not None:
            self.perform_update_allies(
                commited_city_uuid, payload.allied_cities)
            self.update_current_allied_city_uuids(
                commited_city_uuid, payload.allied_cities)

        commited_city = self.peform_retrieve_city_by_id(commited_city_uuid)

        return commited_city

    def peform_retrieve_city_by_id_with_ally_power(
            self, city_uuid: uuid.UUID) -> CitySchemaWithAllyForce:
        """Perform retrieve of a city adding ally power extra parameter."""

        city_object = self.peform_retrieve_city_by_id(city_uuid)

        allied_power = self.calculate_allied_force(
            city_object.geo_location_latitude,
            city_object.geo_location_longitude,
            city_object.allied_cities
        )
        allied_power = city_object.population + allied_power

        city_object = city_object.to_dict()
        city_object.update({'allied_power': allied_power})

        return CitySchemaWithAllyForce(**city_object)

    def perform_retrieve_cities(self) -> List[CitySchema]:
        """Preform retrieve of all cities from the database."""

        retrieve_cities_sql_query = self.build_retrieve_cities_query(
            constants.CITY_TABLE_NAME)

        with PgDatabase() as db:
            db.cursor.execute(retrieve_cities_sql_query)
            cities = [
                CitySchema(**{
                    "city_uuid": result[0],
                    "name": result[1],
                    "beauty": result[2],
                    "population": result[3],
                    "geo_location_latitude": result[4],
                    "geo_location_longitude": result[5],
                    "allied_cities": result[6]})
                for result in db.cursor.fetchall()
            ]

        return cities

    def perform_delete_city_by_id(self, city_uuid: uuid.UUID):
        """Delete an specific city by id."""

        allied_cities = self.select_allied_cities(city_uuid)
        self.perform_remove_alliances(city_uuid, allied_cities)
        self.update_current_allied_city_uuids(city_uuid, allied_cities)

        delete_city_by_id_sql_query = self.build_delete_city_by_id_query(
            constants.CITY_TABLE_NAME)

        with PgDatabase() as db:
            db.cursor.execute(delete_city_by_id_sql_query, (city_uuid,))
            db.connection.commit()
            res = db.cursor.statusmessage

        if res == "DELETE 1":
            return True

        return False

    def perform_delete_alliance_by_id(
            self, first_city_uuid: uuid.UUID,
            second_city_uuid: uuid.UUID) -> bool:
        """Perform sql delete query to city by uuid."""

        delete_alliance_sql_query = self.build_delete_alliance_query(
            constants.ALLY_TABLE_NAME)

        with PgDatabase() as db:
            db.cursor.execute(
                delete_alliance_sql_query, (
                    first_city_uuid, second_city_uuid,
                )
            )

            db.connection.commit()
            result = db.cursor.statusmessage

        if result == "DELETE 1":
            return True

        return False

    def perform_update_city_by_id_query(
            self, city_uuid: uuid.UUID,
            payload: UpdateCitySchema) -> CitySchema:
        """Peform sql update query into the database."""

        values_to_update = [
            (key, value) for key, value in asdict(payload).items() if (
                value is not None and key != "allied_cities")]

        if not values_to_update:
            return city_uuid

        with PgDatabase() as db:
            db.cursor.execute(
                self.build_update_by_id_query(
                    constants.CITY_TABLE_NAME, values_to_update),
                [item[1] for item in values_to_update] + [city_uuid]
            )
            db.connection.commit()
            result = db.cursor.fetchone()

            if not result:
                return None

        commited_city_uuid = result[0]

        return commited_city_uuid

    def perform_remove_alliances(
            self, city_uuid: uuid.UUID,
            allied_cities: List[uuid.UUID]) -> None:
        """Performs Drop of all alliances."""

        if allied_cities:
            for ally_uuid in allied_cities:
                self.perform_delete_alliance_by_id(city_uuid, ally_uuid)
                self.perform_delete_alliance_by_id(ally_uuid, city_uuid)

    def perform_update_city_by_id(
            self, city_uuid: uuid.UUID,
            payload: UpdateCitySchema) -> CitySchema:
        """Update an specific city by uuid."""

        original_allied_cities = self.select_allied_cities(city_uuid)

        commited_city_uuid = self.perform_update_city_by_id_query(
            city_uuid, payload)

        current_alliances_alliances = self.select_allied_cities(city_uuid)
        if current_alliances_alliances:
            self.perform_remove_alliances(city_uuid, current_alliances_alliances)

        if payload.allied_cities is not None:
            self.perform_update_allies(
                commited_city_uuid, payload.allied_cities)
            self.update_current_allied_city_uuids(
                commited_city_uuid, original_allied_cities)

        commited_city = self.peform_retrieve_city_by_id(commited_city_uuid)

        return commited_city
