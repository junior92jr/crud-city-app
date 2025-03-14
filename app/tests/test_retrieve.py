from uuid import UUID


def test_retrieve_single_city(client) -> None:
    """Test retrieve a city object from City App."""

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
    response_city_a.raise_for_status()  # Ensure 201 Created

    loaded_response_city_a = response_city_a.json()
    city_a_uuid = loaded_response_city_a.get("city_uuid")

    assert response_city_a.status_code == 201
    assert city_a_uuid is not None
    assert isinstance(UUID(city_a_uuid), UUID)  # Ensure it's a valid UUID

    response_city_a = client.get(f"api/v1/cities/{city_a_uuid}")
    response_city_a.raise_for_status()  # Ensure 200 OK
    loaded_response_city_a = response_city_a.json()

    assert response_city_a.status_code == 200

    expected_keys = {
        "city_uuid",
        "name",
        "beauty",
        "population",
        "geo_location_latitude",
        "geo_location_longitude",
        "allied_cities",
        "allied_power",
    }
    assert set(loaded_response_city_a.keys()) == expected_keys

    assert loaded_response_city_a.get("name") == "Testing City A"
    assert loaded_response_city_a.get("beauty") == "Average"
    assert loaded_response_city_a.get("population") == 52352
    assert loaded_response_city_a.get("geo_location_latitude") == "12.432000"
    assert loaded_response_city_a.get("geo_location_longitude") == "54.234000"
    assert loaded_response_city_a.get("allied_cities") == []
    assert loaded_response_city_a.get("allied_power") == 52352


def test_retrieve_single_city_with_allies(client) -> None:
    """Test retrieve a city object from City App."""

    response_city_a = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City A",
            "beauty": "Average",
            "population": 1841000,
            "geo_location_latitude": 53.551086,
            "geo_location_longitude": 9.993682,
        },
    )

    loaded_response_city_a = response_city_a.json()

    assert response_city_a.status_code == 201
    assert "city_uuid" in loaded_response_city_a

    city_a_uuid = loaded_response_city_a.get("city_uuid")

    response_city_b = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City B",
            "beauty": "Average",
            "population": 6751000,
            "geo_location_latitude": 40.413793,
            "geo_location_longitude": -3.702895,
        },
    )

    loaded_response_city_b = response_city_b.json()

    assert response_city_b.status_code == 201
    assert "city_uuid" in loaded_response_city_b

    city_b_uuid = loaded_response_city_b.get("city_uuid")

    response_city_c = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City C",
            "beauty": "Average",
            "population": 959000,
            "geo_location_latitude": -16.408413,
            "geo_location_longitude": -71.537554,
        },
    )

    loaded_response_city_c = response_city_c.json()

    assert response_city_c.status_code == 201

    city_c_uuid = loaded_response_city_c.get("city_uuid")

    response_city_d = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City D",
            "beauty": "Average",
            "population": 753056,
            "geo_location_latitude": 50.110924,
            "geo_location_longitude": 8.682127,
            "allied_cities": [city_a_uuid, city_b_uuid, city_c_uuid],
        },
    )

    loaded_response_city_d = response_city_d.json()
    assert response_city_d.status_code == 201

    city_d_uuid = loaded_response_city_d.get("city_uuid")

    response_city_d = client.get(f"api/v1/cities/{city_d_uuid}")
    loaded_response_city_d = response_city_d.json()
    assert response_city_d.status_code == 200

    assert loaded_response_city_d.get("allied_power") == 6209306


def test_retrieve_all_cities(client) -> None:
    """Test create a city object from City App."""

    response_city_a = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City A",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 5.432,
            "geo_location_longitude": 6.234,
        },
    )

    response_city_b = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City B",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 3.432,
            "geo_location_longitude": 4.234,
        },
    )

    response_city_c = client.post(
        "api/v1/cities",
        json={
            "name": "Testing City C",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 1.432,
            "geo_location_longitude": 2.234,
        },
    )

    assert response_city_a.status_code == 201
    assert response_city_b.status_code == 201
    assert response_city_c.status_code == 201

    cities_response = client.get("api/v1/cities")

    loaded_cities_response = cities_response.json()

    assert len(loaded_cities_response) == 3
