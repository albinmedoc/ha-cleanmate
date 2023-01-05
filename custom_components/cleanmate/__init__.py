"""The Cleanmate integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST
from .const import DOMAIN, CONF_AUTH_CODE
from .devices.vacuum import CleanmateVacuum

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS: list[str] = ["vacuum", "number"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cleanmate from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = dict(entry.data)

    config = dict(entry.data)
    host = config[CONF_HOST]
    auth_code = config[CONF_AUTH_CODE]

    device = CleanmateVacuum(host, auth_code)

    hass.data[DOMAIN][entry.entry_id]['device'] = device
    
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, 'vacuum')
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, 'number')
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok