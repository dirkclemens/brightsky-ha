"""Constants for the BrightSky Weather integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_PRESSURE,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
)
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UV_INDEX,
    Platform,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)

DOMAIN = "brightsky"
DEFAULT_NAME = "BrightSky Weather"
DEFAULT_SCAN_INTERVAL = 1800  # 30 minutes (DWD updates hourly)
DEFAULT_ENDPOINT = "https://api.brightsky.dev"
ATTRIBUTION = "Data provided by BrightSky via Deutscher Wetterdienst (DWD)"
MANUFACTURER = "BrightSky"

CONFIG_FLOW_VERSION = 1
ENTRY_NAME = "name"
ENTRY_WEATHER_COORDINATOR = "weather_coordinator"
UPDATE_LISTENER = "update_listener"

PLATFORMS = [Platform.SENSOR, Platform.WEATHER]

# BrightSky specific attributes
ATTR_API_TEMPERATURE = "temperature"
ATTR_API_DEW_POINT = "dew_point"
ATTR_API_CLOUD_COVER = "cloud_cover"
ATTR_API_VISIBILITY = "visibility"
ATTR_API_WIND_SPEED = "wind_speed_10"
ATTR_API_WIND_DIRECTION = "wind_direction_10"
ATTR_API_WIND_GUST_SPEED = "wind_gust_speed_10"
ATTR_API_PRESSURE = "pressure_msl"
ATTR_API_HUMIDITY = "relative_humidity"
ATTR_API_PRECIPITATION = "precipitation_10"
ATTR_API_SUNSHINE = "sunshine_60"
ATTR_API_CONDITION = "condition"
ATTR_API_ICON = "icon"
ATTR_API_TIMESTAMP = "timestamp"

FORECAST_MODE_HOURLY = "hourly"
FORECAST_MODE_DAILY = "daily"

FORECAST_MODES = [
    FORECAST_MODE_HOURLY,
    FORECAST_MODE_DAILY,
]

DEFAULT_FORECAST_MODE = FORECAST_MODE_DAILY

# BrightSky condition mapping to Home Assistant conditions
CONDITION_MAP = {
    "dry": "sunny",
    "fog": "fog",
    "rain": "rainy",
    "sleet": "snowy-rainy",
    "snow": "snowy",
    "hail": "hail",
    "thunderstorm": "lightning",
}

# BrightSky icon mapping to Home Assistant conditions
ICON_MAP = {
    "clear-day": "sunny", 
    "clear-night": "clear-night",
    "partly-cloudy-day": "partlycloudy",
    "partly-cloudy-night": "partlycloudy", 
    "cloudy": "cloudy",
    "fog": "fog",
    "wind": "windy",
    "rain": "rainy",
    "sleet": "snowy-rainy",
    "snow": "snowy",
    "hail": "hail",
    "thunderstorm": "lightning",
}

# Sensor types for BrightSky data
WEATHER_SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=ATTR_API_TEMPERATURE,
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_DEW_POINT,
        name="Dew Point",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_HUMIDITY,
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_PRESSURE,
        name="Pressure",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_WIND_SPEED,
        name="Wind Speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_WIND_DIRECTION,
        name="Wind Direction",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_WIND_GUST_SPEED,
        name="Wind Gust Speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_CLOUD_COVER,
        name="Cloud Cover",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_VISIBILITY,
        name="Visibility",
        native_unit_of_measurement=UnitOfLength.METERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_PRECIPITATION,
        name="Precipitation",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=ATTR_API_SUNSHINE,
        name="Sunshine Duration",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=ATTR_API_CONDITION,
        name="Weather Condition",
    ),
)