"""Sensor entities for BrightSky integration."""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Union

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    UnitOfLength,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfSpeed,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    DOMAIN,
    ENTRY_WEATHER_COORDINATOR,
    MANUFACTURER,
    WEATHER_SENSOR_TYPES,
)
from .weather_update_coordinator import BrightSkyWeatherUpdateCoordinator


_LOGGER = logging.getLogger(__name__)


from dataclasses import dataclass

@dataclass
class BrightSkySensorEntityDescription(SensorEntityDescription):
    """Describe a BrightSky sensor entity."""
    
    # Zusätzliche Felder für unsere Sensorbeschreibung
    value_fn: Callable[[Dict[str, Any]], StateType] = None
    available_fn: Callable[[Dict[str, Any]], bool] = None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BrightSky sensor entities based on a config entry."""
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    weather_coordinator = domain_data[ENTRY_WEATHER_COORDINATOR]
    name = domain_data[CONF_NAME]
    latitude = domain_data[CONF_LATITUDE]
    longitude = domain_data[CONF_LONGITUDE]

    entities = []
    
    # Gemeinsame Device-ID für alle Sensoren
    device_id = config_entry.entry_id

    # Add current condition sensors
    for description in WEATHER_SENSOR_TYPES:
        # Anstatt die value_fn zuzuweisen, erstelle eine neue Instanz mit value_fn
        # und den Werten aus der Beschreibung
        value_fn_for_key = lambda data, key=description.key: _get_current_sensor_value(data, key)
        available_fn = lambda data: _is_sensor_data_available(data)
        
        sensor_description = BrightSkySensorEntityDescription(
            key=description.key,
            name=description.name,
            native_unit_of_measurement=description.native_unit_of_measurement,
            device_class=description.device_class,
            state_class=description.state_class,
            value_fn=value_fn_for_key,
            available_fn=available_fn,
        )
        
        unique_id = f"{config_entry.unique_id}-{description.key}"
        entities.append(
            BrightSkySensor(
                weather_coordinator,
                sensor_description,
                unique_id,
                name,
                latitude,
                longitude,
                device_id,
            )
        )

    async_add_entities(entities)


def _get_current_sensor_value(data: dict[str, Any], key: str) -> StateType:
    """Extract the current value for a specific sensor."""
    if not data or "current" not in data:
        return None
        
    current_weather = data["current"].get("weather")
    if not current_weather:
        return None
        
    # Handle both list and dictionary structure
    current_data = None
    if isinstance(current_weather, list) and len(current_weather) > 0:
        current_data = current_weather[0]
    elif isinstance(current_weather, dict):
        current_data = current_weather
    else:
        return None
    if not current_data:
        return None
        
    return current_data.get(key)


def _is_sensor_data_available(data: dict[str, Any]) -> bool:
    """Determine if sensor data is available."""
    if not data or "current" not in data:
        return False
        
    current_weather = data["current"].get("weather")
    if not current_weather:
        return False
        
    # Handle both list and dictionary structure
    if isinstance(current_weather, list):
        return len(current_weather) > 0
    elif isinstance(current_weather, dict):
        return bool(current_weather)
    return False


class BrightSkySensor(CoordinatorEntity[BrightSkyWeatherUpdateCoordinator], SensorEntity):
    """Implementation of a BrightSky sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    
    entity_description: BrightSkySensorEntityDescription

    def __init__(
        self,
        coordinator: BrightSkyWeatherUpdateCoordinator,
        description: BrightSkySensorEntityDescription,
        unique_id: str,
        name: str,
        latitude: float,
        longitude: float,
        device_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = unique_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": name,
            "manufacturer": MANUFACTURER,
            "model": "Weather Station",
            "sw_version": "1.0",
        }
        self._attr_name = description.name

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.data:
            return False
            
        return (
            super().available 
            and self.entity_description.available_fn(self.coordinator.data)
        )
