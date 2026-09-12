"""Oppsett: velg rom, velg bort lys, og eventuelt egne scener."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_EGNE,
    CONF_EKSKLUDER,
    CONF_EKSTRA_LYS,
    CONF_NATTLYS,
    CONF_OVERGANG,
    CONF_OVERSTYR,
    CONF_ROM,
    CONF_SCENER,
    CONF_UTELAT,
    DOMAIN,
    FOLG_ROLLEN,
    SCENER,
    STD_OVERGANG,
    STD_SCENER,
)


def _felt(entity_id: str) -> str:
    """Entitets-id som feltnavn i skjemaet."""
    return "lys_" + entity_id.replace(".", "__")


def _skjema(d: dict[str, Any]) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_ROM, default=d.get(CONF_ROM, [])): selector.AreaSelector(
            selector.AreaSelectorConfig(multiple=True)),
        vol.Optional(CONF_EKSKLUDER, default=d.get(CONF_EKSKLUDER, [])): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="light", multiple=True)),
        vol.Optional(CONF_NATTLYS, default=d.get(CONF_NATTLYS, [])): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="light", multiple=True)),
        vol.Optional(CONF_SCENER, default=d.get(CONF_SCENER, STD_SCENER)): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[{"value": k, "label": v["navn"]} for k, v in SCENER.items()],
                multiple=True, mode="list")),
        vol.Optional(CONF_OVERGANG, default=d.get(CONF_OVERGANG, STD_OVERGANG)): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=15, step=1, unit_of_measurement="s", mode="box")),
    })


class KiLysConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="KI Lys", data=user_input)
        return self.async_show_form(step_id="user", data_schema=_skjema({}))

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return KiLysOptionsFlow(entry)


class KiLysOptionsFlow(OptionsFlow):
    def __init__(self, entry: ConfigEntry) -> None:
        self.entry = entry
        self._egne: list[dict[str, Any]] = list({**entry.data, **entry.options}.get(CONF_EGNE) or [])
        self._scene: str = "komfort"

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return self.async_show_menu(step_id="init",
                                    menu_options=["innstillinger", "scener", "overstyr"])

    # --------------------------------------------------- overstyring per lys
    async def async_step_overstyr(self, user_input: dict[str, Any] | None = None):
        """Velg scenen du vil justere."""
        if user_input is not None:
            self._scene = user_input["scene"]
            return await self.async_step_lys()
        d = {**self.entry.data, **self.entry.options}
        valgte = d.get(CONF_SCENER) or list(SCENER)
        alternativer = [{"value": k, "label": SCENER[k]["navn"]} for k in SCENER if k in valgte]
        alternativer += [{"value": e["id"], "label": e.get("navn") or e["id"]} for e in self._egne]
        return self.async_show_form(step_id="overstyr", data_schema=vol.Schema({
            vol.Required("scene"): selector.SelectSelector(
                selector.SelectSelectorConfig(options=alternativer, mode="list")),
        }))

    async def async_step_lys(self, user_input: dict[str, Any] | None = None):
        """Sett lysstyrke per lys, og velg hvilke lys som er med."""
        motor = next(iter(self.hass.data.get(DOMAIN, {}).values()), None)
        scene = self._scene
        d = {**self.entry.data, **self.entry.options}
        i_rom: list[str] = []
        for rom in (motor.rom if motor else []):
            i_rom.extend(rom.lys)
        utelat_na = (d.get(CONF_UTELAT) or {}).get(scene) or []
        ekstra_na = (d.get(CONF_EKSTRA_LYS) or {}).get(scene) or []
        alle_lys = sorted(set(i_rom) | set(ekstra_na))
        overstyr = dict((d.get(CONF_OVERSTYR) or {}).get(scene) or {})

        if user_input is not None:
            nytt = dict(d.get(CONF_OVERSTYR) or {})
            rad: dict[str, Any] = {}
            for lys in alle_lys:
                verdi = user_input.get(_felt(lys))
                if verdi is None or int(verdi) == FOLG_ROLLEN:
                    continue
                rad[lys] = {"paa": int(verdi) > 0, "lysstyrke": int(verdi)}
            nytt[scene] = rad
            utelat = {k: list(v) for k, v in (d.get(CONF_UTELAT) or {}).items()}
            ekstra = {k: list(v) for k, v in (d.get(CONF_EKSTRA_LYS) or {}).items()}
            utelat[scene] = list(user_input.get("utelat") or [])
            ekstra[scene] = [x for x in (user_input.get("ekstra") or []) if x not in i_rom]
            return self.async_create_entry(title="", data={
                **{k: v for k, v in d.items() if k not in (CONF_OVERSTYR, CONF_UTELAT, CONF_EKSTRA_LYS)},
                CONF_OVERSTYR: nytt, CONF_UTELAT: utelat, CONF_EKSTRA_LYS: ekstra, CONF_EGNE: self._egne,
            })

        felt: dict[Any, Any] = {}
        for lys in alle_lys:
            o = overstyr.get(lys) or {}
            std = o.get("lysstyrke", 0 if o.get("paa") is False else FOLG_ROLLEN)
            felt[vol.Optional(_felt(lys), default=std, description={"suggested_value": std})] = \
                selector.NumberSelector(selector.NumberSelectorConfig(
                    min=FOLG_ROLLEN, max=100, step=1, mode="slider"))
        felt[vol.Optional("utelat", default=utelat_na)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="light", multiple=True))
        felt[vol.Optional("ekstra", default=ekstra_na)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="light", multiple=True))
        return self.async_show_form(
            step_id="lys", data_schema=vol.Schema(felt),
            description_placeholders={"scene": SCENER.get(scene, {}).get("navn", scene)})

    async def async_step_innstillinger(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data={**user_input, CONF_EGNE: self._egne})
        d = {**self.entry.data, **self.entry.options}
        return self.async_show_form(step_id="innstillinger", data_schema=_skjema(d))

    # ------------------------------------------------------------ egne scener
    async def async_step_scener(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            valg = user_input["valg"]
            if valg == "ny":
                return await self.async_step_ny()
            if valg.startswith("slett:"):
                navn = valg.split(":", 1)[1]
                self._egne = [e for e in self._egne if e.get("id") != navn]
                return self._lagre()
        alternativer = [{"value": "ny", "label": "Legg til en scene"}]
        alternativer += [{"value": f"slett:{e['id']}", "label": f"Slett «{e.get('navn') or e['id']}»"}
                         for e in self._egne]
        return self.async_show_form(step_id="scener", data_schema=vol.Schema({
            vol.Required("valg"): selector.SelectSelector(
                selector.SelectSelectorConfig(options=alternativer, mode="list")),
        }))

    async def async_step_ny(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            scene = {
                "id": user_input["navn"].lower().replace(" ", "_"),
                "navn": user_input["navn"],
                "ikon": user_input.get("ikon") or "mdi:lightbulb-group",
                "roller": {
                    "tak": [user_input["tak"], user_input["kelvin"]] if user_input["tak"] else None,
                    "lampe": [user_input["lampe"], user_input["kelvin"]] if user_input["lampe"] else None,
                    "stemning": [user_input["stemning"], user_input["kelvin"]] if user_input["stemning"] else None,
                    "arbeid": [user_input["arbeid"], user_input["kelvin"]] if user_input["arbeid"] else None,
                    "nattlys": [user_input["nattlys"], 2200] if user_input["nattlys"] else None,
                },
            }
            if user_input.get("scene"):
                scene["scene"] = user_input["scene"]
            self._egne = [e for e in self._egne if e["id"] != scene["id"]] + [scene]
            return self._lagre()

        prosent = selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=100, step=5, unit_of_measurement="%", mode="slider"))
        return self.async_show_form(step_id="ny", data_schema=vol.Schema({
            vol.Required("navn"): str,
            vol.Optional("ikon", default="mdi:lightbulb-group"): selector.IconSelector(),
            vol.Optional("tak", default=50): prosent,
            vol.Optional("lampe", default=60): prosent,
            vol.Optional("stemning", default=70): prosent,
            vol.Optional("arbeid", default=0): prosent,
            vol.Optional("nattlys", default=0): prosent,
            vol.Optional("kelvin", default=2700): selector.NumberSelector(
                selector.NumberSelectorConfig(min=2000, max=6500, step=100, unit_of_measurement="K", mode="box")),
            vol.Optional("scene"): selector.EntitySelector(selector.EntitySelectorConfig(domain="scene")),
        }))

    def _lagre(self):
        d = {**self.entry.data, **self.entry.options}
        d[CONF_EGNE] = self._egne
        return self.async_create_entry(title="", data={k: v for k, v in d.items() if k not in ("title",)})
