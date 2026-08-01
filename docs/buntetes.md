# Büntetés — mit tud, és hol vannak a csapdák

Játékon kívüli korty kiosztása. Két helyről indul, de **egy** felület és **egy**
függvény szolgálja ki (v10.272 óta).

| | MENÜ → 🎲 Büntetés | Wildcard → „Szabályszegő?" |
|---|---|---|
| mikor érhető el | mindig, a MENÜ-ből | csak ha van aktív wildcard |
| cím | „Büntetés — ki igyon?" | „Ki szegte meg a szabályt?" |
| fejléc | — | a wildcard emojija + a szabály szövege |
| banner-jegyzet | „Büntetés" | „Szabályszegés" |
| **minden más** | **azonos** | **azonos** |

Kód: `PenaltyModal` (a komponens) → `applyPenalty` / `applyWcPunish` (a két
belépő) → `givePenalty(map, opts)` (a közös logika).

---

## A felület

- **Középre igazított modal**, 340 px széles, nem alsó lap.
- Soronként: **avatar · név ......... − [n 🍺] +**
- **Egyszerre 5 sor látszik**, onnantól görgethető. A korlát sor-alapú, nem
  `vh`: egy sor 48 px, a rés 8 px → `5×48 + 4×8 = 272 px`. Ezek **mért**
  értékek; ha a sor magassága változik, a `ROW_H` / `ROW_GAP` konstanst kell
  vele együtt vinni, különben a lista fél sornál állna meg.
- A szám melletti mező fix 44 px széles, hogy a `–` → `1 🍺` váltásnál **ne
  ugorjon meg a sor**.
- Záró gomb: „N korty kiosztva" (0-nál „Senki sem iszik"), alatta **Mégse**.
  A háttérre koppintás is zár.
- Csak az **aktív** játékosokat sorolja fel — szünetelő játékosra nem lehet
  kortyot osztani.

## Mit tud

- Fejenként **tetszőleges** korty (nem csak 1).
- **Több embernek egyszerre**, eltérő összeggel is.
- Ez a wildcard-oldalon **új** (v10.272): korábban ott fix 1 korty ment
  egyetlen embernek.

## Mi történik a megerősítés után

1. A korty **azonnal** rákerül a játékosokra (`players.drinks`).
2. Online partiban a szoba szinkronizálódik.
3. Feljön a **result banner** (nem külön Toast — az a v10.271-ben kivezetve).
4. A parti végi statisztikába onnan megy tovább, hogy a `players` tömbben van —
   **nem** logolunk külön eseményt, mert az duplán számolna.

### Mit ír ki a banner

| eset | mi látszik |
|---|---|
| mindenki **ugyanannyit** kapott | a szám: pl. `2 KORTY` + a jegyzet („Büntetés" / „Szabályszegés") |
| fejenként **más** | névenkénti felsorolás (`Sere 2🍺, Kecsi 1🍺`), **szám nélkül** |

A második eset azért szám nélküli, mert **nincs olyan egy szám, ami igaz
lenne** — sem az összeg, sem bármelyik érték.

---

## Három csapda, amibe a naiv megvalósítás beleesik

Mindhármat teszt védi (`tests/penalty_unified_test.js`).

### 1. A büntetés ABSZOLÚT — nem szabad beszorozni

Az `onResult` minden korty-számot beszoroz: `d × diffDrinks × wcMult`. A
büntetésnél viszont a játékos **konkrét** számot választott, és pontosan annyi
ment a `players` tömbbe.

> Extrém nehézségen (×5) egy 2 kortyos büntetésből **10** lett volna a
> bannerben, miközben 2 ment a játékosra.

Ezért kap az `onResult` egy `penalty` jelzőt, ami kihagyja a szorzást.

### 2. A „fordított kör" wildcard nem forgathatja meg

A `reverse` effekt megcseréli a nyerteseket és a veszteseket. Büntetésnél ez a
**szabályszegőt nyertesként** mutatná. Ugyanaz a `penalty` jelző ezt a cserét
is kihagyja — a büntetés büntetés marad.

