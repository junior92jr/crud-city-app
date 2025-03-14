def test_update_single_city(client) -> None:
    """Test update a city object from City App."""

    # Create the city
    response_city_a = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City A",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 12.432,
            "geo_location_longitude": 54.234,
        },
    )

    # Check that the city creation was successful
    assert response_city_a.status_code == 201

    loaded_response_city_a = response_city_a.json()
    city_a_uuid = loaded_response_city_a.get("city_uuid")

    # Ensure that the city UUID is in the response
    assert city_a_uuid is not None

    # Update the city
    response_city_a = client.put(
        f"api/v1/cities/{city_a_uuid}/",
        json={
            "name": "New Testing City A",
            "beauty": "Ugly",
            "population": 123,
            "geo_location_latitude": 5.32,
            "geo_location_longitude": 1.23,
        },
    )

    # Check the response for the updated city
    assert response_city_a.status_code == 200

    loaded_response_city_a = response_city_a.json()

    # Validate the response contains the expected keys
    assert "city_uuid" in loaded_response_city_a
    assert "name" in loaded_response_city_a
    assert "beauty" in loaded_response_city_a
    assert "population" in loaded_response_city_a
    assert "geo_location_latitude" in loaded_response_city_a
    assert "geo_location_longitude" in loaded_response_city_a
    assert "allied_cities" in loaded_response_city_a

    # Validate the city fields are updated correctly
    assert loaded_response_city_a.get("name") == "New Testing City A"
    assert loaded_response_city_a.get("beauty") == "Ugly"
    assert loaded_response_city_a.get("population") == 123
    assert float(loaded_response_city_a.get("geo_location_latitude")) == 5.32
    assert float(loaded_response_city_a.get("geo_location_longitude")) == 1.23
    assert loaded_response_city_a.get("allied_cities") == []


def test_update_city_with_allies_city(client) -> None:
    """Test update a city object from City App with alliances."""

    # Create City C
    response_city_c = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City C",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 12.432,
            "geo_location_longitude": 54.234,
        },
    )
    loaded_response_city_c = response_city_c.json()
    assert response_city_c.status_code == 201
    assert "city_uuid" in loaded_response_city_c

    city_c_uuid = loaded_response_city_c.get("city_uuid")

    # Create City B
    response_city_b = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City B",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 54.432,
            "geo_location_longitude": 43.234,
        },
    )
    loaded_response_city_b = response_city_b.json()
    assert response_city_b.status_code == 201
    assert "city_uuid" in loaded_response_city_b

    city_b_uuid = loaded_response_city_b.get("city_uuid")

    # Create City A with initial alliances
    response_city_a = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City A",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": -24.432,
            "geo_location_longitude": -43.234,
            "allied_cities": [city_b_uuid, city_c_uuid],
        },
    )
    loaded_response_city_a = response_city_a.json()
    assert response_city_a.status_code == 201
    assert "allied_cities" in loaded_response_city_a
    assert loaded_response_city_a.get("allied_cities") == [city_b_uuid, city_c_uuid]

    city_a_uuid = loaded_response_city_a.get("city_uuid")

    # Update City B's alliances (remove City A, keep City C)
    response_city_b = client.put(
        f"api/v1/cities/{city_b_uuid}", json={"allied_cities": [city_c_uuid]}
    )
    loaded_response_city_b = response_city_b.json()
    assert response_city_b.status_code == 200
    assert "city_uuid" in loaded_response_city_b

    # Verify City B has only City C as an ally
    response_city_b = client.get(f"api/v1/cities/{city_b_uuid}")
    loaded_response_city_b = response_city_b.json()
    assert response_city_b.status_code == 200
    assert loaded_response_city_b.get("allied_cities") == [city_c_uuid]

    response_city_b = client.get(f"api/v1/cities/{city_b_uuid}")
    loaded_response_city_b = response_city_b.json()
    assert response_city_b.status_code == 200

    response_city_a = client.get(f"api/v1/cities/{city_a_uuid}")
    loaded_response_city_a = response_city_a.json()
    assert response_city_a.status_code == 200

    response_city_c = client.get(f"api/v1/cities/{city_c_uuid}")
    loaded_response_city_c = response_city_c.json()
    assert response_city_c.status_code == 200

    assert loaded_response_city_b.get("allied_cities") == [city_c_uuid]
    assert loaded_response_city_a.get("allied_cities") == [city_c_uuid]
    assert loaded_response_city_c.get("allied_cities") == [city_a_uuid, city_b_uuid]
