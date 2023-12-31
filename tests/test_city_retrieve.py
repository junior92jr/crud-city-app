"""Module that implements unittest for Retrieve actions in the city app."""

from tests.utils import (
    drop_test_tables,
    get_testing_client
)


def test_retrieve_single_city() -> None:
    """Test retrieve a city object from City App."""

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
    city_a_uuid = loaded_response_city_a.get("city_uuid")
    assert response_city_a.status_code == 201

    response_city_a = client.get(f"/city/{city_a_uuid}")
    loaded_response_city_a = response_city_a.json()
    assert response_city_a.status_code == 200

    assert "city_uuid" in loaded_response_city_a
    assert "name" in loaded_response_city_a
    assert "beauty" in loaded_response_city_a
    assert "population" in loaded_response_city_a
    assert "geo_location_latitude" in loaded_response_city_a
    assert "geo_location_longitude" in loaded_response_city_a
    assert "allied_cities" in loaded_response_city_a
    assert "allied_power" in loaded_response_city_a

    assert loaded_response_city_a.get("name") == "Testing City A"
    assert loaded_response_city_a.get("beauty") == "Average"
    assert loaded_response_city_a.get("population") == 52352
    assert loaded_response_city_a.get("geo_location_latitude") == 12.432
    assert loaded_response_city_a.get("geo_location_longitude") == 54.234
    assert loaded_response_city_a.get("allied_cities") == []
    assert loaded_response_city_a.get("allied_power") == 52352

    drop_test_tables()


def test_retrieve_all_cities() -> None:
    """Test create a city object from City App."""

    client = get_testing_client()

    response_city_a = client.post(
        "/city",
        json={
            "name": "Testing City A",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 5.432,
            "geo_location_longitude": 6.234
        }
    )

    response_city_b = client.post(
        "/city",
        json={
            "name": "Testing City B",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 3.432,
            "geo_location_longitude": 4.234
        }
    )

    response_city_c = client.post(
        "/city",
        json={
            "name": "Testing City C",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 1.432,
            "geo_location_longitude": 2.234
        }
    )

    assert response_city_a.status_code == 201
    assert response_city_b.status_code == 201
    assert response_city_c.status_code == 201

    cities_response = client.get("/city")

    loaded_cities_response = cities_response.json()

    assert len(loaded_cities_response) == 3

    drop_test_tables()
