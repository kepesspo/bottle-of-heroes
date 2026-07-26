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
  jelenti, hogy jó. Ezekhez saját driver kell (`DRIVERS` a fájl elején).
- `– CSAK_ONLINE` — offline el sem indul, online szoba kell hozzá. Egy ilyen
  van: `ovfj` (Ország-Város — a játékosok a telefonjukon írnak és szavaznak).

### Saját driverek (`DRIVERS`)

Minden korábban lefedetlen játéknak van már forgatókönyve:

| játék | amit a driver megold |
|---|---|
| `utveszto` | csapdalerakás → átadás → útvonalrajzolás → feltárás-animáció |
| `loverseny` | 4 fogadás külön lóra → Rajt → a nyertes szétosztja a nyereményt |
| `szamsor` | 1..9 sorban — a számok `cursor:pointer` divek, nem gombok |
| `reakcio` | polling, amíg a mező zöldre vált (háttérszín-figyelés) |
| `memoria` | felfordított lapok memorizálása, ismert párok kijátszása |
| `beerpong` | meccsről meccsre 3–0, majd a torna lezárása |
| `blackjack` | osztás → Stand → Kiszáll (élő korty, `onLiveDrinkUpdate`) |
| `busz` | piramis → buszra szállás → K/N tippek, korty-overlay zárása |
| `ticktak` | indítás → várakozás a 15–45 mp-es véletlen csörgésre |
| `tapper` | **két egyidejű nyomás** szintetikus PointerEventtel |
| `cardbattle` | húzás helyett a kattintós út (lap kijelölés → körslot) |
| `ritmus` | 1. kör aktív koppintás, 2. kör passzív → van nyertes és vesztes |
| `powerhour` | az 1000 ms-os időzítőt felgyorsítja, így az „óra" ~15 mp |

Ami driver-oldali trükköt igényelt, az a kódban is kommentelve van (pl. a
Tappernél a `setPointerCapture` kiütése, a Kártyacsatánál a kijelölés és a
slot-kattintás szétválasztása két `evaluate`-re).

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
