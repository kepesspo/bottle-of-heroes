# Safe area és felső státuszsáv (iOS PWA)

> **Miért van ez a fájl?** Ez a hiba többször visszatért, és minden alkalommal
> több kört vitt el, mert **böngészőben nem reprodukálható**. Itt van összeszedve
> az ok, a megoldás helye a kódban, és hogyan lehet készülék nélkül tesztelni.
>
> Automata védelem: `tests/safearea_test.js` (`node tests/safearea_test.js`).

---

## 0. Az első szabály: böngészőben ez NEM látszik

Böngészőben `env(safe-area-inset-*)` = **0**, tehát minden ide tartozó hiba
láthatatlan. Aki csak Chromiumban néz rá, azt fogja hinni, hogy jó.

**Következmény:** ezt a két dolgot *soha ne* "ránézésre" javítsuk. Vagy
szimulálni kell (lásd 3.), vagy a készülékről kell szám (lásd 4.).

**Második csapda:** a service worker `stale-while-revalidate` stratégiával
szolgál ki (`sw.js`), tehát **az első indítás a push után még az ELŐZŐ buildet
futtatja**. Mielőtt kijelentenénk, hogy egy javítás nem működik, ellenőrizni
kell a verziószámot (a diagnosztika kiírja).

---

## 1. Felső státuszsáv színe

### Az ok

**Két, egymástól független mechanizmus** festi a státuszsáv mögötti sávot.
Ha a kettő eltérő színt ad, a sáv hol jó, hol rossz — jellemzően az *első*
indításkor rossz, utána jó.

| # | Mikor érvényes | Mi adja a színt |
|---|---|---|
| 1 | `apple-mobile-web-app-status-bar-style: black-translucent` aktív (normál eset) | a sáv **átlátszó**, a mögötte lévő **folyamban lévő** lap-tartalom látszik |
| 2 | amíg ez a stílus nem érvényesül (tipikusan a legelső indítás a főképernyőre mentés után), illetve Androidon | `<meta name="theme-color">` |

### Két buktató, ami sok időt vitt el

- **iOS a `position:fixed` rétegeket üresnek látja** a státuszsáv mögött. Volt a
  kódban egy `position:fixed; z-index:55` festősáv — az **soha nem festett** ott.
  Nem tűnt fel, mert a színe (`T.bg`) pont egyezett a mögötte lévő `<body>`
  háttérrel. Amint fehérre váltottuk, kiderült.
  → **A színnek folyamban lévő tartalomból kell jönnie.**
- A `theme-color` fixen a téma háttere volt, egyetlen helyen beállítva
  induláskor → a 2-es ág mindig barackot adott.

### A megoldás a kódban (`app.src.html`, `BottleApp`)

Egyetlen forrás, `statusBarBg`:

```js
const statusBarBg = (creatingRoom || screen === 'home' || screen === 'play')
  ? T.bg        // ahol NINCS fejléc → a téma háttere
  : T.surface;  // ahol fehér AppBar van → fehér, így a fejléc a kijelző tetejéig ér
```

Ezt **három helyen** kell használni, különben szétcsúsznak:

1. **a gyökér képernyő-konténer `background`-ja** — ez a folyamban lévő tartalom,
   ez fest az 1-es ágon (a konténernek van `paddingTop: env(safe-area-inset-top)`,
   így a háttere pont a státuszsáv mögötti sávot tölti ki);
2. a `position:fixed; z-index:55` festősáv — böngészőben/Androidon ez fest;
3. `useEffect` → `<meta name="theme-color">` — ez fest a 2-es ágon.

### Ha új képernyő kerül be

A `statusBarBg` feltételébe azok a képernyők tartoznak, ahol **nincs AppBar**:
jelenleg `home`, `play`, és a `creatingRoom` állapot. Minden más képernyő fehér
AppBar-t rajzol → fehér sáv. Új, fejléc nélküli képernyőnél ide fel kell venni.

### 1/b. Modal és bottom sheet: a sáv is besötétedik (v10.343)

A modalok sötétítő háttere `position:fixed` — vagyis **pontosan az a réteg,
amit iOS nem fest a státuszsáv mögé**. Következmény: a lap besötétedett, a
státuszsáv világos maradt, és a kettő élesen elvált.

Mivel a sáv színe csak a `statusBarBg`-n keresztül jöhet, **magát a
`statusBarBg`-t sötétítjük**:

