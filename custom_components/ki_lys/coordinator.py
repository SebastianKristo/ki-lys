"""Motoren: finner lysene i hvert rom, gir dem en rolle, og setter scenene."""
from __future__ import annotations

import re
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar, entity_registry as er

from .const import (
    CONF_EGNE,
    CONF_EKSKLUDER,
    CONF_NATTLYS,
    CONF_OVERGANG,
    CONF_ROM,
    CONF_SCENER,
    DOMAIN,
    OPPSKRIFT,
    ROLLER,
    SCENER,
    STD_OVERGANG,
    STD_ROLLE,
    STD_SCENER,
)


class Rom:
    """Ett rom med lysene sine."""

    def __init__(self, area_id: str, navn: str) -> None:
        self.area_id = area_id
        self.navn = navn
        self.lys: list[str] = []

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9_]+", "_", self.navn.lower()).strip("_") or self.area_id


class LysMotor:
    """Leser rom og lys fra Home Assistant, og kjører scenene."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.rom: list[Rom] = []
        self._lyttere: list = []

    # ------------------------------------------------------------- oppsett
    @property
    def oppsett(self) -> dict[str, Any]:
        return {**self.entry.data, **self.entry.options}

    @property
    def overgang(self) -> int:
        return int(self.oppsett.get(CONF_OVERGANG) or STD_OVERGANG)

    @property
    def valgte_scener(self) -> list[str]:
        valgt = self.oppsett.get(CONF_SCENER) or STD_SCENER
        return [s for s in STD_SCENER if s in valgt]

    @property
    def egne(self) -> list[dict[str, Any]]:
        return list(self.oppsett.get(CONF_EGNE) or [])

    def les_rom(self) -> None:
        """Finner lysene i hvert valgte rom, minus de ekskluderte."""
        områder = ar.async_get(self.hass)
        reg = er.async_get(self.hass)
        ekskl = set(self.oppsett.get(CONF_EKSKLUDER) or [])
        self.rom = []
        for area_id in self.oppsett.get(CONF_ROM) or []:
            omr = områder.async_get_area(area_id)
            if omr is None:
                continue
            rom = Rom(area_id, omr.name)
            for e in er.async_entries_for_area(reg, area_id):
                if e.entity_id.startswith("light.") and not e.disabled_by and e.entity_id not in ekskl:
                    rom.lys.append(e.entity_id)
            # lys uten områdetilknytning, men på en enhet i rommet, tas også med
            for st in self.hass.states.async_all("light"):
                if st.entity_id in ekskl or st.entity_id in rom.lys:
                    continue
                oppf = reg.async_get(st.entity_id)
                if oppf and oppf.area_id == area_id:
                    rom.lys.append(st.entity_id)
            rom.lys.sort()
            if rom.lys:
                self.rom.append(rom)

    # --------------------------------------------------------------- roller
    def rolle(self, entity_id: str) -> str:
        """Hvilken rolle lyset spiller: tak, lampe, stemning, arbeid eller nattlys."""
        if entity_id in (self.oppsett.get(CONF_NATTLYS) or []):
            return "nattlys"
        st = self.hass.states.get(entity_id)
        navn = f"{entity_id} {(st.attributes.get('friendly_name') if st else '') or ''}".lower()
        for rolle, mønster in ROLLER:
            if re.search(mønster, navn):
                return rolle
        return STD_ROLLE

    def roller_i(self, rom: Rom) -> dict[str, list[str]]:
        ut: dict[str, list[str]] = {}
        for lys in rom.lys:
            ut.setdefault(self.rolle(lys), []).append(lys)
        return ut

    # ---------------------------------------------------------------- kjør
    async def sett(self, area_id: str, scene: str) -> None:
        """Setter en scene i ett rom."""
        rom = next((r for r in self.rom if r.area_id == area_id), None)
        if rom is None:
            return

        egen = next((e for e in self.egne if e.get("id") == scene), None)
        if egen:
            await self._kjor_egen(rom, egen)
            return

        oppskrift = OPPSKRIFT.get(scene)
        if oppskrift is None:
            return
        for lys in rom.lys:
            innstilling = oppskrift.get(self.rolle(lys))
            await self._sett_lys(lys, innstilling)

    async def _kjor_egen(self, rom: Rom, egen: dict[str, Any]) -> None:
        """Egen scene: enten faste verdier per rolle, eller en scene/skript."""
        if egen.get("scene"):
            await self.hass.services.async_call("scene", "turn_on", {"entity_id": egen["scene"]}, blocking=False)
            return
        if egen.get("skript"):
            domene, tjeneste = str(egen["skript"]).split(".", 1)
            await self.hass.services.async_call(domene, tjeneste, {}, blocking=False)
            return
        for lys in rom.lys:
            rolle = self.rolle(lys)
            verdi = (egen.get("roller") or {}).get(rolle)
            await self._sett_lys(lys, tuple(verdi) if verdi else None)

    async def _sett_lys(self, entity_id: str, innstilling: tuple[int, int] | None) -> None:
        if innstilling is None:
            await self.hass.services.async_call(
                "light", "turn_off", {"entity_id": entity_id, "transition": self.overgang}, blocking=False)
            return
        prosent, kelvin = innstilling
        data: dict[str, Any] = {
            "entity_id": entity_id,
            "brightness_pct": max(1, min(100, int(prosent))),
            "transition": self.overgang,
        }
        st = self.hass.states.get(entity_id)
        moduser = (st.attributes.get("supported_color_modes") or []) if st else []
        if "color_temp" in moduser:
            data["color_temp_kelvin"] = int(kelvin)
        await self.hass.services.async_call("light", "turn_on", data, blocking=False)

    async def sett_alle(self, scene: str) -> None:
        for rom in self.rom:
            await self.sett(rom.area_id, scene)

    # -------------------------------------------------------------- oversikt
    def scener(self) -> list[dict[str, Any]]:
        ut = [{"id": s, **SCENER[s]} for s in self.valgte_scener]
        for e in self.egne:
            ut.append({"id": e.get("id"), "navn": e.get("navn") or e.get("id"),
                       "ikon": e.get("ikon") or "mdi:lightbulb-group", "rekkefolge": 90})
        return sorted(ut, key=lambda x: x.get("rekkefolge", 50))

    def oversikt(self, rom: Rom) -> dict[str, Any]:
        roller = self.roller_i(rom)
        return {
            "rom": rom.navn, "area_id": rom.area_id, "slug": rom.slug,
            "lys": rom.lys, "roller": roller,
            "scener": [{**s, "entity": f"button.{rom.slug}_lys_{s['id']}"} for s in self.scener()],
            "antall_lys": len(rom.lys),
            "paa_naa": [x for x in rom.lys if (self.hass.states.get(x) or None) and self.hass.states.get(x).state == "on"],
        }
