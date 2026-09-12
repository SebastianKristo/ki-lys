## Nytt

**2.0.0 – julelys**

- Options → *Julelys*: velg julelysene og sett sesongdatoene. Lysene grupperes automatisk i julestjerner, julestaker og utendørs ut fra navnet
- `sensor.ki_jul_nedtelling` teller ned – til sesongstart før 1. november, til julaften i sesongen, og til sesongslutt etter julaften. Attributtene har fase, framdrift i prosent, gruppene og alle lysene, klare for kortet
- `sensor.ki_jul_tent`, `switch.ki_jul_sesong`, `binary_sensor.ki_jul_i_sesong` og knappene `button.ki_jul_alle_pa` / `_alle_av`
- Erstatter nedtellingssensoren, tellingen av tente lys og av/på-skriptene i den gamle jule-pakken

Bruk sammen med `ki-jul-card` i ki-cards 3.2.0, som beholder designet fra julepopupen.

## Fra 1.3.0

Soner som slår flere rom sammen, scener per rom, og overstyring per lys.
