# Bottle of Heroes — fejlesztési összefoglaló

## Projekt
Magyar ivós mobiljáték app. React 18 UMD, Firebase Firestore multiplayer.

**GitHub:** https://github.com/kepesspo/bottle-of-heroes  
**Push parancs:**
```bash
git remote set-url origin https://<TOKEN>@github.com/kepesspo/bottle-of-heroes.git && git push -u origin main
```
(Token a session kontextusában van — ne tárold fájlban!)

## ⚠️ BUILD WORKFLOW (v9.902 óta) — EZT KÖVESD!
- **FORRÁS: `app.src.html`** — MINDEN kód-szerkesztés ebben történik (JSX, `type="text/babel"`).
- **`index.html` GENERÁLT FÁJL — SOHA ne szerkeszd kézzel!** A `node build.js` állítja elő.
- Munkafolyamat minden változtatásnál:
  1. szerkeszd az `app.src.html`-t (verzióbump is itt: `const APP_VERSION = '...'`)
  2. `node build.js` — előfordítja a JSX-et (a forrásba ágyazott Babellel), production React-et
     illeszt be a `vendor/`-ból, kidobja a Babel-standalone-t, és generálja az `sw.js`-t
  3. tesztek az `index.html` (buildelt) ellen futnak
  4. commitold MINDKETTŐT (`app.src.html` + `index.html` + `sw.js`)
- Az `app.src.html` önmagában is futtatható böngészőben (dev mód, lassú — böngészőben fordít).
- `sw.js`: cache-elő service worker (stale-while-revalidate) — a build generálja, cache-név az APP_VERSION.
  Frissítésnél a felhasználó "Új verzió" sávot kap; az admin "kényszerített frissítés" továbbra is működik.

## Architektúra
- Forrás: `app.src.html` (~61000 sor) → buildelt `index.html` (~2 MB)
- Game bannerek/ikonok: `assets/` mappa (útvonal-hivatkozás az `IMGS` objektumból)
- Beépített avatarok: `assets/avatars/char_*.png` (a CHAR_AVATARS útvonalakat hivatkozik)
- Python patch scriptek (`patch_5_XX.py`) minden nagyobb változáshoz — az app.src.html-t patchelik!
- Firebase Firestore compat SDK online multiplayer módhoz

## Játékok listája (24 db)
`busz, imposztor, memoria, erem, ticktak, kezcsere, anagramma, ringfire, rulett, kisebb, tapper, kategoria, hajime, kopapir, fingerit, uveg, zene, loverseny, otdolog, szerencse, sohanem, collect, kivagyok, mindenki, igazhamis`

Minden játékhoz: `id, name, difficulty, category, emoji, symbol, img, banner, color, desc`

## Game kategóriák
- **Egyéni** — 1 játékos játszik
- **Páros** — 2 játékos (kihívó + véletlenszerűen kisorsolt ellenfél)
- **Csapat** — mindenki játszik

## PlayScreen fontos elemek

### Top bar (fejléc)
- Bal: info gomb (44px) **54px-es láthatatlan konténerben**
- Közép: `currentGame.banner` → banner kép (`width:100%, height:auto`), egyébként ikon+szöveg
- Jobb: KÖR SVG gyűrű (54px) — körszámláló

### Footer (alsó sáv) — sorrend: MENÜ | Ki játszik | Kövi
- **MENÜ gomb** (bal): ikon + "MENÜ" felirat
- **Player pill** (közép, flex:1): Egyéni/Páros/Csapat variáns, stabil wrapper divben
- **Kövi gomb** (jobb): következő játék ikonja + "Kövi" felirat, aktív/inaktív állapot

### pendingCommit pattern
Az advance funkciók nem commitálnak azonnal — `setPendingCommit({newPlayers, fb, newTurn, newGameIdx, newRound})` — a Kövi gomb nyomására fut `commitPending()`.

