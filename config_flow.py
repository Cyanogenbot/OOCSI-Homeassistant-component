"""Config flow for Oocsi for HomeAssistant integration."""
from __future__ import annotations

import logging
from typing import Any

from oocsi import OOCSI, OOCSIDisconnect
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

"Import everything that is necessary"

_LOGGER = logging.getLogger(__name__)

PLATFORMS = "switch"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 4444

USER_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME): str,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Oocsi for HomeAssistant."""

    VERSION = 1

    def __init__(self):
        """Build global variables for configuration flow."""
        self.name = CONF_NAME
        self.port = CONF_PORT
        self.host = CONF_HOST

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                await self._connect_to_oocsi(user_input)

            except OOCSIDisconnect:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_NAME])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_NAME: self.name,
                        CONF_HOST: self.host,
                        CONF_PORT: self.port,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_CONFIG_SCHEMA,
            errors=errors,
        )

    async def _connect_to_oocsi(self, user_input):
        """Attempt oocsi connection details."""
        self.name = user_input[CONF_NAME]
        self.host = user_input[CONF_HOST]
        self.port = user_input[CONF_PORT]
        oocsiconnect = OOCSI(self.name, self.host, self.port, None, _LOGGER.info, 1)
        oocsiconnect.stop()


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