### 3. A `pendingCommit` felülírhatja (v10.274)

Ez volt a legalattomosabb. Az `advance*` függvények **nem** commitálnak
azonnal: kiszámolják a játékosok végállapotát, és beteszik a `pendingCommit`-be.
A **Kövi** gomb ezt a kész tömböt írja vissza.

Ha közben büntetést adtál, a Kövi egy olyan állapotot írt vissza, ami még nem
tudott róla:

```
pörgetés után : Sere:0, Kecsi:0, Luca:0   ← a nyeremény még pendingCommit-ben
büntetés után : Sere:2, Kecsi:0, Luca:0   ← a büntetés rákerült
KÖVI után     : Sere:0, Kecsi:1, Luca:0   ← a büntetés eltűnt
```

**A megoldás:** a `pendingCommit` eltárolja azt a tömböt is, *amiből* a
végállapot született (`basePlayers`), és commitáláskor a `mergeCommit` a
**különbséget** adja hozzá az aktuális értékhez. Ha közben semmi nem történt,
`current === base`, tehát az eredmény pontosan a régi `newPlayers` — a normál
úton ez semmit nem változtat.

Két helyen kell: `commitPending()` (Kövi) és `flushPendingBeforeEnd()` (buli
lezárása). A második nélkül a büntetés a **végeredményből** esne ki.

> **Ez nem a büntetés hibája volt.** Bármi más, ami menet közben módosítja a
> játékosokat, ugyanígy elveszett volna. A büntetés csak az első, ami ilyet
> ténylegesen csinál — ha jön még ilyen funkció, a `mergeCommit` már megvédi.

---

## Amit NEM tud (tudatosan)

- **Nem vonható vissza.** A MENÜ visszavonás-gombja a *kör* eredményét vonja
  vissza; büntetéshez nem készül undo-pont. És kézzel sincs hova nyúlni: a
  MENÜ → szerkesztés csak nevet és játékost kezel, **korty-számot nem lehet
  benne állítani**. Egy elkattintott büntetés tehát bent marad a partiban.
  (Ha ez zavaró, két irány van: undo-pont a büntetéshez, vagy korty-mező a
  szerkesztés-fülön.)
- **Nem tud pontot elvenni**, csak kortyot adni.
- **Nem tud 0-nál kevesebbet**: a `−` gomb 0-nál letiltott.
- Ha senki nem kap semmit, a záró gomb **nem csinál semmit** — nincs üres
  banner (`if (!total) return;`).

## Mellékhatás, amit érdemes tudni

- A **korty-limit figyelmeztetés** a büntetést is számolja: ha a büntetéssel
  éri el valaki a limitjét, a figyelmeztetés a **következő körváltásnál** jön
  elő (nem azonnal — különben rácsúszna a bannerre).
- A parti **játék-statisztikájába** (`totalDrinks`) a büntetés annak a játéknak
  a rovatára megy, ami épp fut. Ez vitatható — a büntetés nem a játék műve —,
  de így egyszerű, és a parti összesített korty-száma pontos marad.

## Tesztek

`tests/penalty_unified_test.js` — 8 szekció:

1. azonos összeg → a banner kiírja a számot
2. eltérő összeg → névenkénti felsorolás, szám nélkül
3. wildcard-út: ugyanaz a modal, ugyanolyan széles (340/340)
4. új képesség: több korty, több ember
5. fordított kör nem forgatja meg
6. 5 sor / 272 px / sörös ikon / nincs pipa
7. Mégse nem oszt ki semmit
8. a büntetés túléli a Kövi gombot

`tests/penalty_test.js` — a MENÜ-belépő és a sok-játékos eset (12 fő: görgethető
lista, a záró gomb görgetés nélkül is látszik, a modal középen lebeg).

> **Teszt-csapda:** a háttérben futó játék is rajzolhat korty-kiosztót (a
> Kő-papír-olló „1. kör — kortyok" lapját), saját „korty kiosztva" gombbal.
> A gombra keresni **nem elég** — a modal saját overlay-jére (`zIndex 60`) kell
> szűkíteni, különben a háttér lapját vezérled.
