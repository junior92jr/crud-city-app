from fastapi import HTTPException, status


class InvalidCityUUIDException(HTTPException):
    """Exception raised for errors in the input interval."""

    def __init__(self, uuid_list):
        self.status_code = status.HTTP_400_BAD_REQUEST
        uuids = ','.join(list(map(str, uuid_list)))
        self.detail = f"UUID(s) {uuids} does not exists."

        super().__init__(self.status_code, self.detail)


class NotFoundCityUUIDException(HTTPException):
    """Exception raised for errors in the input interval."""

    def __init__(self, city_uuid):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = f"City with UUID {city_uuid} does not exist."

        super().__init__(self.status_code, self.detail)


class RepeatedCoordinatesException(HTTPException):
    """Exception raised for errors in the input interval."""

    def __init__(self, latitude, longitude):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"City with ({latitude}, {longitude}) already exists."

        super().__init__(self.status_code, self.detail)
