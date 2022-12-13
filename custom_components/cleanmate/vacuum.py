"""Support for Cleanmate Vaccums."""
import logging
from typing import Any

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,
    STATE_IDLE,
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_RETURNING,
    STATE_PAUSED,
    STATE_ERROR,
)

from homeassistant.helpers.icon import icon_for_battery_level

from .const import DOMAIN
from .devices.vacuum import WorkMode, WorkState

_LOGGER = logging.getLogger(DOMAIN)

async def async_setup_platform(hass, config_entry, async_add_entities, discoveryInfo=None):
    """Set up the Cleanmate vacuums."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    device = config['device']

    vacuums = [Vacuum(device, 'Robotdammsugare')] # Change name

    _LOGGER.debug("Adding Cleanmate Vacuums to Home Assistant: %s", vacuums)
    async_add_entities(vacuums)


async def async_setup_entry(hass, config_entry, async_add_entities):
    await async_setup_platform(hass, config_entry, async_add_entities)

class Vacuum(StateVacuumEntity):

    fan_speed_map = {
        "intensive": WorkMode.Intensive,
        "standard": WorkMode.Standard,
        "silent": WorkMode.Silent,
    }

    def __init__(self, device, name) -> None:
        """Initialize the Cleanmate vacuum cleaner"""
        self.device = device
        self.device.connect()
        self.device.update_state()

        self._attr_name = name
        self._attr_fan_speed = None
        self._attr_error = None
    
    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.name)},
            "name": "Cleanmate vacuum",
            "manufacturer": "Cleanmate"
        }

    @property
    def state(self) -> str | None:
        """Return the state of the vacuum cleaner."""
        match self.device.work_state:
            case WorkState.Cleaning:
                return STATE_CLEANING
            case WorkState.Charging:
                return STATE_DOCKED
            case WorkState.Idle:
                if(self.device_has_work):
                    return STATE_PAUSED
                return STATE_IDLE
            case WorkState.Problem:
                return STATE_ERROR
            case _:
                _LOGGER.debug('Unkown work_state', self.device.work_state)
                return STATE_DOCKED

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the vacuum cleaner."""
        return self.device.battery_level

    @property
    def battery_icon(self) -> str:
        """Return the battery icon for the vacuum cleaner."""
        return icon_for_battery_level(
            battery_level=self.battery_level, charging=self.device.work_state == WorkState.Charging
        )

    @property
    def fan_speed(self) -> str | None:
        """Return the fan speed of the vacuum cleaner."""
        match self.device.work_mode:
            case WorkMode.Intensive:
                return "intensive"
            case WorkMode.Standard:
                return "standard"
            case WorkMode.Silent:
                return "silent"
            case _:
                return "standard"

    @property
    def fan_speed_list(self) -> list[str]:
        """Get the list of available fan speed steps of the vacuum cleaner."""
        return [
            "intensive",
            "standard",
            "silent",
        ]

    @property
    def supported_features(self) -> VacuumEntityFeature:
        """Flag vacuum cleaner features that are supported."""
        return (
            VacuumEntityFeature.PAUSE
            | VacuumEntityFeature.STOP
            | VacuumEntityFeature.RETURN_HOME
            | VacuumEntityFeature.FAN_SPEED
            | VacuumEntityFeature.BATTERY
            | VacuumEntityFeature.LOCATE
            | VacuumEntityFeature.STATE
            | VacuumEntityFeature.STATUS
            | VacuumEntityFeature.START
        )
    
    @property
    def extra_state_attributes(self):
        """Return the state attributes of the vacuum cleaner."""
        pass

    def return_to_base(self, **kwargs: Any) -> None:
        """Set the vacuum cleaner to return to the dock."""
        self.device.charge()

    def start(self, **kwargs: Any) -> None:
        """Start the vacuum cleaner."""
        self.device.start()
        self.device.update_state()

    def stop(self, **kwargs: Any) -> None:
        """Stop the vacuum cleaner."""
        self.device.stop()
    
    def pause(self, **kwargs: Any) -> None:
        """Stop the vacuum cleaner."""
        self.device.pause()

    def locate(self, **kwargs: Any) -> None:
        """Locate the vacuum cleaner."""
        self.device.find()

    def set_fan_speed(self, fan_speed: str, **kwargs: Any) -> None:
        """Set fan speed."""
        work_mode = self.fan_speed_map[fan_speed]
        self.start(work_mode)

    def update(self) -> None:
        """Update state of the vacuum cleaner."""
        self.device.update_state()