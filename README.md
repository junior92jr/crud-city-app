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

## Build the API image

To build, test and run this API we'll be using `docker-compose`. As such, the first step
is to build the images defined in the `docker-compose.yml` file.

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
