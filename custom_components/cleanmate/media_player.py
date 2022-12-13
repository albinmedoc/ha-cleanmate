"""Support for Cleanmate Vaccums."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(DOMAIN)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Cleanmate vacuums."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    device = config["device"]

    media_players = [MediaPlayer(device, "Volume")]  # Change name

    _LOGGER.debug("Adding Cleanmate media players to Home Assistant: %s", media_players)
    async_add_entities(media_players)


class MediaPlayer(MediaPlayerEntity):
    def __init__(self, device, name) -> None:
        """Initialize the Cleanmate vacuum cleaner"""
        self.device = device
        self.device.update_state()

    @property
    def state(self) -> MediaPlayerState:
        """State of the media player."""
        return MediaPlayerState.ON

    @property
    def volume_level(self) -> float:
        """Volume level of the media player (0..1)."""
        return self.device.volume / 100.0

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag vacuum cleaner features that are supported."""
        return MediaPlayerEntityFeature.VOLUME_SET

    def set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        self.device.set_volume(volume * 100)
