"""Felles navn og standardverdier for KI Lys."""
from __future__ import annotations

DOMAIN = "ki_lys"
PLATFORMS = ["button", "sensor", "switch"]

CONF_ROM = "rom"                  # liste med area_id
CONF_EKSKLUDER = "ekskluder"      # lys som ikke skal være med
CONF_SCENER = "scener"            # hvilke scener som lages
CONF_EGNE = "egne"                # egne scener lagt til manuelt
CONF_OVERGANG = "overgang"        # sekunder på dimmingen
CONF_NATTLYS = "nattlys"          # lys som får stå på i nattmodus

STD_OVERGANG = 2

ATTR_INTEGRASJON = "integrasjon"
ATTR_TYPE = "ki_type"

# Scenene som lages automatisk. rekkefølgen er den kortet viser dem i.
SCENER: dict[str, dict] = {
    "maks": {"navn": "Maks lys", "ikon": "mdi:lightbulb-on", "rekkefolge": 1},
    "komfort": {"navn": "Komfort", "ikon": "mdi:sofa", "rekkefolge": 2},
    "middag": {"navn": "Middag", "ikon": "mdi:silverware-fork-knife", "rekkefolge": 3},
    "tv": {"navn": "TV-kveld", "ikon": "mdi:television-classic", "rekkefolge": 4},
    "mindre": {"navn": "Mindre lys", "ikon": "mdi:lightbulb-on-40", "rekkefolge": 5},
    "natt": {"navn": "Nattmodus", "ikon": "mdi:weather-night", "rekkefolge": 6},
    "av": {"navn": "Alt av", "ikon": "mdi:lightbulb-off", "rekkefolge": 7},
}

STD_SCENER = list(SCENER)

# Hvor kraftig hver rolle lyser i hver scene: (lysstyrke i %, fargetemperatur i kelvin).
# None betyr at lyset slås av.
OPPSKRIFT: dict[str, dict[str, tuple[int, int] | None]] = {
    "maks":    {"tak": (100, 4000), "lampe": (100, 3500), "stemning": (100, 3000), "arbeid": (100, 4000), "nattlys": (60, 2200)},
    "komfort": {"tak": (60, 2900),  "lampe": (70, 2700),  "stemning": (80, 2400),  "arbeid": (70, 3500),  "nattlys": (40, 2200)},
    "middag":  {"tak": (45, 2700),  "lampe": (60, 2500),  "stemning": (75, 2300),  "arbeid": None,        "nattlys": (30, 2200)},
    "tv":      {"tak": None,        "lampe": (25, 2300),  "stemning": (55, 2200),  "arbeid": None,        "nattlys": (25, 2200)},
    "mindre":  {"tak": (25, 2500),  "lampe": (30, 2400),  "stemning": (35, 2300),  "arbeid": (30, 2700),  "nattlys": (20, 2200)},
    "natt":    {"tak": None,        "lampe": None,        "stemning": None,        "arbeid": None,        "nattlys": (8, 2200)},
    "av":      {"tak": None,        "lampe": None,        "stemning": None,        "arbeid": None,        "nattlys": None},
}

# Nøkkelord som avgjør hvilken rolle et lys får.
ROLLER: list[tuple[str, str]] = [
    ("nattlys", r"natt|nightlight|nattlampe|seng"),
    # «benk» alene treffer også «tv_benk», derfor bare de sammensatte formene
    ("arbeid",  r"pult|kjokkenbenk|kjøkkenbenk|arbeidsbenk|benkebelysning|arbeid|skrivebord|speil|desk"),
    ("stemning", r"stripe|strip|led|list|bak|hylle|skap|gulv|vindu|stemning|ambient|wled"),
    ("lampe",   r"lampe|bord|gulvlampe|pendel|vegg|lamp"),
    ("tak",     r"tak|ceiling|spot|downlight|himling"),
]
STD_ROLLE = "lampe"
