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

## Büntetés (játékon kívüli korty)
Két belépő (MENÜ → Büntetés, Wildcard → „Szabályszegő?"), **egy** felület
(`PenaltyModal`) és **egy** logika (`givePenalty`). Mielőtt hozzányúlsz:
`docs/buntetes.md` — három csapda van benne (abszolút szám, fordított kör,
`pendingCommit`-felülírás). Teszt: `node tests/penalty_unified_test.js`.

## Szólánc (v10.284)
Hőfok-lap a Szerencsekerék pasztelljeiből — a szín a **sor hosszát** kódolja
(`SZ_TONES`, `szTone()`), a tinta FIX `#14202F`. Két invariáns, amit könnyű
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
