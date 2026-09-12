## Rettet

**1.0.1**
- Ingen entiteter ble opprettet. Integrasjonen spurte bare etter lys som har området satt på **entiteten**, men de fleste lys arver området fra **enheten** sin – da så den ingen lys, og uten lys lages det ingen knapper. Nå slås området opp på entiteten først og enheten etterpå
- Er et rom tomt ved oppstart – for eksempel fordi lysintegrasjonen laster senere – prøver KI Lys på nytt når Home Assistant er ferdig startet
- Rom med tomme lyslister skriver nå en linje i loggen så det er lett å se hva som mangler
- Romnavn med æ, ø og å gir penere entitets-id-er: «Kjøkken» blir `kjokken`, ikke `kj_kken`

## Fra 1.0.0

Lysscener per rom, laget automatisk: velg rom, lysene finnes fra områdene, og hvert lys får rolle (tak, lampe, stemning, arbeid, nattlys) ut fra navnet. Sju scener per rom, egne scener i oppsettet.
