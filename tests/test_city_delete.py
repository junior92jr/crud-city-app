"""Module that implements unittest for Delete actions in the city app."""

from tests.utils import (
    drop_test_tables,
    get_testing_client
)


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

    city_c_uuid = loaded_response_city_c.get("city_uuid")

    response_city_c = client.delete(
        f"/city/{city_c_uuid}",
    )

    assert response_city_c.status_code == 204

    response_city_c = client.get(
        f"/city/{city_c_uuid}",
    )

    assert response_city_c.status_code == 404

    drop_test_tables()
