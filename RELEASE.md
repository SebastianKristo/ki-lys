## Nytt

**1.1.0 – overstyr enkeltlys**

- Options → *Overstyr lys i en scene*: en glidebryter per lys. **−1** lar rollen bestemme, **0** slår lyset av, **1–100** setter fast lysstyrke
- **«Ikke med i denne scenen»** lar et lys stå helt urørt når scenen settes, og **«Lys i tillegg»** tar med lys fra andre rom
- `ki_lys.lagre_naa` leser lysene slik de står akkurat nå og lagrer dem som overstyring – sett lyset som du vil ha det, og lagre
- `ki_lys.sett_lys`, `ki_lys.legg_til_lys`, `ki_lys.fjern_lys` og `ki_lys.nullstill` gjør det samme fra automasjoner

Overstyringene lagres i options, uten at integrasjonen lastes på nytt. Egne scener følger de samme reglene.

## Fra 1.0.1

Områdeoppslaget leser nå både entitetens og enhetens område – uten det ble det ikke laget entiteter i det hele tatt.
