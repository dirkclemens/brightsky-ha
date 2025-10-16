"""Weather entity for BrightSky integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.weather import (
    Forecast,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MODE,
    CONF_NAME,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import utc_from_timestamp

from .const import (
    ATTRIBUTION,
    CONDITION_MAP,
    DOMAIN,
    ENTRY_WEATHER_COORDINATOR,
    FORECAST_MODE_DAILY,
    FORECAST_MODE_HOURLY,
    ICON_MAP,
    MANUFACTURER,
)
from .weather_update_coordinator import BrightSkyWeatherUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BrightSky Weather entity based on a config entry."""
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    name = domain_data[CONF_NAME]
    weather_coordinator = domain_data[ENTRY_WEATHER_COORDINATOR]
    forecast_mode = domain_data.get(CONF_MODE, FORECAST_MODE_DAILY)

    # Verwende die Config-Entry ID als Gerät-ID
    device_id = config_entry.entry_id
    unique_id = f"{config_entry.entry_id}-weather"

    entity = BrightSkyWeather(
        name, unique_id, forecast_mode, weather_coordinator, device_id
    )

    async_add_entities([entity], False)


def _map_daily_forecast(forecast) -> Forecast:
    """Map BrightSky daily forecast data to Home Assistant format."""
    # Convert timestamp to datetime
    try:
        timestamp = utc_from_timestamp(
            forecast.get("timestamp")
        ).isoformat()
    except (ValueError, TypeError):
        timestamp = forecast.get("timestamp", "")
    
    mapped_forecast = {
        "datetime": timestamp,
        "condition": ICON_MAP.get(forecast.get("icon"), "sunny"),
        "native_temperature": forecast.get("temperature_max"),
        "native_templow": forecast.get("temperature_min"),
        "native_precipitation": forecast.get("precipitation"),
        "precipitation_probability": None,  # Not provided by BrightSky
        "native_pressure": forecast.get("pressure_msl"),
        "humidity": forecast.get("relative_humidity"),
        "cloud_coverage": forecast.get("cloud_cover"),
        "native_wind_speed": forecast.get("wind_speed"),
        "native_wind_gust_speed": None,  # Not always provided in daily forecast
        "wind_bearing": forecast.get("wind_direction"),
    }
    
    return mapped_forecast


def _map_hourly_forecast(forecast) -> Forecast:
    """Map BrightSky hourly forecast data to Home Assistant format."""
    # Convert timestamp to datetime if needed
    try:
        timestamp = utc_from_timestamp(
            forecast.get("timestamp")
        ).isoformat()
    except (ValueError, TypeError):
        timestamp = forecast.get("timestamp", "")
    
    mapped_forecast = {
        "datetime": timestamp,
        "condition": ICON_MAP.get(forecast.get("icon"), "sunny"),
        "native_temperature": forecast.get("temperature"),
        "native_apparent_temperature": None,  # Not provided by BrightSky
        "native_dew_point": forecast.get("dew_point"),
        "native_pressure": forecast.get("pressure_msl"),
        "native_wind_speed": forecast.get("wind_speed"),
        "wind_bearing": forecast.get("wind_direction"),
        "native_wind_gust_speed": forecast.get("wind_gust_speed"),
        "humidity": forecast.get("relative_humidity"),
        "native_precipitation": forecast.get("precipitation"),
        "precipitation_probability": None,  # Not always provided 
        "cloud_coverage": forecast.get("cloud_cover"),
    }
    
    return mapped_forecast