```js
const baseBarBg = (creatingRoom || screen === 'home' || screen === 'play') ? T.bg : T.surface;
const statusBarBg = bohBlendOver(baseBarBg, useOverlayTint());
```

**⚠️ Miért nem regisztrációval?** Mert **negyven** ilyen fedő réteg van a
forrásban, és egy új modal írójától nem várható el, hogy erre gondoljon —
ugyanúgy elfelejtődne, ahogy a `banner:` mező és a Páros kizárás-lista is
elfelejtődött. Helyette a DOM-ot nézzük: teljes képernyős, **átlátszó** hátterű
`position:fixed` elem = fedő réteg (`bohScanOverlayTint`). Olcsó: csak
DOM-változásra fut, rAF-fel összevonva, és a jelölteket egy inline-stílus
szelektor szűri elő.

Három határeset, amit a detektornak KI kell zárnia (mind a
`statusbar_dim_test` 4. blokkjában):
- **teljesen fedő** réteg (alpha 1) — az nem sötétítés, hanem egy lap;
- **alig látható** (alpha < 0,15) — nem sötétít láthatóan;
- **kicsi, lebegő** fix elem — nem fedő réteg.

**Teszt-buktató:** a `SheetOverlay` **portálba** renderel (`document.body`),
ezért a mountoló host elem törlése NEM szedi le — a React gyökeret kell
lebontani. És a gyökér képernyő-konténer az, aminek az inline stílusában ott a
`--app-h`; a `#root > div` egy külső burok, amivel a mérés vakon átmenne.

---

## 2. Alsó holt-zóna (safe area)

### Az ok

iOS **black-translucent** módban telepített PWA-nál a webnézet a kijelző
tetejétől indul, de a **layout-viewport pontosan a státuszsáv magasságával
rövidebb**. Emiatt alul marad egy ugyanolyan magas sáv, ami **fizikailag
látszik, de a viewporton kívül van** — oda nem kerül tartalom.

Mért adatok egy iPhone-ról (Dynamic Island):

```
screen.height = 874    window.innerHeight = 812    env(safe-area-inset-top) = 62
                       874 − 812 = 62  ← pont az envTop
```

### Amit NE csináljunk: `100dvh`-ra építeni

A `100dvh` ebben a módban **nem következetes**. Ugyanabban az appban két
verzióban két különböző értékként viselkedett (812, majd ~874), ezért a
`calc(100dvh + env(safe-area-inset-top))` képlet egyszer alullőtt, egyszer
túllőtt. Képlettel nem kerülhető meg.

### A megoldás: mért abszolút magasság + aláírás-ellenőrzés

A `<head>`-ben futó szkript beállít egy `--app-h` CSS-változót:

```js
// Az iOS black-translucent holt-zóna EGYEDI ujjlenyomata:
//   screen.height − innerHeight  ==  env(safe-area-inset-top)
var ok = standalone && envTop > 0 && deficit > 0 && Math.abs(deficit - envTop) <= 2;
if (ok) documentElement.style.setProperty('--app-h', screen.height + 'px');
else    documentElement.style.removeProperty('--app-h');
```

Használat (fallback mindenhol `100dvh`):

```css
height: var(--app-h, 100dvh)
```

- gyökér képernyő-konténer magassága
- `SheetOverlay` magassága (a lapok alatti üres sáv ugyanez a hiba volt)
- alsó festősáv pozíciója: `top: calc(var(--app-h, 100dvh) - 1px)`

### Miért az aláírás-ellenőrzés?

Mert a `screen.height` a **fizikai kijelzőt** adja, ami csak teljes képernyős
appnál egyezik az ablak magasságával. Aláírás-ellenőrzés nélkül elrontaná:
iPad Split View / Stage Manager, Android multi-window, fekvő tájolás.

Az aláírás-ellenőrzés miatt a korrekció **csak** a konkrét iOS-hibára kapcsol be;
minden más helyzetben ki van kapcsolva, és marad a szokásos `100dvh`.
A `tests/safearea_test.js` pontosan ezt a hat esetet ellenőrzi.

---

## 3. Tesztelés készülék nélkül

Chromium **nem emulálja** az `env()`-et és a standalone módot. Két trükk kell:

**a) `env()` behelyettesítése** egy másolatba (a build után):

