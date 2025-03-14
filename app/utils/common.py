import sys

import geopy.distance


def is_testing() -> bool:
    """Check if the app is running in a test environment."""
    return "pytest" in sys.modules


def calculate_distance(origin: tuple, destination: tuple) -> int:
    """Calculate distance between two points in km."""

    distance = geopy.distance.geodesic(origin, destination).km

    return int(distance)
