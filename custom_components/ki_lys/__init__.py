"""KI Lys – lysscener per rom, laget automatisk."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN, PLATFORMS
from .coordinator import LysMotor


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    motor = LysMotor(hass, entry)
    motor.les_rom()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = motor
    if not motor.rom:
        # ved oppstart kan lysene komme etter oss – prøv igjen når alt er lastet
        async def _prov_igjen(_hendelse) -> None:
            motor.les_rom()
            if motor.rom:
                await hass.config_entries.async_reload(entry.entry_id)
        entry.async_on_unload(
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _prov_igjen))
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
    def finn_rom(m, rom: str | None):
        if not rom:
            return [r.area_id for r in m.rom]
        return [r.area_id for r in m.rom if rom in (r.area_id, r.navn, r.slug)]

    async def lagre_naa(call: ServiceCall) -> None:
        """Lagrer lysene slik de står nå som overstyring for scenen."""
        for m in motorer():
            for area_id in finn_rom(m, call.data.get("rom")):
                await m.lagre_naa(call.data["scene"], area_id)

    async def sett_lys(call: ServiceCall) -> None:
        """Overstyrer ett lys i én scene."""
        for m in motorer():
            await m.sett_lys(
                call.data["scene"], call.data["entity_id"],
                lysstyrke=call.data.get("lysstyrke"),
                paa=call.data.get("pa"),
                kelvin=call.data.get("kelvin"))

    async def legg_til_lys(call: ServiceCall) -> None:
        for m in motorer():
            await m.legg_til_lys(call.data["scene"], call.data["entity_id"])

    async def fjern_lys(call: ServiceCall) -> None:
        for m in motorer():
            await m.fjern_lys(call.data["scene"], call.data["entity_id"])

    async def nullstill(call: ServiceCall) -> None:
        """Fjerner overstyringene for en scene, så rollene gjelder igjen."""
        for m in motorer():
            alle = dict(m.oppsett.get("overstyr") or {})
            alle.pop(call.data["scene"], None)
            m._lagre({"overstyr": alle})

    scene_felt = {vol.Required("scene"): str}
    hass.services.async_register(DOMAIN, "lagre_naa", lagre_naa, schema=vol.Schema({
        **scene_felt, vol.Optional("rom"): str}))
    hass.services.async_register(DOMAIN, "sett_lys", sett_lys, schema=vol.Schema({
        **scene_felt,
        vol.Required("entity_id"): str,
        vol.Optional("lysstyrke"): vol.Coerce(int),
        vol.Optional("pa"): bool,
        vol.Optional("kelvin"): vol.Coerce(int),
    }))
    hass.services.async_register(DOMAIN, "legg_til_lys", legg_til_lys, schema=vol.Schema({
        **scene_felt, vol.Required("entity_id"): str}))
    hass.services.async_register(DOMAIN, "fjern_lys", fjern_lys, schema=vol.Schema({
        **scene_felt, vol.Required("entity_id"): str}))
    hass.services.async_register(DOMAIN, "nullstill", nullstill, schema=vol.Schema(scene_felt))
    hass.services.async_register(DOMAIN, "les_rom", les_rom)
