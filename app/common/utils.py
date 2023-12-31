"""Module providing util functions to be used in multiple apps."""

import geopy.distance


def calculate_distance(origin: tuple, destination: tuple) -> int:
    """Calculate distance between two points in km."""

    distance = geopy.distance.geodesic(origin, destination).km

    return int(distance)
