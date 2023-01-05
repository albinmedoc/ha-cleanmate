"""Support for Cleanmate Vaccums."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.components.number import (
    NumberEntity,
    NumberMode
)

from .const import DOMAIN
from .devices.vacuum import CleanmateVacuum

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Cleanmate vacuums."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    device = config["device"]

    numberEntities = [CleanmateVolume(device, "Volume")]  # Change name

    _LOGGER.debug("Adding Cleanmate number entity to Home Assistant: %s", numberEntities)
    async_add_entities(numberEntities)


class CleanmateVolume(NumberEntity):
    """Volume level for Cleanmate vacuum cleaner"""

    def __init__(self, device: CleanmateVacuum, name) -> None:
        """Initialize the Cleanmate vacuum cleaner"""
        self.device = device
        self.device.update_state()
    
    @property
    def mode(self) -> int:
        """Input mode."""
        return NumberMode.SLIDER

    @property
    def native_max_value(self) -> int:
        """Volume max level."""
        return 100
    
    @property
    def native_min_value(self) -> int:
        """Volume min level."""
        return 0

    @property
    def native_step(self) -> int:
        """Volume step."""
        return 10

    @property
    def native_value(self) -> int:
        """Volume step."""
        if self.device.volume:
            return self.device.volume
        return 0
    
    async def async_set_native_value(self, value: float) -> None:
        """Set volume level."""
        await self.device.set_volume(value)
