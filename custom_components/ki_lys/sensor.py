"""Oversiktssensor per rom – alt kortet trenger ligger i attributtene."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import ATTR_INTEGRASJON, ATTR_TYPE, DOMAIN
from .entity import LysEntitet


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback) -> None:
    motor = hass.data[DOMAIN][entry.entry_id]
    add([Oversikt(motor, rom) for rom in motor.rom])


class Oversikt(LysEntitet, SensorEntity):
    platform_domene = "sensor"
    _attr_icon = "mdi:lightbulb-group"

    def __init__(self, motor, rom) -> None:
        super().__init__(motor, rom, "oversikt", "lysscener")

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_track_state_change_event(
            self.hass, self.rom.lys, self._endret))

    @callback
    def _endret(self, _hendelse) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        return len([x for x in self.rom.lys
                    if (st := self.hass.states.get(x)) and st.state == "on"])

    @property
    def extra_state_attributes(self) -> dict:
        return {ATTR_INTEGRASJON: DOMAIN, ATTR_TYPE: "oversikt", **self.motor.oversikt(self.rom)}
