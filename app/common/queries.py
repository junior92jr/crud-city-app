"""Module that implements utils sql functions."""
from typing import List

from psycopg2 import sql

from app.common import constants

CITY_IDENTIFIER = constants.CITY_IDENTIFIER
ALLY_IDENTIFIER = constants.ALLY_IDENTIFIER
CITY_ALLIED_UUIDS_IDENTIFIER = constants.CITY_ALLIED_UUIDS_IDENTIFIER
RETRIEVE_CITY_FIELDS = constants.RETRIEVE_CITY_FIELDS
INSERT_CITY_FIELDS = constants.INSERT_CITY_FIELDS
INSERT_ALLY_FIELDS = constants.INSERT_ALLY_FIELDS


class DeleteQueryCompositionMixin:
    """Class that implements SQL Composition for Delete."""

    def build_delete_alliance_query(self, table_name: str) -> sql.SQL:
        """Build SQL query to delete alliance between two cities."""

        return (
            sql.SQL("DELETE FROM {} WHERE {}=%s AND {}=%s").format(
                sql.Identifier(table_name),
                sql.Identifier(CITY_IDENTIFIER),
                sql.Identifier(ALLY_IDENTIFIER)
            )
        )

    def build_delete_city_by_id_query(self, table_name: str) -> sql.SQL:
        """Build SQL query to delete city by uuid."""

        return (
            sql.SQL("DELETE FROM {} WHERE {}=%s").format(
                sql.Identifier(table_name),
                sql.Identifier(CITY_IDENTIFIER)
            )
        )


class RetrieveQueryCompositionMixin:
    """Class that implements SQL Composition for Retrieve."""

    def build_retrieve_cities_query(self, table_name: str) -> sql.SQL:
        """Build SQL query to retrieve all cities."""

        return (
            sql.SQL("SELECT {} FROM {}").format(
                sql.SQL(', ').join(map(sql.Identifier, RETRIEVE_CITY_FIELDS)),
                sql.Identifier(table_name)
            )
        )

    def build_retrieve_city_by_id_query(self, table_name: str) -> sql.SQL:
        """Build SQL query to retrieve a city by id."""

        return (
            sql.SQL("SELECT {} FROM {} WHERE {}=%s").format(
                sql.SQL(', ').join(map(sql.Identifier, RETRIEVE_CITY_FIELDS)),
                sql.Identifier(table_name),
                sql.Identifier(CITY_IDENTIFIER)
            )
        )

    def build_retrieve_allies_query(self, table_name: str) -> sql.SQL:
        """Build SQL query to retrieve all allies from a city."""

        return (
            sql.SQL("SELECT {} FROM {} WHERE {}=%s").format(
                sql.Identifier(ALLY_IDENTIFIER),
                sql.Identifier(table_name),
                sql.Identifier(CITY_IDENTIFIER)
            )
        )


class InsertQueryCompositionMixin:
    """Class that implements SQL Composition for Insert."""

    def build_insert_city_query(self, table_name: str) -> sql.SQL:
        """Build SQL query to insert a city."""

        return (
            sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING {}").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, INSERT_CITY_FIELDS)),
                sql.SQL(', ').join(sql.Placeholder() * len(INSERT_CITY_FIELDS)),
                sql.Identifier(CITY_IDENTIFIER)
            )
        )

    def build_city_exists_query(self, table_name: str) -> sql.SQL:
        """Build SQL query to check if a city exists in the database."""

        return (
            sql.SQL("SELECT EXISTS(SELECT 1 from {} WHERE {}=%s)").format(
                sql.Identifier(table_name),
                sql.Identifier(CITY_IDENTIFIER)
            )
        )

    def build_city_exists_query_coordinates(self, table_name: str) -> sql.SQL:
        """Build SQL query to check if a city exists in the database."""

        return (
            sql.SQL(
                "SELECT EXISTS(SELECT 1 from {} WHERE {}=%s AND {}=%s)").format(
                sql.Identifier(table_name),
                sql.Identifier("geo_location_latitude"),
                sql.Identifier("geo_location_longitude"),
            )
        )


class UpdateQueryCompositionMixin:
    """Class that implements SQL Composition for Update."""

    def build_perform_update_allies_query(self, table_name: str) -> sql.SQL:
        """Build SQL query to update allies from a city."""

        return (
            sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, INSERT_ALLY_FIELDS)),
                sql.SQL(', ').join(sql.Placeholder() * len(INSERT_ALLY_FIELDS))
            )
        )

    def build_update_by_id_query(
            self, table_name: str, values_to_update: List[tuple]) -> sql.SQL:
        """Build SQL query to update by uuid."""

        sql_update_query_structure = (
            "UPDATE {} SET ({}) = ({}) WHERE {}=%s RETURNING {}") if len(
                values_to_update) > 1 else (
                    "UPDATE {} SET {} = {} WHERE {}=%s RETURNING {}")

        return (
            sql.SQL(sql_update_query_structure).format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(
                    sql.Identifier, [item[0] for item in values_to_update])),
                sql.SQL(', ').join(sql.Placeholder() * len(values_to_update)),
                sql.Identifier(CITY_IDENTIFIER),
                sql.Identifier(CITY_IDENTIFIER)
            )
        )

    def build_update_current_allies_query(self, table_name: str) -> sql.SQL:
        """Build SQL query to update array fields."""

        return (
            sql.SQL("UPDATE {} SET {} = %s WHERE {}=%s").format(
                sql.Identifier(table_name),
                sql.Identifier(CITY_ALLIED_UUIDS_IDENTIFIER),
                sql.Identifier(CITY_IDENTIFIER)
            )
        )


class QueryCompositionMixin(RetrieveQueryCompositionMixin,
                            DeleteQueryCompositionMixin,
                            InsertQueryCompositionMixin,
                            UpdateQueryCompositionMixin):
    """Class that implements SQL Composition for CRUD."""
