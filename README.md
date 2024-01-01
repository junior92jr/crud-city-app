# City APP

The project is to design and implement a dockerized RESTFUL API in python
that provides CRUD functionality for a defined object type as a
container.

## API Endpoints

This API implements the following routes:

| **Endpoint**      | **HTTP method**   | **CRUD method**   | **Description**       |
|-----------------  |----------------   |---------------    |---------------------- |
| `/city`           | GET               | READ              | get all cities        |
| `/city/<id>`      | GET               | READ              | get city by id        |
| `/city`           | POST              | INSERT            | add a new city        |
| `/city/<id>`      | DELETE            | DELETE            | delete city by id     |
| `/city/<id>`      | PUT               | UPDATE            | update city by id     |

## API Validations and Exceptions

Payloads needs to be valid input data

```bash
Input should be a valid UUID
```
```bash
Population cannot be a negative value.
```

```bash
City Name cannot be an empty string.
```

```bash
Latitude needs to be in -90.0 - 90.0 range.
```

```bash
Longitude needs to be in -180.0 - 180.0 range.
```

```bash
City UUID in the endpoint must exists.
```

```bash
City UUIDs in inside "allied_cities" must exists.
```

```bash
City name is not unique but coordinates are.
```

## API Examples

Creating a City

```bash
curl -X 'POST' \
  'http://localhost:1337/city/' \
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

After Creating other cities without allies we add two allies

```bash
  curl -X 'POST' \
  'http://localhost:1337/city/' \
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

Retrieve all cities

```bash
curl -X 'GET' \
  'http://localhost:1337/city/' \
  -H 'accept: application/json'

  [
    {
      "city_uuid": "fab86ce5-3ff9-4128-8176-2ed55f2c21a9",
      "name": "Hamburg",
      "beauty": "Gorgeous",
      "population": 1841000,
      "geo_location_latitude": 53.551086,
      "geo_location_longitude": 9.993682,
      "allied_cities": [
        "ba969e34-1976-433c-8601-d157a2c23c5a",
        "d6b89760-f390-4f34-bee6-3b814d0b8822"
      ]
    },
    {
      "city_uuid": "ba969e34-1976-433c-8601-d157a2c23c5a",
      "name": "Frankfurt am Main",
      "beauty": "Average",
      "population": 753056,
      "geo_location_latitude": 50.110924,
      "geo_location_longitude": 8.682127,
      "allied_cities": [
        "fab86ce5-3ff9-4128-8176-2ed55f2c21a9"
      ]
    },
    {
      "city_uuid": "d6b89760-f390-4f34-bee6-3b814d0b8822",
      "name": "Berlin",
      "beauty": "Average",
      "population": 3645000,
      "geo_location_latitude": 52.531677,
      "geo_location_longitude": 13.381777,
      "allied_cities": [
        "fab86ce5-3ff9-4128-8176-2ed55f2c21a9"
      ]
    }
  ]
```

Restrieve a city by uuid

```bash
  curl -X 'GET' \
  'http://localhost:1337/city/fab86ce5-3ff9-4128-8176-2ed55f2c21a9/' \
  -H 'accept: application/json'


  {
    "city_uuid": "fab86ce5-3ff9-4128-8176-2ed55f2c21a9",
    "name": "Hamburg",
    "beauty": "Gorgeous",
    "population": 1841000,
    "geo_location_latitude": 53.551086,
    "geo_location_longitude": 9.993682,
    "allied_cities": [
      "ba969e34-1976-433c-8601-d157a2c23c5a",
      "d6b89760-f390-4f34-bee6-3b814d0b8822"
    ],
    "allied_power": 6239056
  }
```

Update Allies

```bash
  curl -X 'PUT' \
  'http://localhost:1337/city/d6b89760-f390-4f34-bee6-3b814d0b8822/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "allied_cities": [
    "ba969e34-1976-433c-8601-d157a2c23c5a"
  ]
}'
```

## Clone the repository

To clone the repository by SHH

```bash
$ git clone git@github.com:junior92jr/crud-city-app.git
```

To clone the repository by HTTPS

```bash
$ git clone https://github.com/junior92jr/crud-city-app.git
```

## Build the API image

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

## Create Enviroment Variables

You will find a file called `.env_example`, rename it for `.env`


## Run the Containers
 
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


## Create the Database

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

## Run the Tests

The tests can be executed with:

```bash
$ docker-compose exec web pytest
```

Or including a coverage check:

```bash
$ docker-compose exec web pytest --cov="."
```
