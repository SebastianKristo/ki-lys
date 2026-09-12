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
    CONF_NATTLYS,
    CONF_OVERGANG,
    CONF_ROM,
    CONF_SCENER,
    DOMAIN,
    SCENER,
    STD_OVERGANG,
    STD_SCENER,
)


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

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return self.async_show_menu(step_id="init", menu_options=["innstillinger", "scener"])

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
