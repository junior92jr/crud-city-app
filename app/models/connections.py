"""Module providing function to connect to a database."""
import os

import psycopg2


class PgDatabase:
    """PostgreSQL Database context manager."""

    def __init__(self, psql_url=None) -> None:
        self.driver = psycopg2
        self.connection = None
        self.cursor = None
        self.predefined_psql_url = psql_url

    def __enter__(self):
        self.connection = self.connect_to_database()
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exception_type, exc_val, traceback):
        self.cursor.close()
        self.connection.close()

    def connect_to_database(self):
        """Connects to a database."""

        if not self.predefined_psql_url:
            return self.driver.connect(os.environ.get("DATABASE_URL"))

        return self.driver.connect(self.predefined_psql_url)
