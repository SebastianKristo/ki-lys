<p align="center">
  <img src="https://raw.githubusercontent.com/SebastianKristo/ki-lys/main/brand/logo.svg" width="120" alt="KI Lys">
</p>

<h1 align="center">KI Lys</h1>

<p align="center">
  Lysscener per rom, laget automatisk. Velg rommene – resten finner integrasjonen selv.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/HACS-egendefinert-orange.svg">
  <img src="https://img.shields.io/badge/Home%20Assistant-2024.6%2B-41BDF5.svg">
  <img src="https://img.shields.io/badge/versjon-1.0.0-brightgreen.svg">
</p>

---

## Hvorfor

Sju scener i ti rom blir sytti skript å skrive og vedlikeholde. Denne integrasjonen lager dem i stedet: den
leser hvilke lys som hører til hvert rom, gir hvert lys en rolle ut fra navnet, og bruker rollene til å sette
lysstyrke og fargetemperatur per scene.

## Scenene

| Scene | Hva skjer |
|---|---|
| **Maks lys** | Alt på fullt, kjølig hvitt |
| **Komfort** | Taklys dempet, lamper varme – hverdagslyset |
| **Middag** | Taklys ned til 45 %, stemningslys opp, arbeidslys av |
| **TV-kveld** | Taklys av, lamper svakt, stemningslys 55 % i 2200 K |
| **Mindre lys** | Alt ned på rundt en fjerdedel |
| **Nattmodus** | Alt av bortsett fra nattlys på 8 % |
| **Alt av** | Alt av |

Du velger selv hvilke av dem som skal lages, og kan legge til egne.

## Rollene

Hvert lys får en rolle ut fra navnet sitt:

| Rolle | Gjenkjennes på | Eksempel |
|---|---|---|
| **tak** | tak, ceiling, spot, downlight, himling | `light.stue_taklys` |
| **lampe** | lampe, bord, pendel, vegg | `light.bordlampe` |
| **stemning** | stripe, strip, led, hylle, skap, gulv, vindu, wled | `light.tv_benk_stripe` |
| **arbeid** | pult, benk, skrivebord, speil | `light.kjokkenbenk` |
| **nattlys** | natt, nattlampe, seng – eller valgt i oppsettet | `light.nattlampe` |

Stemmer ikke gjetningen, legger du lyset inn som nattlys i oppsettet, eller velger det bort helt.

## Installasjon

1. HACS → tre prikker → *Egendefinerte repositorier* → `https://github.com/SebastianKristo/ki-lys`, type **Integration**
2. Installer **KI Lys** og start Home Assistant på nytt
3. Innstillinger → Enheter og tjenester → *Legg til integrasjon* → **KI Lys**

## Oppsett

| Felt | Betydning |
|---|---|
| **Rom** | Områdene som skal få scener. Lysene finnes automatisk |
| **Lys som ikke skal være med** | For eksempel utelys eller en projektorlampe |
| **Lys som får stå på i nattmodus** | Overstyrer rollegjetningen |
| **Scener som skal lages** | Huk av de du vil ha |
| **Overgang** | Sekunder på dimmingen, standard 2 |

## Entiteter

| Entitet | Gjør |
|---|---|
| `button.<rom>_lys_<scene>` | Setter scenen i det rommet |
| `sensor.<rom>_lys_oversikt` | Antall lys på nå, med roller og scener som attributter |
| `switch.<rom>_lys_alle` | På setter Komfort, av slår alt av |

## Tjenester

```yaml
# Ett rom
action: ki_lys.sett
data: {scene: tv, rom: stue}

# Hele huset
action: ki_lys.sett
data: {scene: natt}

# Etter at du har lagt til nye lys
action: ki_lys.les_rom
```

## Egne scener

Options → *Egne scener* → *Legg til en scene*. Du setter lysstyrke per rolle og en fargetemperatur, og
scenen dukker opp som knapp i alle rommene. Vil du heller peke på en scene du har fra før, velger du den i
feltet nederst – da brukes den i stedet.

## Kortet

`ki-rom-card` i [ki-cards](https://github.com/SebastianKristo/ki-cards) plukker opp scenene automatisk og
viser dem i Scener-raden for hvert rom, sammen med skriptene og scenene du har fra før.
`lysscener: false` i kortet slår det av.
