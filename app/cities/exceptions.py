from typing import List
from uuid import UUID


class InvalidAllyException(Exception):
    """Custom exception raised when an ally UUID does not exist in the city table."""

    def __init__(self, invalid_allies: List[UUID]):
        self.invalid_allies = invalid_allies
        super().__init__(
            f"Invalid ally UUIDs: {', '.join(str(ally) for ally in invalid_allies)}"
        )


class DatabaseOperationException(Exception):
    """Custom exception raised when a database operation fails."""

    def __init__(self, message: str):
        super().__init__(f"Database operation failed: {message}")


class CityNotFoundException(Exception):
    """Custom exception raised when a city with a given UUID does not exist."""

    def __init__(self, city_uuid: UUID):
        self.city_uuid = city_uuid
        super().__init__(f"City with UUID {str(city_uuid)} not found.")
