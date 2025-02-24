import logging

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from custom_components.yamaha_dsp.const import CONF_HOST, CONF_PORT, DOMAIN
from custom_components.yamaha_dsp.yamaha.device import YamahaDspDevice

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=49280): int,
    }
)

logger = logging.getLogger(__name__)


class YamahaDspUserFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

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
