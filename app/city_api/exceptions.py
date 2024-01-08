from fastapi import HTTPException, status


class InvalidCityUUIDException(HTTPException):
    """Exception raised for trying to request a non existing cities."""

    def __init__(self, uuid_list):
        self.status_code = status.HTTP_400_BAD_REQUEST
        uuids = ','.join(list(map(str, uuid_list)))
        self.detail = f"UUID(s) {uuids} does not exists."

        super().__init__(self.status_code, self.detail)


class NotFoundCityUUIDException(HTTPException):
    """Exception raised for trying to request a non existing city."""

    def __init__(self, city_uuid):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = f"City with UUID {city_uuid} does not exist."

        super().__init__(self.status_code, self.detail)


class RepeatedCoordinatesException(HTTPException):
    """Exception raised for using the same coordinates."""

    def __init__(self, latitude, longitude):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"City with ({latitude}, {longitude}) already exists."

        super().__init__(self.status_code, self.detail)


class SelfCityUUIDException(HTTPException):
    """Exception raised for using the same uuid in the body request."""

    def __init__(self, city_uuid):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"UUID {city_uuid} in url cannot be used in the request."

        super().__init__(self.status_code, self.detail)
