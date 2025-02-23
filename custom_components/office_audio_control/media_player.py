import logging
from dataclasses import dataclass

from homeassistant.components.media_player import MediaPlayerEntity, MediaPlayerEntityFeature
from homeassistant.core import HomeAssistant

from custom_components.office_audio_control import RuntimeData, YamahaDspDevice


@dataclass
class SpeakerConfiguration:
    name: str
    index_source: int
    index_volume: int
    index_mute: int
    available_inputs: list[str]


STANDARD_SOURCES = ["Lounge", "Classroom", "Lovelace"]
OFFICE_AUDIO_CONTROL_CONFIGURATION = {
    'speakers': [
        SpeakerConfiguration("Kitchen speakers", 33, 47, 48, STANDARD_SOURCES),
        SpeakerConfiguration("Classroom speakers", 35, 51, 52, STANDARD_SOURCES),
    ]
}

logger = logging.getLogger(__name__)


async def async_setup_entry(_hass: HomeAssistant, entry, async_add_entities):
    # Extract stored runtime data
    runtime_data: RuntimeData = entry.runtime_data
    device = runtime_data.device

    # Add entities for each speaker
    for speaker_configuration in OFFICE_AUDIO_CONTROL_CONFIGURATION["speakers"]:
        async_add_entities([SpeakerEntity(speaker_configuration, device)])


class YamahaDspEntity(MediaPlayerEntity):
    def __init__(self, device: YamahaDspDevice):
        self._device = device


class SpeakerEntity(YamahaDspEntity):
    def __init__(self, config: SpeakerConfiguration, device: YamahaDspDevice):
        super().__init__(device)
        self._config = config

    _attr_supported_features = (
            MediaPlayerEntityFeature.VOLUME_MUTE |
            MediaPlayerEntityFeature.VOLUME_SET |
            MediaPlayerEntityFeature.SELECT_SOURCE
    )

    @property
    def name(self) -> str:
        return self._config.name
