"""KI Lys – lysscener per rom, laget automatisk."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN, PLATFORMS
from .coordinator import LysMotor


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    motor = LysMotor(hass, entry)
    motor.les_rom()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = motor
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_oppdatert))
    _tjenester(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok


async def _oppdatert(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _tjenester(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, "sett"):
        return

    def motorer() -> list[LysMotor]:
        return list(hass.data.get(DOMAIN, {}).values())

    async def sett(call: ServiceCall) -> None:
        """Setter en scene – i ett rom, eller i alle."""
        scene = call.data["scene"]
        rom = call.data.get("rom")
        for m in motorer():
            if rom:
                for r in m.rom:
                    if rom in (r.area_id, r.navn, r.slug):
                        await m.sett(r.area_id, scene)
            else:
                await m.sett_alle(scene)

    async def les_rom(_call: ServiceCall) -> None:
        """Leser rom og lys på nytt, uten omstart."""
        for m in motorer():
            m.les_rom()

    hass.services.async_register(DOMAIN, "sett", sett, schema=vol.Schema({
        vol.Required("scene"): str,
        vol.Optional("rom"): str,
    }))
    hass.services.async_register(DOMAIN, "les_rom", les_rom)
