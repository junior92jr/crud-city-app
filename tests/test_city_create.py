"""Module that implements unittest for Create actions in the city app."""

from tests.utils import (
    drop_test_tables,
    get_testing_client
)


def test_create_single_city() -> None:
    """Test create a city object from City App."""

    client = get_testing_client()

    response_city_a = client.post(
        "/city",
        json={
            "name": "Testing City A",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 12.432,
            "geo_location_longitude": 54.234
        }
    )

    loaded_response_city_a = response_city_a.json()

    assert response_city_a.status_code == 201

    assert "city_uuid" in loaded_response_city_a
    assert "name" in loaded_response_city_a
    assert "beauty" in loaded_response_city_a
    assert "population" in loaded_response_city_a
    assert "geo_location_latitude" in loaded_response_city_a
    assert "geo_location_longitude" in loaded_response_city_a
    assert "allied_cities" in loaded_response_city_a

    assert loaded_response_city_a.get("name") == "Testing City A"
    assert loaded_response_city_a.get("beauty") == "Average"
    assert loaded_response_city_a.get("population") == 52352
    assert loaded_response_city_a.get("geo_location_latitude") == 12.432
    assert loaded_response_city_a.get("geo_location_longitude") == 54.234
    assert loaded_response_city_a.get("allied_cities") == []

    drop_test_tables()


def test_create_city_with_allies_city() -> None:
    """Test create a city object from City App."""

    client = get_testing_client()

    response_city_a = client.post(
        "/city",
        json={
            "name": "Testing City A",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 12.432,
            "geo_location_longitude": 54.234
        }
    )

    loaded_response_city_a = response_city_a.json()

    assert response_city_a.status_code == 201
    assert "city_uuid" in loaded_response_city_a

    city_a_uuid = loaded_response_city_a.get("city_uuid")

    response_city_b = client.post(
        "/city",
        json={
            "name": "Testing City B",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 54.432,
            "geo_location_longitude": 43.234
        }
    )

    loaded_response_city_b = response_city_b.json()

    assert response_city_b.status_code == 201
    assert "city_uuid" in loaded_response_city_b

    city_b_uuid = loaded_response_city_b.get("city_uuid")

    response_city_c = client.post(
        "/city",
        json={
            "name": "Testing City C",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": -24.432,
            "geo_location_longitude": -43.234,
            "allied_cities": [city_a_uuid, city_b_uuid]
        }
    )

    loaded_response_city_c = response_city_c.json()

    assert response_city_c.status_code == 201
    assert "allied_cities" in loaded_response_city_c
    assert loaded_response_city_c.get(
        "allied_cities") == [city_a_uuid, city_b_uuid]

    drop_test_tables()


def test_invalid_uuid_create_city() -> None:
    """Test create a city object from City App."""

    client = get_testing_client()

    response_city = client.post(
        "/city",
        json={
            "name": "City",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 22.432,
            "geo_location_longitude": 55.234,
            "allied_cities": ["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
        }
    )

    loaded_response = response_city.json()

    expected_response = (
        "UUID(s) 3fa85f64-5717-4562-b3fc-2c963f66afa6 does not exists.")

    assert response_city.status_code == 400
    assert expected_response == loaded_response["detail"]


def test_invalid_create_city() -> None:
    """Test create a city object from City App."""

    client = get_testing_client()

    response_city = client.post(
        "/city",
        json={
            "name": "",
            "beauty": "sdas",
            "population": -52352,
            "geo_location_latitude": 212.432,
            "geo_location_longitude": 554.234
        }
    )

    loaded_response_city = response_city.json()
    expected_validation_msg = "Input should be 'Ugly', 'Average' or 'Gorgeous'"
    assert response_city.status_code == 422
    assert expected_validation_msg == loaded_response_city["detail"][0]["msg"]

    response_city = client.post(
        "/city",
        json={
            "name": "",
            "beauty": "Average",
            "population": -52352,
            "geo_location_latitude": 212.432,
            "geo_location_longitude": 554.234
        }
    )

    loaded_response_city = response_city.json()
    expected_validation_msg = (
        "Value error, Population cannot be a negative value.")
    assert response_city.status_code == 422
    assert expected_validation_msg == loaded_response_city["detail"][0]["msg"]

    response_city = client.post(
        "/city",
        json={
            "name": "",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 212.432,
            "geo_location_longitude": 554.234
        }
    )

    loaded_response_city = response_city.json()
    expected_validation_msg = (
        "Value error, City Name cannot be an empty string.")
    assert response_city.status_code == 422
    assert expected_validation_msg == loaded_response_city["detail"][0]["msg"]

    response_city = client.post(
        "/city",
        json={
            "name": "City Test",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 212.432,
            "geo_location_longitude": 554.234
        }
    )

    loaded_response_city = response_city.json()
    expected_validation_msg = (
        "Value error, Latitude needs to be in -90.0 - 90.0 range.")
    assert response_city.status_code == 422
    assert expected_validation_msg == loaded_response_city["detail"][0]["msg"]

    response_city = client.post(
        "/city",
        json={
            "name": "City Test",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 23.432,
            "geo_location_longitude": 554.234
        }
    )

    loaded_response_city = response_city.json()
    expected_validation_msg = (
        "Value error, Longitude needs to be in -180.0 - 180.0 range.")
    assert response_city.status_code == 422
    assert expected_validation_msg == loaded_response_city["detail"][0]["msg"]
