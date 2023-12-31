CREATE DATABASE web_dev;
CREATE DATABASE web_test;

\c web_dev

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SELECT uuid_generate_v4();

DROP TYPE IF EXISTS "beaty_choice";

CREATE TYPE beaty_choice AS ENUM ('Ugly', 'Average', 'Gorgeous');

CREATE TABLE city (
    city_uuid uuid DEFAULT uuid_generate_v4 () PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    beauty beaty_choice,
    population BIGINT NOT NULL,
    geo_location_latitude DOUBLE PRECISION NOT NULL,
    geo_location_longitude DOUBLE PRECISION NOT NULL,
    current_allied_city_uuids uuid[] DEFAULT array[]::uuid[]
);

CREATE TABLE allied_city(
    city_uuid uuid NOT NULL,
    ally_uuid uuid NOT NULL,
    CONSTRAINT fk_city_uuid
        FOREIGN KEY(city_uuid) 
            REFERENCES city(city_uuid)
);
