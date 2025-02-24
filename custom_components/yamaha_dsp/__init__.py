import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.yamaha_dsp.yamaha.device import YamahaDspDevice

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]

logger = logging.getLogger(__name__)


@dataclass
class RuntimeData:
    device: YamahaDspDevice


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Create device
    if "host" in entry.data and "port" in entry.data:
        device = YamahaDspDevice(entry.data["host"], entry.data["port"])
    else:
        raise KeyError("Config entry is missing required parameters")

    # Verify that we can connect, store device handle
    try:
        await device.connect()

        entry.runtime_data = RuntimeData(device)
    except ConnectionError as e:
        raise ConfigEntryNotReady("Unable to connect") from e

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
