"""Weather data coordinator for the BrightSky service."""

import logging
from datetime import datetime, timedelta
from typing import Any

import async_timeout
from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by BrightSky via Deutscher Wetterdienst (DWD)"


class BrightSkyWeatherUpdateCoordinator(DataUpdateCoordinator):
    """Weather data update coordinator for BrightSky."""

    def __init__(
        self,
        latitude: float,
        longitude: float,
        scan_interval: timedelta,
        hass,
        config_entry: ConfigEntry,
        endpoint: str = "https://api.brightsky.dev",
    ):
        """Initialize coordinator."""
        self.latitude = latitude
        self.longitude = longitude
        self.endpoint = endpoint
        self._connect_error = False

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update the weather data."""
        data = {}
        async with async_timeout.timeout(60):
            try:
                current_data = await self._get_current_weather()
                forecast_data = await self._get_forecast_weather()
                
                data = {
                    "current": current_data,
                    "forecast": forecast_data,
                }
                
                self._connect_error = False
                return data
                
            except ClientError as err:
                if not self._connect_error:
                    _LOGGER.error("Error communicating with BrightSky API: %s", err)
                    self._connect_error = True
                raise UpdateFailed(f"Error communicating with API: {err}") from err
            except Exception as err:
                _LOGGER.error("Unexpected error fetching BrightSky data: %s", err)
                raise UpdateFailed(f"Unexpected error: {err}") from err

    async def _get_current_weather(self) -> dict[str, Any]:
        """Get current weather data from BrightSky."""
        url = f"{self.endpoint}/current_weather"
        params = {
            "lat": self.latitude,
            "lon": self.longitude,
        }

        session = async_get_clientsession(self.hass)
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            _LOGGER.debug("BrightSky current weather API response: %s", data)
            return data

    async def _get_forecast_weather(self) -> dict[str, Any]:
        """Get forecast weather data from BrightSky."""
        # Get forecast for next 7 days
        today = datetime.now().date()
        end_date = today + timedelta(days=7)
        
        url = f"{self.endpoint}/weather"
        params = {
            "lat": self.latitude,
            "lon": self.longitude,
            "date": today.isoformat(),
            "last_date": end_date.isoformat(),
        }

        session = async_get_clientsession(self.hass)
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            _LOGGER.debug("BrightSky forecast data fetched successfully")
            return data

    def get_current_weather(self) -> dict[str, Any] | list[dict[str, Any]] | None:
        """Get current weather from coordinator data."""
        if not self.data:
            _LOGGER.debug("No data available in coordinator")
            return None
            
        current_data = self.data.get("current", {})
        weather_data = current_data.get("weather")
        _LOGGER.debug("Current weather data structure: %s", weather_data)
        
        # Validierung des Datentyps
        if weather_data is not None and not isinstance(weather_data, (dict, list)):
            _LOGGER.warning("Unexpected data type for weather data: %s", type(weather_data))
            
        return weather_data

    def get_hourly_forecast(self, hours: int = 48) -> list[dict[str, Any]]:
        """Get hourly forecast data."""
        if not self.data or "forecast" not in self.data:
            return []
        
        weather_data = self.data["forecast"].get("weather", [])
        # Return next 'hours' hours of data
        return weather_data[:hours]

    def get_daily_forecast(self, days: int = 7) -> list[dict[str, Any]]:
        """Get daily forecast data by aggregating hourly data."""
        hourly_data = self.get_hourly_forecast(days * 24)
        if not hourly_data:
            return []

        daily_forecasts = []
        
        # Group hourly data by day
        current_date = None
        daily_data = []
        
        for hour_data in hourly_data:
            timestamp = hour_data.get("timestamp", "")
            if not timestamp:
                continue
                
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                date = dt.date()
                
                if current_date is None:
                    current_date = date
                    
                if date != current_date:
                    # Process previous day's data
                    if daily_data:
                        daily_forecast = self._aggregate_daily_data(daily_data, current_date)
                        daily_forecasts.append(daily_forecast)
                    
                    # Start new day
                    current_date = date
                    daily_data = []
                
                daily_data.append(hour_data)
                
            except (ValueError, AttributeError) as err:
                _LOGGER.warning("Error parsing timestamp %s: %s", timestamp, err)
                continue
        
        # Process last day's data
        if daily_data and current_date:
            daily_forecast = self._aggregate_daily_data(daily_data, current_date)
            daily_forecasts.append(daily_forecast)
        
        return daily_forecasts[:days]

    def _aggregate_daily_data(self, hourly_data: list[dict], date) -> dict[str, Any]:
        """Aggregate hourly data into daily forecast."""
        if not hourly_data:
            return {}
        
        # Find min and max temperatures
        temps = [h.get("temperature") for h in hourly_data if h.get("temperature") is not None]
        temp_min = min(temps) if temps else None
        temp_max = max(temps) if temps else None
        
        # Sum precipitation
        precip_sum = sum(h.get("precipitation", 0) or 0 for h in hourly_data)
        
        # Average other values
        pressures = [h.get("pressure_msl") for h in hourly_data if h.get("pressure_msl") is not None]
        avg_pressure = sum(pressures) / len(pressures) if pressures else None
        
        humidities = [h.get("relative_humidity") for h in hourly_data if h.get("relative_humidity") is not None]
        avg_humidity = sum(humidities) / len(humidities) if humidities else None
        
        cloud_covers = [h.get("cloud_cover") for h in hourly_data if h.get("cloud_cover") is not None]
        avg_cloud_cover = sum(cloud_covers) / len(cloud_covers) if cloud_covers else None
        
        wind_speeds = [h.get("wind_speed") for h in hourly_data if h.get("wind_speed") is not None]
        avg_wind_speed = sum(wind_speeds) / len(wind_speeds) if wind_speeds else None
        
        # Use most common condition during daytime hours (6-18)
        daytime_conditions = []
        for h in hourly_data:
            timestamp = h.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if 6 <= dt.hour <= 18 and h.get("condition"):
                    daytime_conditions.append(h.get("condition"))
            except (ValueError, AttributeError):
                continue
        
        # Get most common condition
        condition = None
        icon = None
        if daytime_conditions:
            condition = max(set(daytime_conditions), key=daytime_conditions.count)
            # Use condition to determine icon
            icon = self._condition_to_icon(condition)
        elif hourly_data:
            # Fallback to first hour's condition
            condition = hourly_data[0].get("condition")
            icon = hourly_data[0].get("icon")
        
        return {
            "timestamp": f"{date}T12:00:00+00:00",  # Noon
            "temperature_min": temp_min,
            "temperature_max": temp_max,
            "precipitation": precip_sum,
            "pressure_msl": avg_pressure,
            "relative_humidity": avg_humidity,
            "cloud_cover": avg_cloud_cover,
            "wind_speed": avg_wind_speed,
            "condition": condition,
            "icon": icon,
        }

    def _condition_to_icon(self, condition: str) -> str:
        """Convert condition to appropriate icon."""
        condition_icon_map = {
            "dry": "clear-day",
            "fog": "fog",
            "rain": "rain",
            "sleet": "sleet",
            "snow": "snow",
            "hail": "hail", 
            "thunderstorm": "thunderstorm",
        }
        return condition_icon_map.get(condition, "clear-day")
