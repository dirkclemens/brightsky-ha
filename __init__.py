"""BrightSky Weather integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MODE,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ENTRY_NAME,
    ENTRY_WEATHER_COORDINATOR,
    PLATFORMS,
    UPDATE_LISTENER,
)
from .weather_update_coordinator import BrightSkyWeatherUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BrightSky Weather as config entry."""
    # Get configuration
    name = entry.data[CONF_NAME]
    latitude = _get_config_value(entry, CONF_LATITUDE)
    longitude = _get_config_value(entry, CONF_LONGITUDE)
    forecast_mode = _get_config_value(entry, CONF_MODE)
    scan_interval = _get_config_value(entry, CONF_SCAN_INTERVAL)

    # If scan_interval config value is not configured fall back to the entry data config value
    if not scan_interval:
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    # If latitude or longitude is not configured fall back to the HA location
    if not latitude:
        latitude = hass.config.latitude
    if not longitude:
        longitude = hass.config.longitude

    # Ensure scan interval is at least 60 seconds
    scan_interval = max(scan_interval, 60)

    hass.data.setdefault(DOMAIN, {})

    # Create and link weather coordinator
    weather_coordinator = BrightSkyWeatherUpdateCoordinator(
        latitude,
        longitude,
        timedelta(seconds=scan_interval),
        hass,
        entry,
    )

    # Initial data refresh
    await weather_coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        ENTRY_NAME: name,
        ENTRY_WEATHER_COORDINATOR: weather_coordinator,
        CONF_LATITUDE: latitude,
        CONF_LONGITUDE: longitude,
        CONF_MODE: forecast_mode,
        CONF_SCAN_INTERVAL: scan_interval,
    }

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener
    update_listener = entry.add_update_listener(async_update_options)
    hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER] = update_listener

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    _LOGGER.info("Unloading BrightSky Weather")

    if unload_ok:
        # Remove update listener
        update_listener = hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER]
        update_listener()

        # Remove entry from data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


def _get_config_value(config_entry: ConfigEntry, key: str) -> Any:
    """Get a config value from either options or data."""
    if config_entry.options and key in config_entry.options:
        return config_entry.options[key]
    # Check if key exists in data
    if config_entry.data and key in config_entry.data:
        return config_entry.data[key]
    return None