class BrightSkyWeather(SingleCoordinatorWeatherEntity[BrightSkyWeatherUpdateCoordinator]):
    """Implementation of a BrightSky Weather entity."""

    _attr_attribution = ATTRIBUTION
    _attr_should_poll = False
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_precipitation_unit = UnitOfLength.MILLIMETERS
    _attr_native_visibility_unit = UnitOfLength.KILOMETERS

    def __init__(
        self,
        name: str,
        unique_id: str,
        forecast_mode: str,
        weather_coordinator: BrightSkyWeatherUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(weather_coordinator)
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": name,
            "manufacturer": MANUFACTURER,
            "model": "Weather Station",
            "sw_version": "1.0",
        }
        self._forecast_mode = forecast_mode

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        current = self.coordinator.get_current_weather()
        if not current:
            return None
            
        try:
            if isinstance(current, list):
                if not current or len(current) == 0:
                    return None
                return current[0].get("temperature") if current[0] else None
            elif isinstance(current, dict):
                return current.get("temperature")
            return None
        except Exception as e:
            _LOGGER.error("Error determining temperature: %s", e)
            return None

    @property
    def native_pressure(self) -> float | None:
        """Return the current pressure."""
        current = self.coordinator.get_current_weather()
        if not current:
            return None
            
        try:
            if isinstance(current, list):
                if not current or len(current) == 0:
                    return None
                return current[0].get("pressure_msl") if current[0] else None
            elif isinstance(current, dict):
                return current.get("pressure_msl")
            return None
        except Exception as e:
            _LOGGER.error("Error determining pressure: %s", e)
            return None

    @property
    def humidity(self) -> float | None:
        """Return the current humidity."""
        current = self.coordinator.get_current_weather()
        if not current:
            return None
            
        try:
            if isinstance(current, list):
                if not current or len(current) == 0:
                    return None
                return current[0].get("relative_humidity") if current[0] else None
            elif isinstance(current, dict):
                return current.get("relative_humidity")
            return None
        except Exception as e:
            _LOGGER.error("Error determining humidity: %s", e)
            return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the current wind speed."""
        current = self.coordinator.get_current_weather()
        if not current:
            return None
            
        try:
            if isinstance(current, list):
                if not current or len(current) == 0:
                    return None
                return current[0].get("wind_speed") if current[0] else None
            elif isinstance(current, dict):
                return current.get("wind_speed")
            return None
        except Exception as e:
            _LOGGER.error("Error determining wind speed: %s", e)
            return None

    @property
    def wind_bearing(self) -> float | None:
        """Return the current wind bearing."""
        current = self.coordinator.get_current_weather()
        if not current:
            return None
            
        try:
            if isinstance(current, list):
                if not current or len(current) == 0:
                    return None
                return current[0].get("wind_direction") if current[0] else None
            elif isinstance(current, dict):
                return current.get("wind_direction")
            return None
        except Exception as e:
            _LOGGER.error("Error determining wind bearing: %s", e)
            return None

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the current wind gust speed."""
        current = self.coordinator.get_current_weather()
        if not current:
            return None
            
        try:
            if isinstance(current, list):
                if not current or len(current) == 0:
                    return None
                return current[0].get("wind_gust_speed") if current[0] else None
            elif isinstance(current, dict):
                return current.get("wind_gust_speed")
            return None
        except Exception as e:
            _LOGGER.error("Error determining wind gust speed: %s", e)
            return None

    @property
    def native_dew_point(self) -> float | None:
        """Return the current dew point."""
        current = self.coordinator.get_current_weather()
        if not current:
            return None
            
        try:
            if isinstance(current, list):
                if not current or len(current) == 0:
                    return None
                return current[0].get("dew_point") if current[0] else None
            elif isinstance(current, dict):
                return current.get("dew_point")
            return None
        except Exception as e:
            _LOGGER.error("Error determining dew point: %s", e)
            return None

    @property
    def cloud_coverage(self) -> int | None:
        """Return the current cloud coverage."""
        current = self.coordinator.get_current_weather()
        if not current:
            return None
            
        try:
            if isinstance(current, list):
                if not current or len(current) == 0:
                    return None
                return current[0].get("cloud_cover") if current[0] else None
            elif isinstance(current, dict):
                return current.get("cloud_cover")
            return None
        except Exception as e:
            _LOGGER.error("Error determining cloud coverage: %s", e)
            return None

    @property
    def visibility(self) -> float | None:
        """Return the visibility."""
        current = self.coordinator.get_current_weather()
        if not current:
            return None
            
        try:
            visibility = None
            if isinstance(current, list):
                if not current or len(current) == 0:
                    return None
                visibility = current[0].get("visibility") if current[0] else None
            elif isinstance(current, dict):
                visibility = current.get("visibility")
            
            # Convert from meters to kilometers
            if visibility is not None:
                return visibility / 1000
            return None
        except Exception as e:
            _LOGGER.error("Error determining visibility: %s - Data: %s", e, current)
            return None

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        current = self.coordinator.get_current_weather()
        _LOGGER.debug("Current weather data for condition: %s", current)
        
        # Default value when no data is available
        if current is None:
            return "sunny"
        
        try:
            # Check if current is a dictionary or a list
            if isinstance(current, list):
                if not current:
                    return "sunny"  # Empty list
                
                first_item = current[0] if len(current) > 0 else None
                if not first_item:
                    return "sunny"  # Empty first item
                
                # First check if icon is available
                icon = first_item.get("icon")
                if icon:
                    return ICON_MAP.get(icon, "sunny")
                    
                # Then try condition
                condition = first_item.get("condition")
                if condition:
                    return CONDITION_MAP.get(condition, "sunny")
            elif isinstance(current, dict):
                # First check if icon is available
                icon = current.get("icon")
                if icon:
                    return ICON_MAP.get(icon, "sunny")
                    
                # Then try condition
                condition = current.get("condition")
                if condition:
                    return CONDITION_MAP.get(condition, "sunny")
            
            # If we got here, no valid condition was found
            _LOGGER.warning("Could not determine weather condition from data: %s", current)
            return "sunny"  # Default
        except Exception as e:
            _LOGGER.error("Error determining weather condition: %s - Data: %s", e, current)
            return "sunny"  # Default on error

    @callback
    def _async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        forecasts = self.coordinator.get_daily_forecast()
        if not forecasts:
            return None
            
        return [_map_daily_forecast(forecast) for forecast in forecasts]

    @callback
    def _async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast."""
        forecasts = self.coordinator.get_hourly_forecast()
        if not forecasts:
            return None
            
        return [_map_hourly_forecast(forecast) for forecast in forecasts]
