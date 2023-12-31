"""Module that contains Util validations for Schemas."""


class CreateValidations:
    """Class that defines custom validations to perform creation."""
    def __init__(self):
        self.population = None
        self.name = ""
        self.geo_location_latitude = None
        self.geo_location_longitude = None

    def __post_init__(self):
        if self.population < 0:
            raise ValueError("Population cannot be a negative value.")

        if len(self.name) == 0:
            raise ValueError("City Name cannot be an empty string.")

        if not -90.0 <= self.geo_location_latitude <= 90.0:
            raise ValueError("Latitude needs to be in -90.0 - 90.0 range.")

        if not -180.0 <= self.geo_location_longitude <= 180.0:
            raise ValueError("Longitude needs to be in -180.0 - 180.0 range.")


class UpdateValidations:
    """Class that defines custom validations to perform update."""

    def __init__(self):
        self.population = None
        self.name = ""
        self.geo_location_latitude = None
        self.geo_location_longitude = None

    def __post_init__(self):
        if self.population and self.population < 0:
            raise ValueError("Population cannot be a negative value.")

        if self.name is not None and len(self.name) == 0:
            raise ValueError("City Name cannot be an empty string.")

        if self.geo_location_latitude and not (
                -90.0 <= self.geo_location_latitude <= 90.0):
            raise ValueError("Latitude needs to be in -90.0 - 90.0 range.")

        if self.geo_location_longitude and not (
                -180.0 <= self.geo_location_longitude <= 180.0):
            raise ValueError("Longitude needs to be in -180.0 - 180.0 range.")
