import json
import logging
import re

from dataclasses import dataclass
from enum import Enum

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
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


@dataclass
class RouterSourceConfiguration:
    label: str
    value: int


@dataclass
class RouterConfiguration:
    name: str
    index_source: int
    sources: list[RouterSourceConfiguration]


@dataclass
class DspConfiguration:
    speakers: [SpeakerConfiguration]
    sources: [SourceConfiguration]
    routes: [RouteConfiguration]
    routers: [RouterConfiguration]

    def __init__(self):
        self.speakers = []
        self.sources = []
        self.routes = []
        self.routers = []


class EntityType(Enum):
    SPEAKER = "speaker"
    SOURCE = "source"
    ROUTE = "route"
    ROUTER = "router"


PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.SWITCH, Platform.SELECT]
UNIQUE_ID_REGEXP = re.compile(r"[\s+]")

logger = logging.getLogger(__name__)


def create_unique_id(name: str, entity_type: EntityType) -> str:
    id = f"{name.lower()}_{entity_type.value}"
    id = re.sub(UNIQUE_ID_REGEXP, "_", id)

    return id


def create_dsp_configuration(options) -> DspConfiguration:
    dsp_configuration = DspConfiguration()

    for speaker_configuration in options.get("speaker_configuration") or []:
        parsed = json.loads(speaker_configuration)
        dsp_configuration.speakers.append(
            SpeakerConfiguration(
                parsed["name"],
                parsed["index_source"],
                parsed["index_volume"],
                parsed["index_mute"],
                parsed.get("sources") or options["default_speaker_sources"],
            )
        )

    for source_configuration in options.get("source_configuration") or []:
        parsed = json.loads(source_configuration)
        dsp_configuration.sources.append(
            SourceConfiguration(
                parsed["name"],
                parsed["index_volume"],
                parsed["index_mute"],
            )
        )

    for route_configuration in options.get("route_configuration") or []:
        parsed = json.loads(route_configuration)
        dsp_configuration.routes.append(
            RouteConfiguration(
                parsed["name"],
                parsed["index_mute"],
            )
        )

    for router_configuration in options.get("router_configuration") or []:
        parsed = json.loads(router_configuration)
        sources: list[RouterSourceConfiguration] = []
        seen_labels: set[str] = set()

        for source in parsed["sources"]:
            label = source["label"]
            value = int(source["value"])
            if label in seen_labels:
                raise ValueError(f"Duplicate router source label '{label}' in '{parsed['name']}'")
            seen_labels.add(label)
            sources.append(RouterSourceConfiguration(label=label, value=value))

        if not sources:
            raise ValueError(f"Router '{parsed['name']}' must define at least one source")

        dsp_configuration.routers.append(
            RouterConfiguration(
                parsed["name"],
                parsed["index_source"],
                sources,
            )
        )

    return dsp_configuration


@dataclass
class RuntimeData:
    device: YamahaDspDevice
    product_information: ProductInformation
    device_info: DeviceInfo
    dsp_configuration: DspConfiguration


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

        # Build the DSP configuration based on the configuration given by the option flow
        dsp_configuration = create_dsp_configuration(entry.options)

        entry.runtime_data = RuntimeData(device, product_information, device_info, dsp_configuration)
    except ConnectionError as e:
        raise ConfigEntryNotReady("Unable to connect") from e
    except json.JSONDecodeError as e:
        raise ConfigEntryError() from e
    except ValueError as e:
        raise ConfigEntryError() from e

    # Register a listener for option updates
    entry.async_on_unload(entry.add_update_listener(entry_update_listener))

    logger.info(f"Initializing entry with runtime data: {entry.runtime_data}")
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Disconnect from the device when unloading, otherwise we'll get a
    # "Task was destroyed but it is pending" error
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        runtime_data: RuntimeData = entry.runtime_data
        await runtime_data.device.disconnect()

    return unload_ok


async def entry_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    # Reload the entry when options have been changed
    await hass.config_entries.async_reload(config_entry.entry_id)
