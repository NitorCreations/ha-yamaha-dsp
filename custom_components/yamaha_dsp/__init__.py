import logging
import re

from dataclasses import dataclass
from enum import Enum

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceInfo

from custom_components.yamaha_dsp.const import DOMAIN
from custom_components.yamaha_dsp.yamaha.device import ProductInformation, YamahaDspDevice


@dataclass
class SpeakerConfiguration:
    name: str
    index_source: int
    index_volume: int
    index_mute: int
    available_inputs: list[str]


@dataclass
class SourceConfiguration:
    name: str
    index_volume: int
    index_mute: int


@dataclass
class RouteConfiguration:
    name: str
    index_mute: int


class EntityType(Enum):
    SPEAKER = "speaker"
    SOURCE = "source"
    ROUTE = "route"


PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.SWITCH]
UNIQUE_ID_REGEXP = re.compile(r"[\s+]")
STANDARD_SOURCES = ["Lounge", "Classroom", "Lovelace"]
YAMAHA_DSP_CONFIGURATION = {
    "speakers": [
        SpeakerConfiguration("Kitchen", 33, 47, 48, STANDARD_SOURCES),
        SpeakerConfiguration("Classroom", 35, 51, 52, STANDARD_SOURCES),
        SpeakerConfiguration("DJ Booth", 34, 49, 50, STANDARD_SOURCES),
        SpeakerConfiguration("Lovelace", 42, 65, 66, STANDARD_SOURCES),
        SpeakerConfiguration("Shannon", 40, 61, 62, ["Lounge", "Classroom", "Lovelace", "TV"]),
        SpeakerConfiguration("Spa", 36, 53, 54, STANDARD_SOURCES),
        SpeakerConfiguration("Spa Lounge", 32, 45, 46, ["Lounge", "Classroom", "Lovelace", "TV"]),
        SpeakerConfiguration("Terrace", 37, 55, 56, STANDARD_SOURCES),
        SpeakerConfiguration("Lounge", 34, 49, 50, STANDARD_SOURCES),
    ],
    "sources": [
        SourceConfiguration("Classroom device", 14, 15),
        SourceConfiguration("Lounge DJ mixer", 11, 12),
        SourceConfiguration("Lounge Mac Mini", 8, 9),
        SourceConfiguration("Lounge USB input", 17, 18),
        SourceConfiguration("Lovelace TV", 23, 24),
        SourceConfiguration("Shannon TV", 26, 27),
        SourceConfiguration("Spa Lounge TV", 45, 46),
        SourceConfiguration("Wireless mics", 5, 6),
    ],
    "routes": [
        RouteConfiguration("Wireless mics to classroom", 2),
        RouteConfiguration("Wireless mics to lounge", 1),
        RouteConfiguration("Wireless mics to Lovelace", 3),
    ],
}

logger = logging.getLogger(__name__)


def create_unique_id(name: str, entity_type: EntityType) -> str:
    id = f"{name.lower()}_{entity_type.value}"
    id = re.sub(UNIQUE_ID_REGEXP, "_", id)

    return id


@dataclass
class RuntimeData:
    device: YamahaDspDevice
    product_information: ProductInformation
    device_info: DeviceInfo


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Create device
    if "host" in entry.data and "port" in entry.data:
        device = YamahaDspDevice(entry.data["host"], entry.data["port"])
    else:
        raise KeyError("Config entry is missing required parameters")

    # Verify that we can connect, store device handle and product/device information
    try:
        await device.connect()
        product_information = await device.query_product_information()
        device_info = DeviceInfo(
            identifiers={(DOMAIN, product_information.serial_number)},
            manufacturer="Yamaha",
            model=product_information.product_name,
            model_id=product_information.device_id,
            serial_number=product_information.serial_number,
            sw_version=product_information.firmware_version,
        )

        entry.runtime_data = RuntimeData(device, product_information, device_info)
    except ConnectionError as e:
        raise ConfigEntryNotReady("Unable to connect") from e

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
