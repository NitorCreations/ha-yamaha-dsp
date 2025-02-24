import logging

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.helpers import selector
from homeassistant.helpers.selector import TextSelectorConfig

from custom_components.yamaha_dsp.const import (
    CONF_HOST,
    CONF_PORT,
    DOMAIN,
    OPTION_DEFAULT_SPEAKER_SOURCES,
    OPTION_ROUTE_CONFIGURATION,
    OPTION_SOURCE_CONFIGURATION,
    OPTION_SPEAKER_CONFIGURATION,
)
from custom_components.yamaha_dsp.yamaha.device import YamahaDspDevice

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=49280): int,
    }
)

logger = logging.getLogger(__name__)


class YamahaDspConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    # noinspection PyTypeChecker
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Try to connect to the device
                device = YamahaDspDevice(user_input["host"], user_input["port"])
                await device.connect()

                # Make a title for the entry
                product_information = await device.query_product_information()
                title = f"Yamaha {product_information.product_name}"
                logger.info(product_information)

                # Make a unique ID for the entry, prevent adding the same device twice
                unique_id = product_information.serial_number
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                # Disconnect, we'll connect again later, this was just for validation
                await device.disconnect()
            except (BrokenPipeError, ConnectionError, OSError):  # all technically OSError
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return YamahaDspOptionsFlow(config_entry)


class YamahaDspOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Load existing values, use defaults if not defined
        default_speaker_sources = self._config_entry.options.get(OPTION_DEFAULT_SPEAKER_SOURCES) or []
        speaker_configuration = self._config_entry.options.get(OPTION_SPEAKER_CONFIGURATION) or []
        source_configuration = self._config_entry.options.get(OPTION_SOURCE_CONFIGURATION) or []
        route_configuration = self._config_entry.options.get(OPTION_ROUTE_CONFIGURATION) or []

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        OPTION_DEFAULT_SPEAKER_SOURCES, default=default_speaker_sources
                    ): selector.TextSelector(TextSelectorConfig(multiple=True)),
                    vol.Optional(OPTION_SPEAKER_CONFIGURATION, default=speaker_configuration): selector.TextSelector(
                        TextSelectorConfig(multiline=True, multiple=True)
                    ),
                    vol.Optional(OPTION_SOURCE_CONFIGURATION, default=source_configuration): selector.TextSelector(
                        TextSelectorConfig(multiline=True, multiple=True)
                    ),
                    vol.Optional(OPTION_ROUTE_CONFIGURATION, default=route_configuration): selector.TextSelector(
                        TextSelectorConfig(multiline=True, multiple=True)
                    ),
                }
            ),
        )
