# City App RESTful API

This project implements a Dockerized RESTful API in Python using FastAPI. The API provides CRUD functionality to manage a collection of City objects, which include information such as city names, populations, geographical coordinates, and relationships with allied cities.

## Task Overview

The task is to design and implement a RESTful API that provides **Create**, **Read**, **Update**, and **Delete** **(CRUD)** operations for a defined object type. The object type is City, and the API allows for:

* Storing and retrieving city data.
* Ensuring data validation for city attributes.
* Defining relationships between cities through an `allied cities` concept.

## API Endpoints
This API includes the following routes:

| **Endpoint**            | **HTTP method**   | **CRUD method**   | **Description**       |
|-------------------------|----------------   |---------------    |---------------------- |
| `/api/v1/cities`        | GET               | READ              | get all cities        |
| `/api/v1/cities/<id>`   | GET               | READ              | get city by id        |
| `/api/v1/cities`        | POST              | INSERT            | add a new city        |
| `/api/v1/cities<id>`    | DELETE            | DELETE            | delete city by id     |
| `/api/v1/cities/<id>`   | PUT               | UPDATE            | update city by id     |

## API Validation Rules
The API includes validation checks to ensure data integrity:

* **City UUID**: Must be a valid UUID and must exist in the system for updates or deletion.
* **Population**: Must not be negative.
* **City Name**: Cannot be an empty string.
* **Latitude**: Must be between -90.0 and 90.0.
* **Longitude**: Must be between -180.0 and 180.0.
* **Allied Cities**: The UUIDs in the `allied cities` list must exist in the database.

## Examples of API Usage

**Creating a City:**
  ```bash
    curl -X 'POST' \
      'http://localhost:1337/api/v1/cities/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "name": "Berlin",
      "beauty": "Average",
      "population": 3645000,
      "geo_location_latitude": 52.531677,
      "geo_location_longitude": 13.381777
    }'
  ```

**Add Allies to a City:**
  ```bash
    curl -X 'POST' \
      'http://localhost:1337/api/v1/cities/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "name": "Hamburg",
      "beauty": "Gorgeous",
      "population": 1841000,
      "geo_location_latitude": 53.551086,
      "geo_location_longitude": 9.993682,
      "allied_cities": ["ba969e34-1976-433c-8601-d157a2c23c5a", "d6b89760-f390-4f34-bee6-3b814d0b8822"]
    }'
  ```

**Get All Cities:**
  ```bash
  curl -X 'GET' \
    'http://localhost:1337/api/v1/cities/' \
    -H 'accept: application/json'
  ```

**Get City by UUID:**
  ```bash
    curl -X 'GET' \
    'http://localhost:1337/api/v1/cities/fab86ce5-3ff9-4128-8176-2ed55f2c21a9/' \
    -H 'accept: application/json'
  ```

**Update Allies for a City:**
  ```bash
    curl -X 'PUT' \
    'http://localhost:1337/api/v1/cities/d6b89760-f390-4f34-bee6-3b814d0b8822/' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "allied_cities": ["ba969e34-1976-433c-8601-d157a2c23c5a"]
  }'
  ```

## Architecture & Approach
1. **FastAPI for API**: The API is built using **FastAPI**, a modern web framework for building APIs with Python. FastAPI ensures high performance, automatic validation, and easy integration with Swagger UI for testing the endpoints.

2. **PostgreSQL for Data Storage**: The cities and their relationships (allied cities) are stored in a **PostgreSQL** database, with data model constraints ensuring valid and consistent data.

3. **UUID-based Identification**: Each city is uniquely identified by a **UUID**, which allows for easy querying and management of the cities.

4. **Dockerized**: The entire application is containerized using **Docker** for easy deployment and scalability. The API and PostgreSQL database are managed with **Docker Compose**.

5. **Validation**: Input validation is enforced at the API level to ensure that invalid data (such as negative population or out-of-range coordinates) does not enter the database.


## Setup & Installation

### Clone the repository

To clone the repository by SHH

```bash
$ git clone git@github.com:junior92jr/crud-city-app.git
```

To clone the repository by HTTPS

```bash
$ git clone https://github.com/junior92jr/crud-city-app.git
```

### Build the API image

To build, test and run this API we'll be using `docker-compose`. As such, the first step
is to build the images defined in the `docker-compose.yml` file.

```bash
$ cd crud-city-app/
```

```bash
$ docker-compose build
```

This will build two images:

- `fastapi-tdd-docker_web` image with REST API.
- `fastapi-tdd-docker_web-db` image with Postgres database.

### Create Enviroment Variables

You will find a file called `.env_example`, rename it for `.env`


### Run the Containers
 
To run the containers previously built, execute the following:
 
```bash
$ docker-compose up -d
```

This will launch two services named `web` (the API) and `web-db` (the underlying 
database) in background. The `web` service will be running on port `1337` on localhost. 
Whereas the database will be exposed to the `web` service. To make sure the
app is running correctly open [http://localhost:1337](http://localhost:1337) in 
your web browser (and/or run `docker-compose logs -f` from the command line).

For using the swagger interface with example payloads open
in your web browser [http://localhost:1337/docs](http://localhost:1337/docs) 


### Create the Database

The database will be created by running the `create_db.sql` file that will be 
executed when the container is built:

```bash
$ docker-compose up -d --build
```

One can confirm that the database was properly created by accessing the database container
and starting a psql console.

```bash
$ docker-compose exec web-db psql -U postgres
```

Next, one can connect to the `web_dev` database and list all the tables:

```bash
# \c web_dev
# \dt
```

### Run the Tests

The tests can be executed with:

```bash
$ docker-compose exec web pytest
```

Or including a coverage check:

```bash
$ docker-compose exec web pytest --cov="."
```