```bash
sed -e 's/env(safe-area-inset-top)/62px/g' \
    -e 's/env(safe-area-inset-bottom, 0px)/34px/g' \
    -e 's/env(safe-area-inset-bottom)/34px/g' \
    -e 's/100dvh/812px/g' \
    index.html > /tmp/sim.html
```

**b) standalone mód + fizikai kijelző hamisítása** Playwrightban:

```js
await p.addInitScript(`
  Object.defineProperty(navigator,'standalone',{get:()=>true,configurable:true});
  Object.defineProperty(window.screen,'height',{get:()=>874,configurable:true});
`);
// a viewport magassága = window.innerHeight (a rövidebb layout-viewport)
const p = await b.newPage({ viewport:{ width:402, height:812 } });
```

**c) az iOS-viselkedés szimulálása a fix rétegre** (hogy kiderüljön, ha valamit
`position:fixed`-re bíztunk a státuszsáv mögött): futásidőben töröljük a fix
csíkot, és nézzük meg, jó marad-e a szín.

---

## 4. Diagnosztika a készüléken

**Beállítások lap alja** — csak akkor jelenik meg, ha a **TESZT DB mód be van
kapcsolva** (a főoldalon a verziószámra 3× koppintva kapcsolható).

```
v10.230 · PWA
screen=874 inner=812 100dvh=812
hiány=62 envTop=62 envBot=34
korrekció=BE (874px)
```

Mit néz az ember:

- **verzió** — a service worker miatt az első indítás még az előző buildet
  futtatja; ha nem a friss verzió, a többi szám nem is releváns
- **hiány vs envTop** — ha egyeznek, fennáll az iOS-aláírás
- **korrekció** — BE/KI, tehát tényleg aktiválódott-e

---

## 5. Ellenőrzőlista, ha megint elromlik

1. A diagnosztikában a **verzió** a friss build? (ha nem: nyisd meg még egyszer)
2. **Felső sáv rossz színű?** → a `statusBarBg` mind a három helyen érvényesül?
   Új, fejléc nélküli képernyő került be?
3. **Alul üres hely / kilóg a tartalom?** → `korrekció=BE`? A `hiány` egyezik az
   `envTop`-pal? Használ valahol még `100dvh`-t olyan elem, ami teljes képernyős?
4. `node tests/safearea_test.js` — zöld?

---

## 6. Teljes képernyős FIX réteg: a pull-up KIOLTHATJA a felső paddingot (v10.328)

Volt a kódban hét ilyen wrapper:

```jsx
position:'fixed',
top:'calc(-1 * env(safe-area-inset-top))',   // felhúzás
paddingTop:'env(safe-area-inset-top)',       // …és ugyanennyi vissza
```

A kettő **EREDŐJE NULLA**: a tartalom pont a fizikai kijelző tetején kezdődik,
tehát a **státuszsáv mögé** kerül. Böngészőben ez láthatatlan (`env()` = 0).

**Miért nem tűnt fel évekig?** Mert a gyökér képernyő-konténer animációja
(`slideIn`) `transform`-ot használ, és egy futó transzformáció **tartalmazó
blokkot** csinál a `position:fixed` leszármazottaknak. Amíg az animáció fut
(0,35 mp), a felhúzás a *már paddingelt* héjhoz képest számít, tehát jónak
látszik — utána viszont a viewporthoz, és a tartalom becsúszik a sáv mögé.
Ezért tűnt „néha jónak".

Ami elromlott tőle: a Busz „host játszik játékosként" nézetében a felső sáv a
**🎮 kijárattal együtt** a státuszsáv alá került — a játékos nem tudott
visszalépni.

**A helyes alak** (a háttér így is befest a sáv mögé, mert a padding-terület a
konténer hátterét viseli):

```jsx
position:'fixed', top:0, left:0, right:0, bottom:0,
paddingTop:'env(safe-area-inset-top)', boxSizing:'border-box'
```

**A pull-up NEM mindig hibás**: ahol a felső padding *nagyobb*
(`calc(env(safe-area-inset-top) + 20px)`), ott szándékosan kompenzál —
a Profil-részletek és az ünneplő overlay ilyen. A `safearea_test.js` 4. blokkja
ezért nem a pull-upra szűr, hanem a **kioltó párosra**.

Teszt: `node tests/safearea_test.js` 4. blokk. A regressziót a **forrás-
ellenőrzés** fogja meg (a DOM-mérés a helyes geometriát dokumentálja).
