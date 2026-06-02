# Bottle of Heroes — fejlesztési összefoglaló

## Projekt
Magyar ivós mobiljáték app. Single HTML file (`index.html`), React 18 UMD + Babel standalone, Firebase Firestore multiplayer.

**Aktuális verzió:** v5.66  
**GitHub:** https://github.com/kepesspo/bottle-of-heroes  
**Push parancs:**
```bash
git remote set-url origin https://<TOKEN>@github.com/kepesspo/bottle-of-heroes.git && git push -u origin main
```
(Token a session kontextusában van — ne tárold fájlban!)

## Architektúra
- Egyetlen `index.html` (~39000+ sor)
- Minden asset (képek) base64-ben beágyazva az `IMGS` objektumba
- Python patch scriptek (`patch_5_XX.py`) minden nagyobb változáshoz
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

## Fontos szabályok
1. Minden commitnál verzióbump kötelező
2. Nagy változásoknál Python patch script (`patch_5_XX.py`)
3. Assert-ekkel ellenőrizni a string replacement-et
4. `align-items:stretch` a footer rowon → egyforma magasság
5. Pill variánsok stabil `flex:1, minWidth:0, overflow:hidden` wrapperben

## Következő tervezett feature
- **Ország-Város-Fiú-Lány játék** megvalósítása (egy telefon mód: betű kisorsol, játékosok szavaznak az eredményekre)