### Páros ellenfél auto-select
`useEffect([turn, gameIdx])` — véletlenszerűen választ ellenfelet, nem kell manuálisan kiválasztani.

## CSS osztályok
- `.appbar-shell` — sticky fejléc (Players/Games oldal), lekerekített alsó sarkok
- `.bottombar-shell` — alsó sáv, lekerekített felső sarkok  
- `.play-footer-inner` — játék footer belső sor (`align-items:stretch, gap:12px`)

## Banner képek
- Forrás: `game-headers/` mappa (800×120px PNG, átlátszó háttér)
- Középre igazított verzió: `game-headers-centered/` (automatikusan generált PIL-lel)
- Beágyazva: `IMGS['<id>_banner.png']` kulcs alatt

## ⚠️ Safe area és felső státuszsáv (iOS PWA) — VISSZATÉRŐ HIBA
**Mielőtt hozzányúlsz: `docs/safe-area.md`.** Automata védelem:
`node tests/safearea_test.js`.

Röviden, ami a legtöbb kört elvitte:
- **Böngészőben ez NEM reprodukálható** (`env(safe-area-inset-*)` = 0). Soha ne
  "ránézésre" javítsd — szimulálj (lásd a doksit), vagy kérj számot a
  készülékről (Beállítások alja, TESZT DB módban).
- A **service worker `stale-while-revalidate`**: az első indítás a push után
  még az ELŐZŐ buildet futtatja. Verziót ellenőrizni, mielőtt kijelentenéd,
  hogy a javítás nem működik.
- **iOS a `position:fixed` rétegeket üresnek látja** a státuszsáv mögött → a sáv
  színének *folyamban lévő* tartalomból kell jönnie (a gyökér konténer
  háttere), és a `theme-color` metának is ugyanazt kell adnia.
- **`100dvh` iOS PWA-ban nem következetes** → a teljes képernyős magasság
  `var(--app-h, 100dvh)`, ahol az `--app-h` mért érték, és csak a konkrét
  iOS-aláírásra (`screen.height - innerHeight == env(safe-area-inset-top)`)
  aktiválódik.

## Én még soha (v10.288)
A kérdés-lap **egy színű**, és a szín a témából jön (`T.bgSoft`) — a fűszerszintet
csak a bal felső jelvény viszi (`SPICE[].badge`, fix szín, fehér felirattal).
Amit könnyű elrontani: mivel a lap színe témafüggő, a **tinta is `T.ink`** kell
legyen. A régi fix `CARD_INK = '#14202F'` sötét témán sötét szöveget hagyna
sötét lapon. Ugyanezért származik a perem és a két halvány kör is `T.ink`-ből.
A `DrinkDistributor` nem szab saját szélességet — a szülő dönt (játékon belül
a kérdés-lappal egyenlő, a Büntetés-modalban 296 px). Kiosztás után a léptetők
eltűnnek, és csak azok maradnak a listában, akik ténylegesen kaptak kortyot.

