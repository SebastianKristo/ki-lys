"""Felles grunnlag for entitetene: én enhet per rom."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


class LysEntitet(Entity):
    _attr_has_entity_name = False
    _attr_should_poll = False

    def __init__(self, motor, rom, nøkkel: str, navn: str) -> None:
        self.motor = motor
        self.rom = rom
        self._attr_unique_id = f"{motor.entry.entry_id}_{rom.area_id}_{nøkkel}"
        self._attr_name = f"{rom.navn} {navn}"
        self.entity_id = f"{self.platform_domene}.{rom.slug}_lys_{nøkkel}"

    platform_domene = "sensor"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.motor.entry.entry_id}_{self.rom.area_id}")},
            name=f"Lys {self.rom.navn}",
            manufacturer="KI",
            model="Lysscener",
        )
