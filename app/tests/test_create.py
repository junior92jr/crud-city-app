import pytest


def test_create_single_city(client) -> None:
    """Test create a city object from City App."""

    # Expected city data
    city_data = {
        "name": "Testing City A",
        "beauty": "Average",
        "population": 52352,
        "geo_location_latitude": 12.432,
        "geo_location_longitude": 54.234,
    }

    # Send POST request to create a city
    response_city_a = client.post("api/v1/cities", json=city_data)

    # Load the response JSON
    loaded_response_city_a = response_city_a.json()

    print("/////////////////////")
    print(loaded_response_city_a)
    print("/////////////////////")

    # Assert the status code is 201
    assert response_city_a.status_code == 201

    # Assert the response contains the correct fields
    expected_fields = [
        "city_uuid",
        "name",
        "beauty",
        "population",
        "geo_location_latitude",
        "geo_location_longitude",
        "allied_cities",
    ]
    for field in expected_fields:
        assert field in loaded_response_city_a

    # Assert the returned data matches the input data
    assert loaded_response_city_a["name"] == city_data["name"]
    assert loaded_response_city_a["beauty"] == city_data["beauty"]
    assert loaded_response_city_a["population"] == city_data["population"]

    # Ensure geo-location values are returned as floats
    assert (
        float(loaded_response_city_a["geo_location_latitude"])
        == city_data["geo_location_latitude"]
    )
    assert (
        float(loaded_response_city_a["geo_location_longitude"])
        == city_data["geo_location_longitude"]
    )

    # Assert that the allied_cities field is an empty list (as expected)
    assert loaded_response_city_a["allied_cities"] == []


def test_create_city_with_allies_city(client) -> None:
    """Test create a city object with allied cities."""

    # Helper function to create a city
    def create_city(city_data: dict) -> dict:
        response = client.post("api/v1/cities", json=city_data)
        assert response.status_code == 201
        loaded_response = response.json()
        assert "city_uuid" in loaded_response
        return loaded_response

    # Create two cities for allies
    city_a_data = {
        "name": "Testing City A",
        "beauty": "Average",
        "population": 52352,
        "geo_location_latitude": 12.432,
        "geo_location_longitude": 54.234,
    }
    city_b_data = {
        "name": "Testing City B",
        "beauty": "Average",
        "population": 52352,
        "geo_location_latitude": 54.432,
        "geo_location_longitude": 43.234,
    }

    city_a = create_city(city_a_data)
    city_b = create_city(city_b_data)

    # Create the third city with allied cities
    city_c_data = {
        "name": "Testing City C",
        "beauty": "Average",
        "population": 52352,
        "geo_location_latitude": -24.432,
        "geo_location_longitude": -43.234,
        "allied_cities": [city_a["city_uuid"], city_b["city_uuid"]],
    }

    city_c = create_city(city_c_data)

    # Assert that the city C has the correct allied cities
    assert city_c.get("allied_cities") == [city_a["city_uuid"], city_b["city_uuid"]]


def test_invalid_uuid_create_city(client) -> None:
    """Test creating a city object with invalid allied city UUIDs."""

    invalid_ally_uuid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"  # Non-existing UUID

    # Attempt to create a city with an invalid allied city UUID
    response_city = client.post(
        "api/v1/cities",
        json={
            "name": "City",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 22.432,
            "geo_location_longitude": 55.234,
            "allied_cities": [invalid_ally_uuid],  # Invalid UUID
        },
    )

    loaded_response = response_city.json()

    # Check if the response status code is 400 (Bad Request)
    assert response_city.status_code == 400

    # Validate that the error message matches the expected format
    assert loaded_response["detail"] == f"Invalid ally UUIDs: {invalid_ally_uuid}"


@pytest.mark.parametrize(
    "city_data, expected_status_code",
    [
        # Invalid data cases (empty name)
        (
            {
                "name": "",
                "beauty": "sdas",
                "population": -52352,
                "geo_location_latitude": 212.432,
                "geo_location_longitude": 554.234,
            },
            422,
        ),
        (
            {
                "name": "",
                "beauty": "Average",
                "population": -52352,
                "geo_location_latitude": 212.432,
                "geo_location_longitude": 554.234,
            },
            422,
        ),
        (
            {
                "name": "",
                "beauty": "Average",
                "population": 52352,
                "geo_location_latitude": 212.432,
                "geo_location_longitude": 554.234,
            },
            422,
        ),
        # Invalid data (lat/long out of range)
        (
            {
                "name": "City Test",
                "beauty": "Average",
                "population": 52352,
                "geo_location_latitude": 212.432,
                "geo_location_longitude": 554.234,
            },
            422,
        ),
        # Valid data with missing latitude
        (
            {
                "name": "City Test",
                "beauty": "Average",
                "population": 52352,
                "geo_location_latitude": 23.432,
                "geo_location_longitude": 554.234,
            },
            422,
        ),
    ],
)
def test_invalid_create_city(client, city_data, expected_status_code):
    """Test create a city object from City App with invalid input."""

    response_city = client.post("api/v1/cities", json=city_data)

    assert response_city.status_code == expected_status_code
