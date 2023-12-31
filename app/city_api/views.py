"""Module that implements viewset logic."""

import uuid
from typing import List

from fastapi import APIRouter, status

from app.city_api.controllers import CityAppController
from app.city_api.exceptions import (
    InvalidCityUUIDException,
    NotFoundCityUUIDException,
    RepeatedCoordinatesException,
)
from app.models.schemas import (
    CitySchema,
    CitySchemaWithAllyForce,
    CreateCitySchema,
    UpdateCitySchema,
)

router = APIRouter()
controller = CityAppController()


@router.post(
    '/',
    response_model=CitySchema,
    status_code=status.HTTP_201_CREATED)
def create_city_view(city_payload: CreateCitySchema) -> CitySchema:
    """View Logic to Post City Payloads."""

    invalid_cities = controller.check_city_uuids_exists(
        city_payload.allied_cities)

    if city_payload.allied_cities and invalid_cities:
        raise InvalidCityUUIDException(uuid_list=invalid_cities)

    if controller.city_exists_by_coordinates(
            city_payload.geo_location_latitude,
            city_payload.geo_location_longitude):

        raise RepeatedCoordinatesException(
            city_payload.geo_location_latitude,
            city_payload.geo_location_longitude)

    return controller.perform_insert_city(city_payload)


@router.get(
    '/',
    response_model=List[CitySchema],
    status_code=status.HTTP_200_OK)
def get_city_list_view() -> List[CitySchema]:
    """View Logic to retrieve a all cities."""

    return controller.perform_retrieve_cities()


@router.get(
    '/{city_uuid}/',
    response_model=CitySchemaWithAllyForce,
    status_code=status.HTTP_200_OK)
def get_city_by_uuid_view(city_uuid: uuid.UUID) -> CitySchemaWithAllyForce:
    """View Logic to retrieve a city by UUID."""

    if not controller.city_exists(city_uuid):
        raise NotFoundCityUUIDException(city_uuid=city_uuid)

    result = controller.peform_retrieve_city_by_id_with_ally_power(city_uuid)

    return result


@router.put(
    '/{city_uuid}/',
    response_model=CitySchema,
    status_code=status.HTTP_200_OK)
def update_city_by_id_view(
        city_payload: UpdateCitySchema, city_uuid: uuid.UUID) -> CitySchema:
    """View Logic to update a city payload by UUID."""

    if not controller.city_exists(city_uuid):
        raise NotFoundCityUUIDException(city_uuid=city_uuid)

    invalid_cities = controller.check_city_uuids_exists(
        city_payload.allied_cities)

    if city_payload.allied_cities and invalid_cities:
        raise InvalidCityUUIDException(uuid_list=invalid_cities)

    if controller.city_exists_by_coordinates(
            city_payload.geo_location_latitude,
            city_payload.geo_location_longitude):

        raise RepeatedCoordinatesException(
            city_payload.geo_location_latitude,
            city_payload.geo_location_longitude)

    result = controller.perform_update_city_by_id(city_uuid, city_payload)

    return result


@router.delete(
    '/{city_uuid}/',
    status_code=status.HTTP_204_NO_CONTENT)
def perform_delete_city_by_id_view(city_uuid: uuid.UUID) -> None:
    """View Logic to delete a city by UUID."""

    if not controller.city_exists(city_uuid):
        raise NotFoundCityUUIDException(city_uuid=city_uuid)

    return controller.perform_delete_city_by_id(city_uuid)
