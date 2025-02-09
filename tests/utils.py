import os

from starlette.testclient import TestClient

from app.main import create_application
from app.models_.connections import PgDatabase
from app.common.constants import CITY_TABLE_NAME, ALLY_TABLE_NAME


def create_test_tables() -> None:
    """Create Test Database."""

    with PgDatabase(os.environ.get("DATABASE_TEST_URL")) as db:
        db.cursor.execute(f"""
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            SELECT uuid_generate_v4();

            DROP TYPE IF EXISTS "beaty_choice" CASCADE;

            CREATE TYPE beaty_choice AS ENUM ('Ugly', 'Average', 'Gorgeous');

            CREATE TABLE {CITY_TABLE_NAME} (
                city_uuid uuid DEFAULT uuid_generate_v4 () PRIMARY KEY,
                name VARCHAR(64) NOT NULL,
                beauty beaty_choice,
                population BIGINT NOT NULL,
                geo_location_latitude DOUBLE PRECISION NOT NULL,
                geo_location_longitude DOUBLE PRECISION NOT NULL,
                current_allied_city_uuids uuid[] DEFAULT array[]::uuid[]
            );

            CREATE TABLE {ALLY_TABLE_NAME} (
                city_uuid uuid NOT NULL,
                ally_uuid uuid NOT NULL,
                CONSTRAINT fk_city_uuid
                    FOREIGN KEY(city_uuid)
                        REFERENCES city(city_uuid)
            );
        """)

        db.connection.commit()


def drop_test_tables() -> None:
    """DROP Test Database."""

    with PgDatabase(os.environ.get("DATABASE_TEST_URL")) as db:
        db.cursor.execute(f"""
            DROP TABLE IF EXISTS {ALLY_TABLE_NAME} CASCADE;
            DROP TABLE IF EXISTS {CITY_TABLE_NAME} CASCADE;
        """)

        db.connection.commit()


def get_testing_client() -> TestClient:
    """Return Test Client for Fast Api."""

    drop_test_tables()
    create_test_tables()
    os.environ["DATABASE_URL"] = os.getenv("DATABASE_TEST_URL")
    app = create_application()
    client = TestClient(app)

    return client
