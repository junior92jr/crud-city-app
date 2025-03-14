"""Module that implements unittest for Update actions in the city app."""

from not_tests.utils import drop_test_tables, get_testing_client


def test_update_single_city() -> None:
    """Test update a city object from City App."""

    client = get_testing_client()

    response_city_a = client.post(
        "/city",
        json={
            "name": "Testing City A",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 12.432,
            "geo_location_longitude": 54.234,
        },
    )

    loaded_response_city_a = response_city_a.json()

    city_a_uuid = loaded_response_city_a.get("city_uuid")

    assert response_city_a.status_code == 201

    response_city_a = client.put(
        f"/city/{city_a_uuid}/",
        json={
            "name": "New Testing City A",
            "beauty": "Ugly",
            "population": 123,
            "geo_location_latitude": 5.32,
            "geo_location_longitude": 1.23,
        },
    )

    loaded_response_city_a = response_city_a.json()

    assert response_city_a.status_code == 200

    assert "city_uuid" in loaded_response_city_a
    assert "name" in loaded_response_city_a
    assert "beauty" in loaded_response_city_a
    assert "population" in loaded_response_city_a
    assert "geo_location_latitude" in loaded_response_city_a
    assert "geo_location_longitude" in loaded_response_city_a
    assert "allied_cities" in loaded_response_city_a

    assert loaded_response_city_a.get("name") == "New Testing City A"
    assert loaded_response_city_a.get("beauty") == "Ugly"
    assert loaded_response_city_a.get("population") == 123
    assert loaded_response_city_a.get("geo_location_latitude") == 5.32
    assert loaded_response_city_a.get("geo_location_longitude") == 1.23
    assert loaded_response_city_a.get("allied_cities") == []

    drop_test_tables()


def test_update_city_with_allies_city() -> None:
    """Test update a city object from City App."""

    client = get_testing_client()

    response_city_c = client.post(
        "/city",
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

    response_city_b = client.post(
        "/city",
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

    response_city_a = client.post(
        "/city",
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

    response_city_b = client.put(
        f"/city/{city_b_uuid}", json={"allied_cities": [city_c_uuid]}
    )

    loaded_response_city_b = response_city_b.json()

    assert response_city_b.status_code == 200
    assert "city_uuid" in loaded_response_city_b

    response_city_b = client.get(f"/city/{city_b_uuid}")
    loaded_response_city_b = response_city_b.json()
    assert response_city_b.status_code == 200

    response_city_a = client.get(f"/city/{city_a_uuid}")
    loaded_response_city_a = response_city_a.json()
    assert response_city_a.status_code == 200

    response_city_c = client.get(f"/city/{city_c_uuid}")
    loaded_response_city_c = response_city_c.json()
    assert response_city_c.status_code == 200

    assert loaded_response_city_b.get("allied_cities")[0] == city_c_uuid
    assert loaded_response_city_a.get("allied_cities")[0] == city_c_uuid
    assert loaded_response_city_c.get("allied_cities")[0] == city_a_uuid
    assert loaded_response_city_c.get("allied_cities")[1] == city_b_uuid

    drop_test_tables()


def test_invalid_uuid_update_city() -> None:
    """Test create a city object from City App."""

    client = get_testing_client()

    response_city_c = client.post(
        "/city",
        json={
            "name": "Testing City C",
            "beauty": "Average",
            "population": 52352,
            "geo_location_latitude": 12.432,
            "geo_location_longitude": 54.234,
        },
    )

    loaded_response_city_c = response_city_c.json()
    city_c_uuid = loaded_response_city_c.get("city_uuid")

    assert response_city_c.status_code == 201
    assert "city_uuid" in loaded_response_city_c

    response_city_c = client.put(
        f"/city/{city_c_uuid}", json={"allied_cities": [city_c_uuid]}
    )

    loaded_response_city_c = response_city_c.json()

    expected_response = f"UUID {city_c_uuid} in url cannot be used in the request."

    assert response_city_c.status_code == 400
    assert expected_response == loaded_response_city_c["detail"]

    response_city_c = client.put(
        f"/city/{city_c_uuid}",
        json={"allied_cities": ["3fa85f64-5717-4562-b3fc-2c963f66afa6"]},
    )

    loaded_response_city_c = response_city_c.json()

    expected_response = "UUID(s) 3fa85f64-5717-4562-b3fc-2c963f66afa6 does not exists."

    assert response_city_c.status_code == 400
    assert expected_response == loaded_response_city_c["detail"]

    fake_city_uuid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

    response_city_c = client.put(f"/city/{fake_city_uuid}", json={"population": 233})

    assert response_city_c.status_code == 404
    assert expected_response == loaded_response_city_c["detail"]


def test_invalid_update_city() -> None:
    """Test create a city object from City App."""

    client = get_testing_client()

    response_city = client.post(
        "/city",
        json={
            "name": "City",
            "beauty": "Average",
            "population": 2352,
            "geo_location_latitude": 12.432,
            "geo_location_longitude": 54.234,
        },
    )

    loaded_response_city = response_city.json()
    assert response_city.status_code == 201
    city_uuid = loaded_response_city.get("city_uuid")

    response_city = client.put(
        f"/city/{city_uuid}",
        json={
            "beauty": "Avedasdrage",
        },
    )

    loaded_response_city = response_city.json()
    expected_validation_msg = "Input should be 'Ugly', 'Average' or 'Gorgeous'"
    assert response_city.status_code == 422
    assert expected_validation_msg == loaded_response_city["detail"][0]["msg"]

    response_city = client.put(f"/city/{city_uuid}", json={"population": -52352})

    loaded_response_city = response_city.json()
    expected_validation_msg = "Value error, Population cannot be a negative value."
    assert response_city.status_code == 422
    assert expected_validation_msg == loaded_response_city["detail"][0]["msg"]

    response_city = client.put(f"/city/{city_uuid}", json={"name": ""})

    loaded_response_city = response_city.json()
    expected_validation_msg = "Value error, City Name cannot be an empty string."
    assert response_city.status_code == 422
    assert expected_validation_msg == loaded_response_city["detail"][0]["msg"]

    response_city = client.put(
        f"/city/{city_uuid}", json={"geo_location_latitude": 212.432}
    )

    loaded_response_city = response_city.json()
    expected_validation_msg = "Value error, Latitude needs to be in -90.0 - 90.0 range."
    assert response_city.status_code == 422
    assert expected_validation_msg == loaded_response_city["detail"][0]["msg"]

    response_city = client.put(
        f"/city/{city_uuid}", json={"geo_location_longitude": 554.234}
    )

    loaded_response_city = response_city.json()
    expected_validation_msg = (
        "Value error, Longitude needs to be in -180.0 - 180.0 range."
    )
    assert response_city.status_code == 422
    assert expected_validation_msg == loaded_response_city["detail"][0]["msg"]
