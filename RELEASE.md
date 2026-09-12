## Første utgave

**KI Lys** lager lysscener per rom, uten at du skriver skript.

- Velg rommene – lysene finnes automatisk fra områdene i Home Assistant
- Hvert lys får en rolle ut fra navnet: tak, lampe, stemning, arbeid eller nattlys
- Sju scener lages per rom: Maks lys, Komfort, Middag, TV-kveld, Mindre lys, Nattmodus og Alt av. Du velger hvilke du vil ha
- Egne scener legges til i oppsettet, med lysstyrke per rolle – eller ved å peke på en scene du har fra før
- Entiteter: `button.<rom>_lys_<scene>`, `sensor.<rom>_lys_oversikt` og `switch.<rom>_lys_alle`
- Tjenester: `ki_lys.sett` (ett rom eller alle) og `ki_lys.les_rom`

`ki-rom-card` 1.12.0 plukker opp scenene automatisk og viser dem i Scener-raden per rom.
