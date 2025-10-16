"""Config flow for BrightSky Weather."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MODE,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONFIG_FLOW_VERSION,
    DEFAULT_FORECAST_MODE,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    FORECAST_MODES,
)

_LOGGER = logging.getLogger(__name__)


class BrightSkyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for BrightSky Weather."""

    VERSION = CONFIG_FLOW_VERSION

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> "BrightSkyOptionsFlow":
        """Get the options flow for this handler."""
        return BrightSkyOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(
                    CONF_LATITUDE, default=self.hass.config.latitude
                ): cv.latitude,
                vol.Optional(
                    CONF_LONGITUDE, default=self.hass.config.longitude
                ): cv.longitude,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
                vol.Optional(CONF_MODE, default=DEFAULT_FORECAST_MODE): vol.In(
                    FORECAST_MODES
                ),
            }
        )

        if user_input is not None:
            # Check if already configured
            await self.async_set_unique_id(
                f"{user_input[CONF_LATITUDE]}-{user_input[CONF_LONGITUDE]}"
            )
            self._abort_if_unique_id_configured()

            # Verify connectivity to BrightSky
            if await _verify_brightsky_connectivity(self.hass, user_input):
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
            
            errors["base"] = "cannot_connect"

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


class BrightSkyOptionsFlow(OptionsFlow):
    """Handle options for BrightSky Weather."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self._get_options_schema(),
        )

    def _get_options_schema(self) -> vol.Schema:
        """Return options schema."""
        options = {
            vol.Optional(
                CONF_MODE,
                default=self.config_entry.options.get(
                    CONF_MODE, self.config_entry.data.get(CONF_MODE, DEFAULT_FORECAST_MODE)
                ),
            ): vol.In(FORECAST_MODES),
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL,
                    self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ),
            ): int,
        }

        # Include latitude and longitude for existing entries
        if CONF_LATITUDE in self.config_entry.data:
            options[
                vol.Optional(
                    CONF_LATITUDE,
                    default=self.config_entry.options.get(
                        CONF_LATITUDE, self.config_entry.data[CONF_LATITUDE]
                    ),
                )
            ] = cv.latitude

        if CONF_LONGITUDE in self.config_entry.data:
            options[
                vol.Optional(
                    CONF_LONGITUDE,
                    default=self.config_entry.options.get(
                        CONF_LONGITUDE, self.config_entry.data[CONF_LONGITUDE]
                    ),
                )
            ] = cv.longitude

        return vol.Schema(options)


async def _verify_brightsky_connectivity(hass, config_data: dict[str, Any]) -> bool:
    """Verify connectivity to the BrightSky API."""
    import aiohttp

    latitude = config_data.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config_data.get(CONF_LONGITUDE, hass.config.longitude)
    
    url = f"https://api.brightsky.dev/current_weather"
    params = {
        "lat": latitude,
        "lon": longitude,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return response.status == 200
    except Exception as ex:
        _LOGGER.error("Error connecting to BrightSky API: %s", ex)
        return False
