"""Module that provides constant values."""

CITY_TABLE_NAME = "city"

ALLY_TABLE_NAME = "allied_city"

CITY_IDENTIFIER = "city_uuid"

ALLY_IDENTIFIER = "ally_uuid"

CITY_ALLIED_UUIDS_IDENTIFIER = "current_allied_city_uuids"

UGLY_CHOICE = 'Ugly'

AVERAGE_CHOICE = 'Average'

GORGEOUS_CHOICE = 'Gorgeous'

RETRIEVE_CITY_FIELDS = (
    'city_uuid',
    'name',
    'beauty',
    'population',
    'geo_location_latitude',
    'geo_location_longitude',
    'current_allied_city_uuids'
)

INSERT_CITY_FIELDS = (
    'name',
    'beauty',
    'population',
    'geo_location_latitude',
    'geo_location_longitude'
)

INSERT_ALLY_FIELDS = (
    'city_uuid',
    'ally_uuid'
)
