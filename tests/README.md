# Tesztek

## `ledger_test.js` — buli-könyvelés füstteszt

Végigjátssza az összes játékot, és összeveti, amit az **eredmény-banner ígér**
(`onResult`: ki nyert, ki iszik, „+1 pont") azzal, amit a játék ténylegesen
**átad a buli állásának** (`onAdvance`: pont- és kortytérkép).

Ez a hibafajta nem dob hibaüzenetet és nem látszik a képernyőn — csak az lesz
belőle, hogy a buli végén 0 pont áll valakinél, akinek nyernie kellett volna.
Három ilyen hiba került elő a v10.105–v10.109 körül:

- a head-to-head adat rossz mezőnévre íródott (soha nem jelent meg),
- az Időpárbaj és az Útvesztő győztese nem kapott pontot,
- a Beer Pong pontjai és kortyai eldobódtak a buli lezárásánál.

### Futtatás

```bash
node tests/ledger_test.js            # mind a 45 játék (~20 perc)
node tests/ledger_test.js zene rulett  # csak a felsoroltak
```

Előfeltétel: `index.html` (buildelt), Playwright + Chromium.
A Firestore-t a `fbstub.js` memóriában emulálja — nincs hálózat.

Kilépési kód `1`, ha bármelyik játéknál eltér a banner és a könyvelés.

### Kimenet

- `✓ OK` — a banner és a könyvelés egyezik
- `✗ HIBA` — eltérés vagy konzolhiba (ez a lényeg)
- `– NEM_JATSZHATO` — a generikus driver nem tudta végigjátszani, **nem** azt
  jelenti, hogy jó. Ezekhez saját driver kell:
  - *timing/ügyességi*: `ticktak`, `reakcio`, `szamsor`, `ritmus`, `tapper`,
    `memoria`, `utveszto`, `cardbattle` (drag&drop)
  - *több fázisú / lobbys*: `busz`, `blackjack`, `powerhour`, `loverseny`
  - *csak online szobában*: `ovfj`
  - `beerpong` — külön, teljes lefedettséggel: lásd a Beer Pong teszteket

### Hogyan működik

A valódi `GameContent` komponenst mountolja a játék id-jával, és egy generikus
driverrel klikkel: ismerős gombfeliratok prioritási sorrendben → ha a képernyő
szövege két kattintás után sem változik, rács-cellákra vált (Collect, Memória
típusú pályák). Ha `onAdvance` megérkezett, kiértékel.

## `fbstub.js` — memóriabeli Firestore

A compat SDK-t utánozza annyira, hogy a valódi hibák reprodukálódjanak.
Fontos: a `set()` a pontot **szó szerinti mezőnévnek** veszi (mint az éles
Firestore), csak az `update()` értelmezi mezőútként — pont ez a különbség
rejtette el a head-to-head hibát.