## Büntetés (játékon kívüli korty)
Két belépő (MENÜ → Büntetés, Wildcard → „Szabályszegő?"), **egy** felület
(`PenaltyModal`) és **egy** logika (`givePenalty`). Mielőtt hozzányúlsz:
`docs/buntetes.md` — három csapda van benne (abszolút szám, fordított kör,
`pendingCommit`-felülírás). Teszt: `node tests/penalty_unified_test.js`.

## „Ki igyon?" — a KÖZÖS korty-sor (v10.291)
Minden ilyen felület **egyetlen** `PlayerDrinkRow`-ból épül (`app.src.html`,
a `DRINK_ROW_H` konstans alatt). Ne írj újat: korábban négy változat élt
(Büntetés + Én még soha közösen, a Kategória kézzel lemásolva, a Lóverseny
fehér kártyára forkolva), és a másolatok elcsúsztak — a nulla egyszer `–` volt,
egyszer `0`, a `+` egyszer korall, egyszer menta.

A különbség **prop, nem új markup**:
- `variant='stepper'` (alap) — `−  szám  +`. Büntetés, Én még soha, Lóverseny.
- `variant='pick'` — léptető helyett pipa, egy embert választunk. Kategória.
- `readOnly` — szám gomb nélkül (kiosztás utáni összegzés). Nullánál nem ír
  ki `0 🍺`-t: ott vagy a `meta` beszél, vagy semmi.
- `meta` — jobbra tolt chip. A Lóverseny tétje ide megy (ló-pont + korty),
  **nem** második sorba: a sor mind a négy helyen pontosan `DRINK_ROW_H` = 48 px.
- `max` — plafon egy játékosra (Én még soha: 1).
  `addDisabled` — a **közös** keret fogyott el (Lóverseny nyereménye).

Két dolog, amit könnyen elrontasz:
- **Ikonok.** A korongos `BohIcon` (`check`/`cross`/`plus`/`minus`) a *lágy*
  hátterű sorokra való, ahol a saját színe hordozza a jelentést. Tömör
  mint/korall gombon beleolvadna — ott a vonalas `Icon` megy fehérrel.
  Unicode `✓ ✕ − +` sehol.
- **Tesztfogódzó.** A léptetők SVG-k, nincs szöveges `+`/`−`. A tesztek
  `button[aria-label="Egy korttyal több"]` / `"…kevesebb"` alapján kattintanak
  (`ledger_test.js`, `sohanem_test.js`, `penalty_unified_test.js`). Ha
  átnevezed az aria-labelt, négy teszt némán elnémul.

## Szólánc (v10.286)
Hőfok-lap a Szerencsekerék pasztelljeiből — **egy szín = egy tét**
(`SZ_TONES`, `szTone()`): zöld 2–4 szó / 1 korty, sárga 5–7 / 2, rózsa 8+ / 3,
felszorozva a nehézséggel és a wildcarddal. A tinta FIX `#14202F`.
A lánc `SZ_MAX_LEN = 12` szónál zárul, és aki odáig elviszi, **mindenkinek**
+1 pontot hoz. Három dolog, ami együtt mozog:
- a `stake:[1,3]` tartományt kézzel kell utánaigazítani, ha a `korty` értékek
  változnak, különben a korty-korong mást ígér, mint amit a játék kioszt;
- **23 kategória**, mind pontosan **20 szavas**, mert `SZ_MAX_LEN` láncszó
  után is kell legalább 3 csali — 15 szónál minden szinten ugyanaz a három
  lenne, és két kör után mindenki tudná, hogy azokat nem kell nézni;
- a `chainPool` / `decoyPool` vágás `SZ_MAX_LEN`-hez igazodik, nem felezés. Két invariáns, amit könnyű
elrontani, és a `tests/szolanc_test.js` őriz:
- **`SZ_CARD_H` / `SZ_ACT_H`**: az átadás és a villantás UGYANAZT a téglalapot
  használja (méret *és* pozíció). A villantáson üresen fenn kell tartani a
  gombsor helyét — enélkül a középre igazítás 31 px-szel feljebb tolja a lapot.
- **`chainPool` / `decoyPool`**: a kevert lista kettévágva. Ha egy kalapból
  húznál, a csali megint jövőbeli láncszem lenne, és a játék előre kiadná magát.

## Fontos szabályok
1. Minden commitnál verzióbump kötelező (az `app.src.html`-ben!)
2. Kódot CSAK az `app.src.html`-ben szerkessz, majd `node build.js` (lásd BUILD WORKFLOW fent)
3. Nagy változásoknál Python patch script (`patch_5_XX.py`)
4. Assert-ekkel ellenőrizni a string replacement-et
5. `align-items:stretch` a footer rowon → egyforma magasság
6. Pill variánsok stabil `flex:1, minWidth:0, overflow:hidden` wrapperben
