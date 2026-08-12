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

## Szólánc (v10.286, számok v10.289 óta)
Hőfok-lap a Szerencsekerék pasztelljeiből — **egy szín = egy tét**
(`SZ_TONES`, `szTone()`): zöld 1–4 szó / 1 korty, sárga 5–7 / 2, rózsa 8+ / 3,
felszorozva a nehézséggel és a wildcarddal. A tinta FIX `#14202F`.
A lánc **1 szóval indul** (`fresh(1, 0, true)`) és `SZ_MAX_LEN = 10` szónál
zárul; aki odáig elviszi, **mindenkinek** +1 pontot hoz. Három dolog, ami együtt mozog:
- a `stake:[1,3]` tartományt kézzel kell utánaigazítani, ha a `korty` értékek
  változnak, különben a korty-korong mást ígér, mint amit a játék kioszt;
- **23 kategória**, mind pontosan **20 szavas** (10 lánc + 10 csali), mert
  `SZ_MAX_LEN` láncszó után is kell legalább 3 csali — 13 szónál minden
  szinten ugyanaz a három lenne, és két kör után mindenki tudná, hogy azokat
  nem kell nézni;
- a `chainPool` / `decoyPool` vágás `SZ_MAX_LEN`-hez igazodik, nem felezés. Két invariáns, amit könnyű
elrontani, és a `tests/szolanc_test.js` őriz:
- **`SZ_CARD_H` / `SZ_ACT_H`**: az átadás és a villantás UGYANAZT a téglalapot
  használja (méret *és* pozíció). A villantáson üresen fenn kell tartani a
  gombsor helyét — enélkül a középre igazítás 31 px-szel feljebb tolja a lapot.
- **`chainPool` / `decoyPool`**: a kevert lista kettévágva. Ha egy kalapból
  húznál, a csali megint jövőbeli láncszem lenne, és a játék előre kiadná magát.

## Szoba-töltés animációk (v10.292)
`RoomFillArt` — négy rajz, szobanyitáskor sorsolva (`BOH_ROOM_ART_COUNT = 4`),
a „TÖLTJÜK A SZOBÁT" felirat fölött. SVG, nem kép: a kontúr a `T.ink`-ből jön.
- **0 korsó** · **1 palack** · **2 feles-sor** (hat stampedli, balról jobbra)
  — mind a három EGY edényt tölt meg, és a töltés maga a folyamatjelző.
- **3 koccintás** — két korsó lendül össze, a becsapódásnál szikra, csillag és
  habcseppek. Ez az egyetlen, ami nem tölt: azt mondja, hogy *többen lesztek*.

Amit könnyű elrontani:
- A koccintásnál a **fülek kifelé néznek** — befelé fordítva a két fül a
  koccanáskor egymásba érne.
- A becsapódás **34%-nál** van, és a szikra/csillag/csepp MIND oda van időzítve.
  Ha az egyiket elcsúsztatod, szétesik a mozdulat.
- A nyugalmi helyzet ±30 egység és −13° dőlés, ezért a viewBox `-16 0 272 150`
  — a 16 egységnyi eltartás nélkül levágódik a két szélső korsó.
Teszt: `node tests/roomart_test.js` (mind a négy rajzol és animál, a koccanásnál
a rés tényleg nullára zár, és felvillan a csillag).

## Nehézségi korty-szorzó (v10.296) — EGY forrás
A szorzó a `DIFFICULTY_INFO` `mult` mezőjéből jön, és a szintek azonosítója
**`easy` / `mid` / `hard` / `extreme`** (1 / 2 / 3 / 5) — a `gameMeta.difficulty`
ezt tárolja. A `GAMES[].difficulty` (`könnyű`/`közepes`/`nehéz`) ettől FÜGGETLEN:
az a játék saját, statikus címkéje a kártyán, nem a partira beállított szint.
A kettőt összekeverni néma hiba: a magyar címkére illesztő szorzó mindig 1-et ad.

Hol számolódik és hogyan jut le:
- `PlayScreen`: `diffDrinks = diffMeta.mult`, a wildcarddal `diffDrinks * wcMult`
- ez megy le a `GameContent`-nek **`drinkMult` propként** — új játéknál ezt add
  tovább, ne számolj újat
- a könyvelés (`advanceLoverseny`) és a banner (`onResult`) **már szoroz**, tehát
  a korty-osztó sor csak KIJELZ: `PlayerDrinkRow`/`DrinkDistributor` `drinkMult`-ja
  kizárólag a megjelenített számot skálázza, a `onFinish` nyers marad

Egy felület, ami KIMARAD, és nem véletlenül:
- **Büntetés** (`PenaltyModal`) — abszolút, se nehézség, se wildcard nem szorozza
  (`docs/buntetes.md` 1. csapda, `penalty` jelző az `onResult`-ban)

A **Lóverseny v10.299-ig szintén kivétel volt** (`scale=1`) — már nem az, lásd lent.

Teszt: `node tests/diffmult_test.js` — mind a négy szinten összeveti a léptetőre
írt számot azzal, amennyi ténylegesen a játékosra kerül, és őrzi a büntetés
abszolút voltát.

## ⚠️ A `gameMeta` MENTETT config — nem callback-csatorna (v10.297)
A `gameMeta` egészében lemegy a Firestore-ba (`createRoom` → `rooms/<kód>`).
Csak **szerializálható** érték kerülhet bele: szám, string, tömb, sima objektum.
Egy React callback beletétele az EGÉSZ szobanyitást megöli:

> `invalid-argument — Unsupported field value: a function (found in field
> gameMeta.onBetUpdate)`

A csapda alattomos, mert **időben eltolva üt**: a callbacket a `PlayScreen`
teszi bele játék közben, a hiba viszont a KÖVETKEZŐ szobanyitáskor jön — így
véletlenszerűnek látszik, és az első parti még hibátlanul lefut.

Ha egy játéknak fel kell szólnia a `PlayScreen`-hez, az **prop**, nem `gameMeta`:
a `GameContent` már így adja tovább a `drinkMult`, `onLiveDrinkUpdate`,
`onSetHideFooter` mezőket. Új visszahívásnál ezt a sort bővítsd.

Két védőháló, ami ezt őrzi:
- `sanitizeForFirestore` kidobja a függvény-mezőket (a kulcs eltűnik, nem `null`
  lesz — egy `null` felülírna egy valódi mezőt)
- a `tests/fbstub.js` a valódi Firestore-ral azonosan **dob** függvényre is, nem
  csak `undefined`-ra. Amíg ez hiányzott, a hiba MINDEN teszten átment, és csak
  éles eszközön bukott ki.

Teszt: `node tests/roomcreate_fn_test.js` — a sanitizer viselkedése, és a valódi
repró: egy végigjátszott meccs UTÁN is nyitható új szoba.

## Fontos szabályok
1. Minden commitnál verzióbump kötelező (az `app.src.html`-ben!)
2. Kódot CSAK az `app.src.html`-ben szerkessz, majd `node build.js` (lásd BUILD WORKFLOW fent)
3. Nagy változásoknál Python patch script (`patch_5_XX.py`)
4. Assert-ekkel ellenőrizni a string replacement-et
5. `align-items:stretch` a footer rowon → egyforma magasság
6. Pill variánsok stabil `flex:1, minWidth:0, overflow:hidden` wrapperben

## Lóverseny: tartomány a fejlécben, és a tét is szorzódik (v10.299)
Két dolog változott együtt, és csak együtt van értelmük.

**A fejléc-korong TARTOMÁNYT mutat**, nem az éppen beállított tétet:
`stakeOf(meta, létszám) → [0, 6 × létszám]`, felszorozva a nehézséggel és a
wildcarddal. Az alsó határ 0, mert a **nyertes nem iszik**; a felső azért `6 ×
létszám` és nem 6, mert a vesztes a **saját tétjén felül a nyertesek kalapjából
is kap** — szélső esetben rajta kívül mindenki nyer 6-tal, és mind rá öntik.
A `stakeOf` **második paramétere a játékosszám** — ez az egyetlen ilyen a
mezőnyben, a többi csak a `gameMeta`-t nézi.

Korábban az élő tétet mutatta (`onBetUpdate` → `loversenyBet`). Az azért bukott,
mert a fejléc mást ígért, mint amennyit a játékos végül ivott. **A csatorna
megszűnt** — ha visszahoznád, előbb a kalapot is oldd meg.

**A tét szorzódik**: 2 korty nehéz szinten 6. A `scale=1` kivétel megszűnt az
`advanceLoverseny`-ben. Ami könnyen elromlik: a játék MINDENT nyers kortyban
tart (tét 1–6, ajándék a kalapból), a `drinkMult` csak a KIJELZÉST skálázza
(`shown()`, a `PlayerDrinkRow` `drinkMult`-ja), a könyvelés pedig egyszer szoroz
az `advanceLoverseny`-ben. **Ha itt is szoroznál az `onAdvance` számaiba,
duplán menne fel.** A léptető szándékosan nyers marad (1–6): a szorzót a
léptető alatti mondat írja ki (`6 kortyot (2 × 3)`).

Teszt: `node tests/diffmult_test.js` 3. blokkja — mindenki ugyanarra a lóra tesz
1/2/3-at, és a **vesztes ágra játszik rá** (addig újrapróbálja a futamot, amíg
megkapja): nehéz szinten `[3,6,9]` kerül fel. Ha ez a retry kikerül, a teszt
némán üresen fut át — az első változata pontosan így csúszott át.
A tartományt a `stake_test.js` 6. blokkja őrzi (2/3/5/6 fő → 12/18/30/36).

## Gombfeliraton NINCS pipa (v10.300)
Díszítő pipa (`✓` / `✔`) **egyetlen gomb feliratára sem** kerül — se elé, se
mögé. Ez húsz helyen élt („Ki osztom ✓", „Tét megerősítése ✓", „✓ Kitalálták",
„Senki nem rontott ✔", „N ember iszik ✔"…), és mind kikerült: a gomb szövege
önmagában mondja meg, mi történik.

Ami MARAD, és nem tévesztendő össze ezzel — ott a pipa nem dísz, hanem **maga az
állapot**:
- bevásárlólista-elem négyzete (`toggleCartItem`) — a pipa a „kipipálva"
- kvíz bónusz-tipp gombjai — a pipa a *saját választásod* és a *helyes válasz*
  jelölése; nélküle nem látszana, mit tippeltél

Szintén maradnak a `✅` **emoji** felületek (RSVP „✅ Jövök", „✅ Élő" állapot) —
az másik vizuális nyelv, nem ez a gombtípus.

## Lóverseny: kiosztás után (v10.300)
A „Ki osztom" megnyomása három dolgot csinál egyszerre, és ezek együtt járnak:
1. **a gomb eltűnik** (`!acceptedDistribution` a feltételében),
2. **a nyertesek kiesnek a listából** — csak az marad, akinek innia kell,
3. **a léptetők eltűnnek** (`readOnly`), mert már nincs mit osztani.

A megmaradt sor a **teljes** mennyiséget mutatja: `bet + given`, nem csak az
ajándékot. Ez a lényeg, amit könnyű elrontani — kiosztás előtt a sor szándékosan
csak az ajándékot lépteti (`cnt={given}`, a tét a jobb oldali chipben van), de
utána az a vesztes, aki nem kapott ajándékot, `0`-val szerepelne, holott a saját
tétjét meg kell innia.

Teszt: `node tests/drinkrow_unified_test.js` utolsó blokkja — kiosztja a teljes
kalapot, megnyomja a gombot, és mind a négyet ellenőrzi (sorszám csökken, gomb
eltűnt, léptetők eltűntek, egyetlen gomb feliratán sincs pipa).

## Szólánc létra: egy csip = egy szó (v10.301)
Az átadó-lap csíkja **`SZ_MAX_LEN` (=10) csipből** áll, és a beteltek száma
PONTOSAN a jelenlegi szószám — ugyanaz, ami a jelvényen áll (`4 SZÓ` → 4 csip).
Mind a betelt csip **a fokozat színét** viszi (`tone.badge`), egyetlen színnel.

Amit ez javított, és amit könnyű visszacsinálni: a létra korábban a SZINTEKET
mutatta (`i + 2`, tehát `MAX_LEN - 1` = 9 szakasz, 2-től indexelve), a már
teljesített szakaszok pedig a TÉMA színét vitték (`T.mint` — ez nem minden
témában zöld, világos témán kék), a jelenlegi meg a fokozatét. Így 4 szónál
**„2 kék + 1 zöld"** állt: se a csipek száma nem egyezett a jelvénnyel, se a
színük egymással.

A gyökér-ok az volt, hogy **v10.289** a kezdést 2→1 szóra és a maximumot
12→10-re vitte, de a létrát (és a tesztet, és ezt a doksit) nem igazította
utána. Ha a kezdő szószám megint változik, a létra `i + 1`-es indexelését
ellenőrizd.

Teszt: `node tests/szolanc_test.js` 4. blokkja — csipszám, betelt szám ÉS az
egyetlen szín. A régi létrával mind a három bukik.

## Kisebb/Nagyobb: fejléc-korong és a két fő gomb (v10.302)
**A korong tartományt mutat**, nem a KÖR gyűrűt. A játék korábban `stake:null`
volt (v10.276 „határtalan halmozók" csoportja), ezért a fejlécben a körszámláló
állt — pedig a felső határ kiszámolható.

A tét 1-ről indul, minden jó tipp után **+1** (alap) vagy **×2** (`stackMode`),
bukásnál a játékos a *pillanatnyi* tétet issza, majd a tét nullázódik. Ebből:
- **+1 mód** — a pakli szab határt: `[1, 52 × decks]`. Ez PONTOS.
- **×2 mód** — a valódi plafon `2^(lapok−1)`, ami sem kiírható, sem értelmes
  ígéret. Ezért a kijelzés a `KISEBB_X2_DOUBLINGS = 8` **gyakorlati plafonon**
  áll meg (256). Ez tudatosan választott szám, nincs játékbeli megfelelője —
  nyolcnál hosszabb hibátlan sorozatnál a korong ALULMOND. Ha valaha pontos
  akar lenni, a játékban kell tétplafont bevezetni, nem a korongon szépíteni.

**A két fő gomb EGY sorban van** (`flexDirection:'row'`, `flex:1`), magasságuk
marad 100 px. Fél szélességen a régi 26 px-es felirat + 38 px-es háromszög nem
fért ki, ezért 22 / 28, és `whiteSpace:'nowrap'` tiltja a tördelést — enélkül a
„Nagyobb" két sorba törne 360 px-es kijelzőn.

Teszt: `node tests/stake_test.js` 6b. blokkja — 1 pakli / 2 pakli / nehéz / ×2,
és a két gomb egy sorban, 100 px-en, törés nélkül.

## Ország-Város: szavazat-index és a kétjegyű betűk (v10.303)
**Minden szó KÜLÖN értékelhető.** A `hostVote` / `submitVote` sokáig index
nélkül képezte a kulcsot (`ovfjVoteKey(round, pid, cat)`), miközben a sorok és a
pontszámítás index-szel olvasnak. Következmény: bármelyik szó gombja a 0. szó
kulcsára írt, a 2.+ szavakra pedig „senki nem szavazott" állt — és a
`finishVoting` szabálya szerint (`vals.length === 0 || yes > no`) azok
**automatikusan pontot értek**. Az `ai` indexnek végig kell mennie az
`onVote(pid, cat, yes, ai)` láncon.

**Ahol két kezdet is jó, két különböző szabály él — ne keverd össze őket:**
- **kétjegyű** (`OVFJ_DIGRAPHS`): `NY` → „nap" és „nyár" is jó;
- **ékezetes pár** (`OVFJ_PAIRS`, v10.307): `a↔á e↔é i↔í o↔ó ö↔ő u↔ú ü↔ű`.
  Itt a szabály **KÉTIRÁNYÚ**: `O` alatt az „óra" is ér, és `Ó` alatt az „orr"
  is. A címke a pár mindkét tagjánál ugyanaz („O / Ó").
  Az `o` és az `ö` **nem pár** (ahogy az `u` és az `ü` sem): külön betűk, nem
  hosszú/rövid változatok — `Ö` alatt az „orr" nem ér.

A **digráf egyirányú, az ékezetes pár kétirányú** — ez szándékos különbség.
`N` alatt a „nyár" nem ér (a szűkebb kör nem olvadhat bele a tágabba), `O`
alatt viszont az „óra" igen: az `o` és az `ó` ugyanaz a hang, a játékos nem
azon bukjon, hogy melyik ékezetes alakra gondolt. A felület
ugyanazt mondja, amit a szabály: `ovfjLetterPair()` mindkettőt kiírja („N / NY”,
„O / Ó”), és a sorsoló animáció ilyenkor kisebb betűmérettel rajzol, hogy
beférjen.
Az `X` és az `Y` eleve nincs az `OVFJ_LETTERS`-ben.

**Egy szavazó-nézet, három hívási hely.** Az `OVFJVotingView`-t a host, a
telefon és (v10.303 óta) a host kör végi „Mit írtak?" panelje is rendereli — az
utóbbi `readOnly`-val, ami az értékelő gombokat rejti, de a szavazat-számlálót
és az érvényesség-jelölést meghagyja. A `tallies` a telefonon is megy: az adat
ugyanabban a szoba-pillanatképben ül (`ovfjV<pid>` mezők).

Teszt: `node tests/ovfj_vote_test.js` — a „TÖBB SZÓ" blokk a szavazat-indexet
őrzi (a javítás nélkül a 0. szó kulcsára megy és az ELSŐ szó gombja jelölődik),
az „EGY FORRÁS" blokk pedig azt, hogy egyetlen komponens-definíció van.

**A szószám körönként állítható** (v10.304): az `OVFJLimitPicker` a lobby mellett
a host kör végi lapján is kint van (`round < totalRounds`). Az `answerLimit`
lemegy az `ovfjState`-be, tehát a telefonok a következő körtől azzal dolgoznak.

Teszt: `ovfj_vote_test.js` „BETŰPÁROK" blokkja (22 eset, mindkét irány) és
`ovfj_sync_test.js` 1b. blokkja — az végigviszi az első kört, és a host kör végi
lapján ellenőrzi a három csempét, a szószám-választót és a „Mit írtak?" panelt
(utóbbiban NINCS értékelő gomb — `readOnly`).

## MENÜ → Vezérlés panel (v10.308)
Fentről lefelé: **vezető-fejléc → szobakód-kártya → NÉGY gomb EGY sorban →
„Játékos hozzáadása" (teljes szélesség) → Kilépés**.

Amit könnyű visszacsinálni, mert korábban másképp volt:
- a négy gomb **egy sorban** áll, nem 2×2 rácsban;
- a szobakód sorában **nincs apró „+"** — a játékos-hozzáadás lent, teljes
  szélességben, ONLINE és OFFLINE partiban ugyanúgy (korábban online szobában
  csak a pici „+" volt, offline csak a széles gomb — két hely, egy funkció);
- a **Kilépés szöveges gomb** (átlátszó háttér), nem tömör menta sáv;
- a **vezető-fejléc** nem sárga kártya: a lap saját háttere viszi, és a
  pontszám függőleges elválasztó után, csillaggal áll.

**A színek témából jönnek** (`T.mint`, `T.bgSoft`) — a küldött design kék
felületei ugyanezek egy kék témában. Egyetlen kivétel az „Újra" gomb fix zöld
árnyalata (`#2E9E76`): enélkül a semleges háttértől nem vált el a letiltott
„Vissza"-tól. Zöld akcentusú témában emiatt az „Újra" és a „Következő" közel
kerül egymáshoz — ott az ikon és a felirat különbözteti meg őket.

Teszt: `node tests/gamectrl_test.js` — online ÉS offline partiban méri az
elrendezést (egy sor, négy külön háttér, nincs apró „+", sorrend, Kilépés).
A menü PORTÁLBA renderel, ezért a teszt esetenként újratölti az oldalt —
enélkül a második eset mindkét panel gombjait látná.

## Nyolc képernyő az új design szerint (v10.311)
Egy csomagban nyolc felület igazodott a küldött mockupokhoz. A mockupok az
**`ice` (Jéghegy) témában** készültek — ha összevetnéd őket, előbb állítsd át a
témát, különben a meleg alapértelmezés miatt minden színt eltérésnek látsz.
Az összehasonlító képek Playwrighttal, a **buildelt `index.html`-ből** készültek.

**Játékosok (üres).** Középre igazított kör-ikon jelvény + „Még nincsenek
játékosok". A régi nagy halvány `0` kikerült. A szaggatott kontúr a **körön**
van, nem a lapon: a kártya tömör fehér, mint a képernyő többi lapja. A
„Játékos hozzáadása" **körvonalas** — tömör mentaként ugyanolyan súlyú volt,
mint a lenti „Tovább a játékokhoz", és két elsődleges gomb állt egy lapon.
Az info-sávban a haladás-pöttyök **jobbra** mentek: elöl felsorolás-jelnek
látszottak, nem állapotjelzőnek.

**Zene Felismerés.** A bakelit lemez **kikerült**, helyette hanghullám, közepén
a fehér kör lejátszás-gomb — a sáv maga a gomb. A `ZENE_WAVE` **fix** minta (a
véletlen minden újrarajzoláskor más sávot adna), a `wavePulse` animáció csak
lejátszás alatt fut, és **nem a zene ritmusára** — a preview-hoz nincs analizer.
A „Lejátszás" innentől **szöveg-felirat**, nem tömör gomb, alatta `ZENE_TICKS`
pöttyös idővonal (a preview hossza ismeretlenül **30 mp**-nek számít).

**5 dolog.** Érem-ikon a „KATEGÓRIA" fölé, a gyűrű 11→**7 px**, az öt jelölő
`flex:1`-gyel **kitölti a sort** (fix 50 px helyett), és ívelt nyíl mutat rájuk,
amíg egy sincs bejelölve.

**Mit választanál.** A gyűrűs visszaszámláló helyett **vízszintes sor**
(vonal — ⏱ szám mp — vonal): a gyűrű 88 px-et vitt el a két laptól. A body-beli
„MIT VÁLASZTANÁL?" felirat kikerült (a fejlécben már ott van). Minden kérdés
**két emojit** visz (`ea`/`eb`) a kör-jelvénybe — új kérdésnél **mindkettő
kell**, fél párral a lapok elcsúsznak. Az A/B **sarok-fül**, ezért a szülőn
`paddingTop:12` van: a fül 10 px-szel a lap fölé lóg.

## Mit választanál: 100 kérdés (v10.312)
A bank 15-ről **100**-ra nőtt. A játék `gameIdx % hossz` szerint lapoz, tehát a
darabszám maga is működési kérdés: 15 kérdésnél egy hosszabb esten belül
visszajött ugyanaz a dilemma.

A `statsA` a „hányan választanák az A-t" — **kitalált szám, nem mérés**. A játék
egyedül a többségi oldal eldöntésére használja (`statsA >= 50`), és a felfedés
ezzel zárja a kört („a többséggel értettél egyet" / „kisebbségben voltál").
Ebből jön három megkötés, amit új kérdésnél tartani kell:
- **nincs 50** — ott a többség érzésre is döntetlen, és a záró mondat olyat
  állítana, ami nem igaz;
- **1–99 között marad** — a 0 és a 100 azt ígérné, hogy az egyik oldalt SENKI
  nem választja;
- **mindkét oldalon kell nyerő kérdés** — ha minden érték 50 fölött állna, a „B"
  soha nem érne pontot, és a játék egy kör után kiadná magát.

Az opciók **60 karakternél rövidebbek**: a 74 px-es kör-jelvény mellett ennél
hosszabb szöveg 360 px-es kijelzőn négy sorba törik, és kilóg a 118 px-es lapból.

Teszt: `node tests/mitval_test.js` — böngésző nélkül fut (a tömb sima
objektum-literál, a forrásból kiértékelhető), ezért a teljes bank átnézése
másodperc. Őrzi a darabszámot, a két emojit (megléte ÉS hogy a páron belül
különböznek), a `statsA` fenti három szabályát, az ismétlődés-mentességet
(kérdés-pár és opció-szöveg szintjén is) és a hosszkorlátot.

**Időpárbaj.** A cél-lap **`T.mint`**, nem `T.ink` — a fekete tábla
hibaüzenet-sávnak látszott. Céltábla-ikon, halvány koncentrikus körök,
„Minél közelebb, annál jobb!" pirula. A játékos-kártya `isUp` jelzővel mondja
meg, kinél van a stopper („Te következel" / „Várakozik"), és az indító gomb a
**téma mentája**, nem a játékos saját színe: sárga játékoson a fehér felirat
alig látszott.

**Kártyacsata.** A szaggatott kontúr a **dobózónára** költözött; a sor tömör
fehér, benne `CB_ROUND_TONE` színes korong + pontozott vezetővonal. A korong
színe a **kör sorszámát** jelöli, nem a tulajdonost — játékos-színnel mind az öt
sor egyforma lenne. A kéz **legyezőben** áll (a kiválasztott lap kiegyenesedik),
a lapok 36×48 → **46×62 px**, és a `CB_SUITS` jel az **értékből** jön, hogy
ugyanaz a lap mindig ugyanazt vigye. A színjel dísz: a játékban csak a szám számít.

**Szűrés.** A kategória chip-pirulákból **teljes szélességű sor** lett, színes
ikon-csempével és rádió-koronggal (`FILTER_CATS`); a nehézség **arc-ikonos**
kártya (`FILTER_DIFFS`). A három fokozat színe **FIX**, nem témafüggő: a
„zöld = könnyű, piros = nehéz" jelentés nem lehet kék.

**Játékmenet.** A nehézség és a játéksorrend **kompakt sor-kártya** lett
(`SetupPickCard`), egymás mellett, a részletek `SetupPickSheet`-en nyílnak; a
max körök saját dobozt kapott. A stat sáv (játékos / játék / perc) **marad**.
A „Nehézségi szintek" külön info-gomb megszűnt — a választó **maga írja ki** a
kortyszorzót (`DIFFICULTY_INFO[].mult`, `N× korty` chip). Ez nem elhagyható:
a szint fő hatása a szorzó, és a `diffEasyNote`-féle szövegek csak időzítőkről
beszélnek. A MÓDOK sorai fehérek, kör-ikonnal — a bekapcsolt mód korábban tömör
menta sáv volt, súlyosabb, mint a képernyő elsődleges gombja.

A `SetupPickSheet` sorai `role="radio"` + `aria-checked`-et visznek: a
kiválasztottságot a korong és a háttér mutatja, szöveges „MOST EZ" nélkül —
a jelölés így is megfogható géppel és teszttel.

Teszt: `node tests/setupflow_test.js` (három külön doboz, a két kompakt kártya
egy sorban, a választó kiírja mind a négy szintet a szorzóval, és pontosan egy
sor van bejelölve).

## Splash: a logó mögött nincs semmi (v10.313)
A nyitóképernyőn a logó **leérkezik, és megáll** — `impactDrop` + `impactSettle`,
más nem. A becsapódás-effektek kikerültek:
- **fehér villanás** (`#splash-flash` + `splashFlash`) — teljes képernyős
  felvillanás a becsapódás pillanatában,
- **lökéshullám-gyűrűk** (négy `.splash-shock` + `splashShock`) — a logó mögül
  kifutó körök,
- **fényudvar** (`impactGlow` indulásnál, `splashLogoIdle` 2,3 mp után
  végtelenítve) — a logó körüli lüktető glow.

A logón most **fix** `drop-shadow` van, nem animált filter: ez árnyék, nem
fényjáték. Aki visszaállítaná, ne csak a keyframe-eket hozza vissza — a
`_startSplashAnim` időzítései és a témából jövő `glow`/`ring` színek is
kikerültek. A `--splash-ring` amúgy is halott volt: beállítottuk, de sehol nem
használtuk.

A felirat (`splashLetterSlam`) és a tagline (`splashTagline`) **marad** — azok
nem a logó mögött vannak, hanem alatta, és a szöveg érkezését jelzik.

## DNR exkluzív: hat játék (v10.314)
A jelölő a `GAMES[]` bejegyzésen a **`dnr:true`** mező — nem a `category`.
A kategória marad, ami volt (mind a hat `Csapat`); a DNR-státusz e mellé jön.
Aki `category:'DNR'`-t írna, az kiesne a saját kategória-szekciójából.

A hat játék: **blackjack, imposztor, kisebb, beerpong, powerhour, ovfj**
(a `busz` a hetedik, de az azonosítóval van bedrótozva: `g.id === 'busz' || g.dnr`).

A jelölő két helyre megy le, és sehova máshova:
- a Szűrés `DNR Exkluzív` sora (`f === 'DNR'`),
- a kártyán a **★ DNR EXKLUZÍV** szalag.

Amit könnyű összekeverni: a `config/homeConfig.dnrAppsEnabled` kapcsoló **NEM**
ezekre vonatkozik. Az a főoldal alján lévő „TOVÁBBI DNR" sort kapcsolja
(`dnrAppsOn`, egyetlen helyen) — a DNR exkluzív játékok a listában attól
függetlenül ott maradnak.

## Kártyacsata, Mit választanál, Időpárbaj, Ritmus, Quiz (v10.315)

**Kártyacsata — a lerakott lap KISEBB.** A `CardChip` `small` propja 46×62-ről
30×38-ra viszi a lapot a kör-soron. A méret nem esetleges: a sor `minHeight`-ja
62 px, és a 30×38-as lap (+2 px keret, +2 px dobózóna-keret, +16 px sor-padding)
pontosan 62-t ad — **a sor magassága lerakáskor sem változik**. Ha a lap vagy a
paddingek változnak, a `minHeight`-ot utána kell igazítani, különben a sorok
megugranak lerakáskor.

**A lap visszahozható a kézbe** — kétféleképp, és mindkettő ugyanoda fut:
a soron kívül elengedve, vagy egyszerűen **rákoppintva** (a `pointerdown`
kezdőpontjához képest 6 px-nél kisebb elmozdulás = koppintás). A kéz
`sort((a,b)=>a-b)`-vel rendezve marad, különben a visszatett lap a legyező
végére ugrana. A kéz `justifyContent:'center'`.

**A tervező-lap fölött két sor** mondja el a szabályt és a tétet — enélkül a
képernyő egy nevet és öt üres sort mutatott.

**Mit választanál — az óra NEM indul a lap megjelenésével.** `started` állapot +
„Felfed & Indít" gomb, ugyanaz a minta, mint az Ötdolognál. A kérdés indulás
előtt **nem látszik**: ha látszana, a játékos elolvashatná, majd felkészülve
indítaná, és az óra semmit nem mérne. A választás már **nem** hív `startTimer`-t
(az meghosszabbította volna a kört).

**⚠️ Időpárbaj — alkomponens NEM mehet a törzsbe.** A `PlayerCard` és a `BigBtn`
a játék törzsében volt definiálva, ezért minden újrarendereléskor ÚJ
függvény-azonosságot kapott: a React nem frissítette a fát, hanem **leszedte és
újramountolta**, az avatar `<img>` pedig újratöltődött. Ez volt az „ugrálnak az
avatar képek". Mindkettő kikerült a komponensen kívülre
(`IdoparbajPlayerCard`, `IdoparbajBigBtn`), a `tgt` pedig **prop**, nem closure.
Új alkomponenst ne tegyél a törzsbe.

**Ritmus — van fejléc-korong.** Eddig `stake:null` volt („határtalan halmozók").
A vesztes a **pontkülönbséget** issza, és a pont `Math.max(0, …)`-szal 0-ra van
vágva, tehát a plafon a **nem-csapda felvillanások száma**. A `ritmusMaxDrinks()`
a játék saját ütemezéséből számol (900→380 ms láthatóság, 150→60 ms rés),
`(1 - trapChance)`-szal szorozva: 30 mp / 20% csapda → **1–32 korty**.
Ha a `spawnNext` tempója változik, ezt a függvényt is át kell vezetni.

**Quiz — a korty-kiosztó a KÖZÖS `PlayerDrinkRow`.** Kézzel lemásolt változat
volt benne: unicode `−`/`+` a korongos `BohIcon` helyett, saját színek, és
hiányzó `aria-label`. A `quiz_test.js` emiatt a `'+'` feliratra kattintott —
most `button[aria-label="Egy korttyal több"]`-re, mint a többi korty-teszt.

Teszt: `stake_test.js` (Ritmus három beállítással), `quiz_test.js`,
`drinkrow_unified_test.js`.

## DNR Pub: fix gombsávok, címkék, értékelő lap (v10.316)

**A két gombsáv PORTÁLBA megy.** A lista alján az „Új keverés" + „Receptek", a
részleteknél a „Szerkesztés" + „Értékelés" — mindkettő `ReactDOM.createPortal`
a `document.body`-ba, ugyanazzal a `bottom:'calc(-1 * env(safe-area-inset-bottom)
- 80px)'` számítással, mint a `DrinkForm` lábléce. Ez nem stílus: a `100dvh` és
az animált wrapper iOS PWA-ban elcsúsztatná a sávot a valódi képernyő-aljtól
(lásd `docs/safe-area.md`). A görgő terület alsó paddingja ezért
`calc(env(safe-area-inset-bottom) + 104px)` — enélkül az utolsó kártyát takarná.

A **„Receptek" szándékosan kicsi** (ikon + 11 px felirat): az elsődleges akció az
új keverés felvétele, a receptek csak egy átkapcsoló. Két egyforma súlyú gomb
korábban azt sugallta, hogy egyenrangúak.

**Fotó helyett címke.** A fotó-feltöltő kikerült az űrlapból, de az `image`
mezőt a mentés **visszaadja** — enélkül a korábban feltöltött képek az első
szerkesztéskor csendben eltűnnének. A címkék **kisbetűsítve és trimmelve**
tárolódnak (`addTag`), különben az „Édes" és az „édes" két külön címke lenne, és
a szűrő egyiket sem találná meg. A már használt címkék javaslatként megjelennek
(`tagSuggest`) — gépelés helyett egy koppintás, így nem szóródik szét a névtér.

**A tag-szűrő a típus-szűrő UTÁN fut**, tehát a kettő kombinálható („Shot" +
„édes"). Több kijelölt címkénél **MINDEGYIKNEK** szerepelnie kell az italon.
Az `allTags` egy forrás: a szűrő és az űrlap javaslatai ugyanabból dolgoznak.

**Az értékelés külön lapra került** (`ratingFor` → `SheetOverlay`). Korábban a
csillagok és a „ki vagy?" profil-választó a részletek kártyájába volt ágyazva:
a kártya minden megnyitáskor más magasságú volt, és a választó lejjebb tolta az
egész lapot. A lapon a csillagok csak akkor élők, ha már ki van választva a
értékelő — különben a pontszám nem tudná, kihez tartozik.

**A Törlés a szerkesztő lap aljára költözött**, megerősítéssel. A részleteknél
ugyanakkora súlyt kapott, mint a Szerkesztés, holott visszavonhatatlan.

**A kosárba tevés ikon lett**, a „Keverte:" sor jobb szélén. Teljes szélességű
gombként kettévágta a lapot a hozzávalók és az értékelések között.

## Kisebb/Nagyobb: observer nézet és élő korty-könyvelés (v10.317)

**A kortyok MENET KÖZBEN kerülnek fel.** Eddig csak a `finishGame` könyvelt, az
pedig kizárólag akkor futott le, ha a pakli elfogyott vagy egy játékos maradt —
ha a parti előbb lépett tovább, **minden rontás nyom nélkül elveszett**. Mostantól
minden rontásnál azonnal megy az `onLiveDrinkUpdate`, és a `finishGame` **csak a
győztes pontját** adja. Ha ott is osztanánk kortyot, minden rontás duplán számítana.

A két csatorna másképp skáláz, és ezt könnyű elrontani:
- **`onLiveDrinkUpdate` NYERS számot vár** (nem szoroz) → itt `failedPot * drinkMult` megy;
- **`onResult` maga szoroz** (`diffDrinks * wcMult`) → oda a nyers `failedPot` megy.
A fejléc-korong is szorzódik (`stake_test`: nehéz szinten 3–156), tehát a
kiosztott korty és a korong ígérete csak így marad szinkronban.

**A tipp AZONOSÍTÓT visz** (`kisebbGuess.ts`). Enélkül két egyforma tipp
(ugyanaz a játékos, ugyanaz az irány) ugyanaz a mezőérték lett volna, a Firestore
nem küldött volna újabb snapshotot — ez volt a „nem működnek a gombok". Ráadásul
a régi tipp bennragadt a mezőben, és a kör visszaértekor **magától lefutott
volna**. A host `lastGuessTsRef`-fel dobja a már feldolgozottat.

**A `kisebbTurn` bővült**: `card`, `lives`, `livesOn`, `activePids`, `remaining`.
Az observer enélkül nem tudta megmutatni, mire tippel az ember, és **nem látszott
az élet** sem.

**`KisebbCard` modul-szintű** — a host és az observer UGYANAZT a lapot rajzolja,
így a két képernyő nem tud elcsúszni egymástól. (És nem a komponens törzsében:
ott minden újrarenderelés újramountolna — lásd az Időpárbaj avatar-hibáját.)

A „Ki vagy?" képernyő a többi választóval egy nyelvet beszél: kör-ikon jelvény,
avataros sorok, chevron — nem tömör színes névgombok.

## Nyolc javítás: bannerek, rácsok, csapdák, PWA-kapcsolók (v10.318)

**⚠️ A banner ELŐBB jön, mint az advance.** A „Ki vagyok én" és az „5 dolog"
fordítva hívta: `onAdvance` → `onResult`. Az advance `gameIdx`-et válthat, a
`useEffect([gameIdx])` pedig `setGameResult(null)`-t hív — a banner így
kitörlődhetett, mielőtt megjelent volna. Új játéknál is EZ a sorrend:
**`onResult`, aztán `onAdvance`.** Mindkettő `winners`/`losers` tömböt is kap,
különben a banner csak a nevet tudja, az arcot nem.

**Szerencsekerék — a címke nem csúszhat a hub alá.** A `labelR` eddig fix arány
volt (`rad × 0.45` két játékosnál), a középső „PÖRGESS!" gomb viszont `46·k`
sugarú: két főnél a név pont alá került. Mostantól a `labelR` alsó határa
`hubR + címkeblokk/2 + 6` — ha a hub vagy az avatar mérete változik, ez
automatikusan követi.

**⚠️ Útvesztő — egy TÍPUSBÓL TÖBB is lerakható.** A kód önmagával került
ellentmondásba: a `TRAPS` a mezők ötöde (6×6-on 7, 7×7-en 10), a `canPlace`
viszont típusonként egyet engedett, és csak öt típus van. A lerakás így a
nagyobb pályákon SOHA nem telt be — a számláló „5 / 10"-en állt, a „Kész" gomb
pedig hazudott. A típusonkénti korlát került ki, nem a képlet: a `gamecfg_test`
azt őrzi, hogy a csapdaszám **kövesse a pályát**. Ha valaha visszajönne a
típusonkénti korlát, a `TRAPS`-ot is le kell sapkázni a típusok számára.

**Memória — a rács oszlopszáma a LAPOKBÓL jön**, nem a helyből. Az `auto-fill`
más párszámnál csonka utolsó sort hagyott. A `memCols` a négyzetgyökhöz
legközelebbi OSZTÓ: 8 lap → 4×2 · 12 → 4×3 · 16 → 4×4 · 20 → 5×4 · 24 → 6×4.
A kör végén **végeredmény-tábla** mutatja, ki hány párt talált — eddig csak a
győztes és a vesztes látszott, a köztük levők teljesítménye sehol.

**Kvíz — a vesztes is bekerül a bannerbe.** A kiosztás után `onResult` csak a
nyertest vitte (`drinks:0`, `losers` nélkül). Most `winners`/`losers` megy, és a
korty is: ha mindenki ugyanannyit kapott, egy szám áll a banneren, ha nem, a
`loseNote` sorolja fel nevenként — ugyanaz a szabály, mint a `givePenalty`-nél.

**PWA appok külön kapcsolhatók.** A `config/homeConfig.dnrApps` térkép
appokra bontva (`{ bar:false }`), a `dnrAppEnabled()` egy forrásból dönt.
A hiányzó mező **BE**-t jelent — egy régi config különben csendben mindent
elrejtene. A „TOVÁBBI DNR" sor akkor is elmarad, ha a mester-kapcsoló BE van,
de egyetlen app sincs engedélyezve (üres lapra vinne).

**Kártyacsata** — a kör-sor összege EGY lapnál is kint van (eddig csak 1-nél
többnél), és a `SetupPickSheet` sorai megkapták a 18 px vízszintes paddingot.

## Wildcard, dupla kör, Kategória, Tapper (v10.319)

**⚠️ A wildcard KÉT részre válik szét.** Az időzítő bármikor lejárhat — akár a
Ritmus közepén —, és a teljes képernyős popup ott elvágta a kört. A szétválasztás:
- a **SZABÁLY** (`activeWildcard`: felső sáv + hatás, pl. a dupla szorzó)
  **azonnal** életbe lép — ez csak megjelenik, nem szakít félbe semmit;
- a **POPUP** (`showWcPopup`, és a Szerencsekör bannere) csak a **következő
  átmenetnél** jön elő, a `commitRound` blokkjából, elsőbbséggel a körszámláló
  fölött (a kettő egymásra csúszna).

Ez a határvonal nem esztétikai: a `stake_test` azt őrzi, hogy dupla wildcard
alatt a fejléc-korong a TELJES szorzót mutassa (nehéz × dupla = 6). Ha a szabály
is az átmenetig várna, az a teszt — és vele a korong ígérete — elcsúszna.
A Szerencsekör **pontja** is azonnal felmegy (az csak állapot), csak a bannere
vár a popupra.

**Kivétel a magukban futó játék** (`isSoloGame` — Busz, Power Hour): ott nincs
átmenet, amire várni lehetne, ezért a wildcard szándékosan menet közben jön.
A `soloNowRef` követi az épp futó játékot. Ha ez a jelző elromlana, a Buszban
soha többé nem lenne wildcard.

**Dupla kör: a banner sem írhat „+1"-et.** A könyvelés régóta szorzott
(`points + pm[id] * wcMult`), a banner viszont **bedrótozott** `'+1'`-et
mutatott — a nagy kártyán és a kicsinyített sávon is. Dupla körben két pont ment
fel, a felirat meg mást állított. A szám mostantól a banner SAJÁT effektjéből
jön (`gameResult.effect === 'double' ? 2 : 1`), nem az élő `wcMult`-ból: egy már
lezárt banner különben megkapná egy későbbi kör szorzóját.

**Kategória: ki kezd.** A játék körbe megy, de sehol nem állt, kinél indul a sor
— a footer „most ő jön" pirulája a következő kört jelzi, nem a kezdést. A
`challenger` innentől prop, és a kategória-lap alatt egy sor mondja ki.

**⚠️ Tapper: a párost a HOST küldi le** (`tapperPair`). Az observer eddig
találgatta („az első más `id`-jű játékos"), a host viszont **véletlenszerűen**
sorsol ellenfelet. Kettőnél több játékosnál a kettő rendszeresen eltért: a
telefon a rossz névre írt (`tapperInput.<név>`), a host pedig sosem látta meg a
nyomást — ezért „csak a host képernyőn" ment a játék. A `tapperInput` NÉVVEL
kulcsolt, tehát a szinkronizált párosnak és a hosti névnek egyeznie kell.

## Ország-Város és a Büntetés pont-módja (v10.320)

**⚠️ Egy szavas módban az Enter NEM ment.** `lim === 1`-nél nincs `+` gomb és
nincs szó-chip sem (`lim !== 1 && saved.length > 0`) — az Enter viszont
meghívta az `addWord`-öt, a szó `saved`-be került, az input letiltódott
(„megvan mind"), és **semmi nem vette ki onnan**. A szó véglegesen bennragadt.
Innentől `lim === 1`-nél az Enter csak a következő kategóriára ugrik, és a
`disabled` sem kapcsol be (`full && lim !== 1`).

**Idő nélküli körben csak teljes lappal lehet beadni.** Nincs, ami lezárja a
kört, ezért a „Kész vagyok!" addig letiltott, amíg minden kategóriában megvan a
kért **darabszám** (`ovfjLimit(limit) || 1`) érvényes szó. Időzítős körben ez
NEM áll: ott az óra zár, és a félig kitöltött lapot is be kell tudni adni.

**A betűkészlet sima latin** (`A…Z`, Q/W/X/Y nélkül). A magyar készlet (Á, Ő,
CS, LY, TY, ZS…) túl sok játszhatatlan kört adott. Az **érvényesség szabályai
változatlanok**: az ékezetes pár továbbra is kétirányú (`O` alatt az „óra" is
ér), a digráf pedig egyirányú (`N` alatt a „nyár" NEM ér) — azok a húzott
betűtől függetlenül élnek, és a `ovfj_vote_test` őrzi őket.

**A host kihagyhatja magát.** A `HostPickScreen` régóta tud `onSkip`-et, az
Ország-Város csak nem adta át. Ha a host nem játszik, az írás fázisban nem
üres űrlapot kap, hanem a **haladást** (ki van kész) — a `hostPid === null`
ágakat a kód már eddig is kezelte.

## Büntetés: korty VAGY pont (v10.320)
A `PenaltyModal` kapott egy szegmens-váltót. A két ág ugyanazt a kiosztót
használja, csak más mezőbe ír: `drinks` vagy `points`. **A váltás nullázza a
kiosztást** — ami kortynak szánt 3-as volt, pontként mást jelentene.

A `givePenalty` `opts.kind`-ból dönt. Pont módban a kapók a banner **nyertes**
oldalára kerülnek (`drinks:0`, hogy a szám-oszlop ne írjon korty-számot), és a
modal saját címet ad („Ki kap pontot?") — a hívó „…ki igyon?" felirata ott
ellentmondana. Ami **nem** változott: a szám mindkét ágban ABSZOLÚT, se a
nehézség, se a wildcard nem szorozza (`docs/buntetes.md` 1. csapda).

Mindkét belépő (MENÜ → Büntetés, Wildcard → „Szabályszegő?") átadja a típust.

## 🌪 Szélvihar (Busz) — mikor sül el (v10.320)
A lánc ellenőrizve, `node tests/szelvihar_test.js`. Négy feltételnek EGYSZERRE
kell teljesülnie, különben csendben nem történik semmi:
1. **online szoba** (`roomCode`) — offline Buszban nincs;
2. a Busz beállításokban a **Szélvihar kapcsoló BE** (`buszConfig.szelviharEnabled`,
   alapból KI);
3. a játék a **`bus` fázisban** van;
4. van legalább egy **néző, aki NEM ül a buszon** (`busWatchers[pid]` igaz, és
   vagy nincs a `busRiders` között, vagy már `busRiderDone`). Ha senki nem nézi,
   az ütemező 45 mp múlva újrapróbál.

Az időzítés **3–10 perc** (`randomDelay`), tehát egy rövid teszt-partiban simán
elő sem jön — ez nem hiba. A `window.__szelviharTestDelay` erre való: az első
tüzelés idejét írja felül.

A gomb 3 mp-ig él a célnál, az esemény 5 mp után magától törlődik. A megnyomás
új útvonalat oszt ÉS a még úton lévő buszozókat visszateszi a startra
(`busRiderPositions[rid] = 0`), majd `szelviharAnnounce`-ot ír — arra ugrik fel
mindenkinél a popup.

## „Fradi - Grill" shot-sorozat a Pubban (v10.321)
Hét beépített DNR keverés (`FRADI_GRILL_SHOTS`, modul-szintű konstans a
`BarScreen` felett, a `DNR_MIXES`-be spreadelve). Egyetlen alap-arány, hét
ízvariáció: **csak a HELL és a Sió íze változik**, a Finlandia és a szóda /
citrom-lime nem — ezért a hét bejegyzés egy `.map()`-ből jön, nem hét kézzel
írt objektumból.

**Az arányok 1 literre vannak felszorozva.** A kapott alap
(250 Finlandia : 250 HELL : 250 Sió : 100 szóda) **850 ml**, tehát a szorzó
1,176 — így áll a recept **295 / 295 / 295 / 115 ml**-en, ami pontosan 1000 ml.
Ha az arány valaha változik, a négy szám összegének 1000-nek kell maradnia
(a `bar_fradigrill_test` ezt méri): a `serv:25` ezen a literen alapul
(1 liter ÷ 4 cl-es feles ≈ 25 adag), és a részletek lapján az adagszámláló
ebből skálázza a mennyiségeket.

**A címke KISBETŰS** (`FRADI_GRILL_TAG = 'fradi - grill'`). Az `allTags` és a
tag-szűrő is `toLowerCase()`-el dolgozik, egy nagybetűs változat külön címkévé
esne szét, és a szűrő egyiket sem találná meg — ugyanaz a szabály, amit az
űrlap `addTag`-je érvényesít a kézzel felvett italokra.

A **címkék a részletek lapján is kint vannak** (a jegyzet alatt, pirulákban).
Eddig kizárólag a lista szűrőjében látszottak, tehát a recept mellett sehol nem
derült ki, milyen címke alatt fut az ital.

Teszt: `node tests/bar_fradigrill_test.js` — a hét recept adata (1000 ml,
egyedi HELL+Sió páros, egy közös kisbetűs címke), a lista, a szűrés (a címke
nélküli Barack Attack / Bogyóbomba kiesik) és a részletek lapja.

## Pub: az értékelő lap alatt eltűnik a gombsáv (v10.322)
A részletek „Szerkesztés / Értékelés" sávja `ReactDOM.createPortal`-lal a
`document.body`-ba megy (`docs/safe-area.md` — iOS PWA-ban másképp nem tapad a
képernyő aljához). Emiatt viszont **magasabban ült, mint a fölé nyíló értékelő
lap**, és rácsúszott a csillagokra: a „HÁNY CSILLAGOT ÉR?" sort a sáv takarta,
és rá sem lehetett koppintani.

**Nem z-indexszel javítjuk.** A sáv a MÖGÖTTE lévő részletek laphoz tartozik —
aktívnak sem szabad látszania, amíg az értékelő lap nyitva van. Ezért
`{!ratingFor && ReactDOM.createPortal(…)}`: a lap alatt egyszerűen nincs sáv.
Ugyanez a minta bármelyik jövőbeli portálos sávra: ha lap nyílik fölé, a sávot
a lap állapota kapcsolja ki, nem a rétegsorrend.

A `SheetOverlay` alsó `calc(6px + env(safe-area-inset-bottom))` paddingja
változatlan — az a home indicatortól tartja el a tartalmat, a takarást nem az
okozta.

Teszt: `bar_fradigrill_test.js` „AZ ERTEKELO LAP" blokkja. A fogódzó a
**hit-test** (`elementFromPoint` a csillag-sor közepén), nem a geometria: a sáv
nem tolta el a tartalmat, csak ráfeküdt, ezért a „képernyőn belül van" ellenőrzés
a hibás verzión is átment. Az `elementFromPoint` viszont a sávot adta vissza.

## Pub: az értékelés visszavonható (v10.323)
Az értékelő lapon a saját pontszám törölhető — „Értékelésem törlése", a
csillagok alatt, és **csak akkor jelenik meg, ha a kiválasztott értékelő már
értékelt** (`mine > 0`). Nincs megerősítés: egy koppintással vissza is rakható
egy csillag, szemben az ital törlésével, ami visszavonhatatlan (az ezért maradt
a szerkesztő lap alján, megerősítéssel).

**A 0 csillag NEM visszavonás.** Az `avgOf` az értékek átlagát veszi, tehát egy
lementett 0 lehúzná az átlagot — „mindenki utálja" lenne belőle, holott a
játékos épp azt mondta, hogy nem akar véleményt adni. A mezőt tényleg ki kell
venni a térképből, ezt teszi az `unrate`.

**Beágyazott `FieldValue.delete()`, nem dotted path.** A `set({ [drinkId]:
{ [rater]: FieldValue.delete() } }, { merge:true })` alak azért kell, mert a
`update('id.rater')` a pontot MEZŐÚTKÉNT értelmezné — egy pontot tartalmazó
ital-id (a Firestore auto-id-k is bármit tartalmazhatnak) csendben rossz helyre
írna. A `set`+`merge` a kulcsokat szó szerinti mezőnévnek veszi; a `fbstub` is
így viselkedik.

Teszt: `bar_fradigrill_test.js` „AZ ERTEKELES TORLESE" blokkja. A fogódzó a
**store** (`window.__fbStore`), nem a felület: a kulcsnak el kell TŰNNIE
(`{}`), nem `0`-ra vagy `null`-ra állnia — a felületen mind a három egyformán
„nincs értékelés"-nek látszik, az átlagban viszont nem.

## Busz: mi fordult ezen a megállón? (v10.324)
A „Húzott lapok" sor pozíciónként **mindig csak az UTOLSÓ lapot** mutatja
(`busPositionDrawnCards`), mert a következő buszozó felülírja. Az előzményt
ezért külön térkép őrzi:

```
busPositionHistory[posIdx] = [{ c: lap, r: [{ id, ok }] }, …]
```

A megállóra koppintva a `BusStopHistorySheet` nyílik — **egy komponens**, mert a
host tábla és a nézőmód ugyanazt mutatja; két másolat elcsúszna egymástól
(ugyanaz a hiba, ami a korty-sornál négy változatot szült).

Három dolog, amit könnyű elrontani:
- **Egy húzás TÖBB buszozóhoz tartozhat.** Aki ugyanazon a megállón áll, mind
  UGYANARRA a lapra tippel, ezért az `r` tömb, nem egyetlen azonosító.
- **KÉT könyvelő hely van.** A host (`resolvePosition`) és a játékos-eszköz
  (`BuszPlayerView`, inline másolat) külön oldja fel a pozíciót — a
  `busPushHistory` hívást MINDKETTŐBE be kell tenni, különben a telefonról
  játszott kör nyom nélkül marad.
- **A `BUS_HISTORY_MAX = 12` nem esztétika.** A TELJES `buszState` újraíródik a
  `rooms/<kód>` dokumentumba minden lépésnél, tehát a történet minden eleme
  drágítja az összes további írást. A plafonnál a **legrégebbi** esik ki.

A jelvény (darabszám a lap sarkán) csak **1-nél több** előzménynél jelenik meg:
egyetlen bejegyzésnél a látható lap maga az egész történet, ott a jelvény
zajt csinálna. Nélküle viszont senki nem tudná, hogy van mit megnyitni.

A történet ott nullázódik, ahol a `busPositionDrawnCards` is: a busz indulásakor
és a **szélvihar** új osztásánál. (A `startBus` eddig egyiket sem nullázta —
egy újrajátszott parti a régi húzott lapokkal indult volna.)

Teszt: `node tests/bus_history_test.js`. A 2. blokk a lényeg: **végigjátszik**
három bukott tippet ugyanazon a megállón, és a `__fbStore`-ból olvassa vissza a
hármat — seedelt előzménnyel a renderelés akkor is átmenne, ha a könyvelés soha
nem írna semmit. A tipp-gombokra **várni kell** (bukás után 6 mp-ig áll az
eredmény-sáv); fix várakozással a 2. és 3. kattintás némán elveszne.

## Blackjack: a telefonos felület három képernyője (v10.325)
A küldött mockupok szerint igazodott a **csatlakozás**, a **tét** és az
**asztal**. Az összehasonlító képek Playwrighttal, a buildelt `index.html`-ből
készültek, a **`BlackjackObserverView`** közvetlen mountolásával (a szoba a
`fbstub` `__fbStore`-jában ül) — a teljes parti végigjátszása nélkül.

**Csatlakozás.** A három készlet-választó **EGY sorban**, csempeként (korsó +
szám + „KORTY" pirula). Egymás alatt, teljes szélességű gombként mindhárom
ugyanakkora súlyú volt, mint a képernyő elsődleges akciója. A kijelölést
**borostyán keret** viszi, nem menta: a menta a megerősítő gombok színe, itt
egy választás áll, nem egy akció. A pipa zöld **körbe** került konfettivel
(`BJ_CONFETTI` — a pozíciók FIXEK, véletlennel minden újrarendereléskor máshova
ugrálna a szemcse), és a blokk nyitánya vonal–korsó-medál–vonal.

**Tét.** A lap felső harmada `T.mintSoft`, benne a medál, a cím és a tömör
**„Készleted" sáv**. A −/+ **kör**, a szám keretes dobozban. Új a
**gyorsválasztó sor** (1/2/3/5 korty): ami nem fér a készletbe, az **le van
tiltva** — enélkül egy koppintással olyan tétet állítana be a játékos, amit a
`setMyBet` clamp-je (`Math.min(myChips, v)`) úgyis visszavág, és a felület
mást mutatna, mint ami ténylegesen bemegy.

**Asztal.** A poszton halvány ♣/♥ vízjel (`aria-hidden`, `pointerEvents:none`).
A lefordított lap háta **zöld mintás fehér kerettel** (`BJCardEl`) — a kékes hát
idegen testként ült az asztal zöldjén. A helyek **nem csempék**: kör-avatar,
a soros játékosnál arany gyűrű, a helyeket **függőleges vonal** választja el.
Az akciógombok **KÖRÖK, a felirat a kör ALATT** — a régi széles téglalapokon a
felirat mellett álló emoji négy gombnál (split is) kicsordult.

Két dolog, amit könnyű elrontani:
- **A `BJActionBtn` MODUL-szintű.** A komponens törzsében minden újrarenderelés
  új függvény-azonosságot adna, és a React leszedné-újramountolná a gombokat
  (ugyanaz a hiba, ami az Időpárbajnál az avatarokat ugráltatta).
- **Egy kéznél a pontszám a FEJLÉC sorában van**, split után marad kezenként.
  A kettőt együtt renderelve a szám kétszer jelenne meg.

Teszt: `node tests/bj_design_test.js` — az elrendezést méri, nem a színt: egy
sor / három vízszintes pozíció, a letiltott gyorsválasztó, a kör alakú léptetők
és akciógombok (négyzetes befoglaló + `50%` sugár), a felirat a korong alatt,
a fejlécbe került pontszám, és a csempe-háttér nélküli helyek elválasztóval.

## Éremdobás, Kártyacsata, admin XP-lap, Statisztika fülsor (v10.326)

**Éremdobás — a játék saját végképernyője nem szorzott.** „iszik 1-et" volt
bedrótozva, miközben az `onResult` ÉS a könyvelés is szoroz a nehézséggel:
nehéz szinten a banner 3-at mondott, a játék 1-et. A szám innentől a
`drinkMult` propból jön (a `GameContent` eddig nem adta tovább az éremnek).
A szöveg **„N kortyot"**, nem „N-et": a magyar toldalék számonként más
(1-et / 3-at / 5-öt), a „kortyot" viszont mindegyikkel jó.

**Kártyacsata — a kör-sor az ÖSSZEGET mutatta egy lapon.** Aki két lapot rakott
egy körre, annál a 3+4-ből egyetlen „7"-es chip lett — egy nem létező lap.
A `results` mostantól a lapokat is viszi (`p1c` / `p2c`), és a sor minden
lerakott lapot külön chipben rajzol; egynél többnél az összeg **pirulában** áll
mellettük (`=25`). A tét-oldal tükrözve van: balra lapok→összeg, jobbra
összeg→lapok, hogy a két oszlop a középső jel felé fusson.

**Admin: „Büntetés" fül → „XP & Szint".** A büntetés-lista funkciója rég más
(a Büntetés-modal osztja a kortyot/pontot), ezért a fül kikerült. Helyette az
`AdminXpInfo` írja le, miből jön az XP — és a súlyokat **az `XP_W` konstansból
olvassa**, nem beírt számokból: különben a leírás csendben elcsúszna a
képlettől, amint a súlyok változnak. Ugyanígy a szint-küszöbök az
`xpForLevel()`-ből és a rangok a `LEVEL_BANDS`-ből jönnek.
Az `AdminPunishments` komponens **megmaradt** (a `config/punishments`
dokumentum és a `PUNISHMENTS_DEFAULT` is) — csak nincs rá belépő.

**Statisztika fülsor.** Négy fül (Profil / Játékok / Beerpong / Busz) + a Múlt
gomb 360 px-es kijelzőn már nem fért ki: előbb a „Beerpong" felirat vált
ellipszisre, aztán a sor kicsúszott. A fülek `flex:'1 0 auto'` + `minWidth:60`
— széles képernyőn kitöltik a sort, keskenyen megtartják az olvasható méretet,
és a **konténer görgethető vízszintesen**. A **Múlt a görgő sávon KÍVÜL** marad,
különben elgörögne a fülekkel.

Teszt: `node tests/erem_cardbattle_test.js` — az Érem mindhárom nehézségen
összeveti a játék végképernyőjét a **result bannerrel** (pont ez a kettő tért
el), a Kártyacsata pedig végigjátszik egy partit, ahol mindkét játékos MIND az
öt lapját az 1. körre teszi: ott kell tíz chipnek és két `=25` pirulának lennie.

## Csoportos ivászat: számlálódik, és a PARTI szintjét követi (v10.327)
**Igen, számlálódik.** A „Megiszom!" MINDEN játékos `drinks` mezőjét növeli
(`setPlayers`), a parti végén pedig ez megy fel a statisztikába
(`totalDrinks += p.drinks`) — ugyanaz a csatorna, mint a játékokban szerzett
kortyoké.

**A mennyiség viszont rossz forrásból jött.** A `currentGame.difficulty`
(`könnyű`/`közepes`/`nehéz`) adta az 1/2/3-at — az a **játék saját, statikus
címkéje**, nem a partira beállított szint, tehát extrém nehézségen ugyanannyi
kortyot osztott, mint könnyűn. Innentől a `DIFFICULTY_INFO[].mult` (1/2/3/5),
mint minden más korty-forrásnál. Pontosan az a keverés, amitől a v10.296
szakasz óv.

**A wildcard szorzó NEM játszik.** A csoportos ivászat nem egy kör eredménye,
hanem két kör KÖZÖTT felugró esemény — nincs mihez képest duplázni.

Az esemény 5–10 percenként sül el, és a popup nem játék közben jön: az ütemező
csak „esedékesre" állít, a felület pedig a **következő kör/játék** kezdete után
~1,8 mp-cel mutatja. Ezért egy rövid teszt-partiban elő sem jönne — a
`window.__groupDrinkTestDelay` írja felül az első tüzelés idejét (ugyanaz a
fogódzó, mint a szélviharnál).

Teszt: `node tests/groupdrink_test.js` — mind a négy szinten. A hordozó játék az
**Éremdobás**, aminek a kártyáján `könnyű` áll: a régi képlet így mind a négy
esetben 1-et adott volna, tehát a teszt tényleg a parti szintjét méri.

**A Büntetés marad ABSZOLÚT** — ott a játékos konkrét számot választ, és
pontosan annyi megy fel (`docs/buntetes.md` 1. csapda).

**Teszt-harness buktató, ami órákat tud elvinni:** a `PlayScreen`-t
`gameMeta.modes` NÉLKÜL mountolva a `trackScores` hamis, a könyvelés meg sem
történik, és a **Kövi gomb végig letiltott marad** (`active = !!pendingCommit`).
A mérés ilyenkor csupa nullát ad, és úgy néz ki, mintha a játék nem könyvelne.
Játék-tesztben `modes: ['points']` (vagy `['drinks']`) kell.

## ⚠️ Fix réteg + safe area: a felhúzás kioltotta a paddingot (v10.328)
Hét teljes képernyős `position:fixed` wrapper `top:'calc(-1 * env(safe-area-inset-top))'`
+ `paddingTop:'env(safe-area-inset-top)'` párost vitt. A kettő **eredője nulla**,
tehát a tartalom a **státuszsáv mögé** került. Böngészőben láthatatlan.

Ami elromlott tőle: a Busz „host játszik játékosként" nézetében a felső sáv a
**🎮 kijárattal** együtt a sáv alá csúszott — a játékos nem tudott visszalépni.
Helyesen `top:0` + `paddingTop:env(...)`: a háttér így is befest a sáv mögé
(a padding-terület a konténer hátterét viseli), a tartalom viszont alatta kezdődik.

**Miért tűnt néha jónak:** a gyökér konténer `slideIn` animációja `transform`-ot
használ, ami futás közben **tartalmazó blokkot** csinál a `fixed` elemeknek — a
0,35 mp alatt a felhúzás a már paddingelt héjhoz képest számít.

A pull-up NEM mindig hibás: ahol a padding *nagyobb* (`calc(env(...) + 20px)`),
ott szándékosan kompenzál (Profil-részletek, ünneplő overlay) — ezért a teszt a
**kioltó párosra** szűr, nem a felhúzásra.

A Busz játékos-nézet azonosító sávja ezen felül **sticky** lett: ez az egyetlen
kijárat azon a képernyőn, és sok játékosnál a „Kiosztott kortyok" lista
elgörgette.

Részletek és a szimulációs recept: `docs/safe-area.md` 6. szakasz.
Teszt: `node tests/safearea_test.js` 4. blokkja.

## BohTimer — a KÖZÖS visszaszámláló (v10.329, még nincs bekötve)
Ma **nyolc** külön időzítő-megjelenítés él: gyűrű (Ötdolog, Fingerit, Power Hour,
Csak egy szó, Ritmus, Tabu), vízszintes sor (Mit választanál) és pöttyös idővonal
(Zene). Mind ugyanazt csinálja, csak máshogy néz ki — és a gyűrűk **148–200 px**
magasságot esznek a játék tartalma elől.

A `BohTimer` mindhárom variánsa **30 px** (`BOH_TIMER_H`), és vízszintes:

```jsx
<BohTimer variant="bar|ticks|pill" total={30} left={12.4} label="Kör" paused={false} />
```

`total` / `left` **másodpercben**. A komponens **nem méri az időt**, csak
kirajzolja, amit kap — így ugyanaz a nézet szolgálja ki a host-oldali és a
Firestore-ból szinkronizált (observer) időzítőt is.

**⚠️ A három fokozat színe FIX, NEM témafüggő** (`BOH_TIMER_TONES`). Ez nem
esztétika: a `T.mint` a téma **akcentusa** (barackban `#E06030`, jégben
`#2070C0`), a `T.coral` pedig barackban `#F08060` — vagyis témából származtatva
a **vészjelzés VILÁGOSABB lenne, mint a nyugalmi állapot**. Ugyanaz a szabály,
mint a Szűrés nehézség-kártyáinál: a „zöld = van idő, piros = mindjárt lejár"
jelentés nem lehet kék.

**A `bar` variáns a LETELT időt rajzolja, nem a hátralévőt** — és a jobb végén
ott a jelölt „necces" zóna, amibe a mozgó fej beér. Fordítva (fogyó sávnál) a
zóna a bal szélre esne, pont a szám-csip alá. A sor végén a **kezdő időtartam**
áll (`/ 30 mp`) — az a léc, amihez a hátralévő szám méri magát.

Három apróság, ami könnyen elromlik:
- **A riasztás küszöbe az utolsó negyed, DE legfeljebb 5 mp.** Egy 60 mp-es
  körnél a negyed 15 mp lenne — ott a piros túl korán jönne.
- **A zóna szélessége UGYANAZ a küszöb** (`min(25%, 5/total)`), nem külön szám:
  így a zóna pontosan ott kezdődik, ahol a szám is pirosra vált. 20 mp-ig
  negyed, fölötte arányosan keskenyebb (30 mp → 1/6, 60 mp → 1/12).
- **A sávban a szám OPAK csipben ül.** Közvetlenül a sávra írva a végén a
  színes kitöltésre esne, és beleolvadna.

Teszt: `node tests/bohtimer_test.js` — a küszöbök, a fix színek (kontrollal:
barack témában a `T.coral` tényleg világosabb a `T.mint`-nél) és a 30 px.

## Busz: mióta megy a busz (v10.330)
A `BohTimer` **`pill`** variánsa, `elapsed` móddal — **felfelé** számol, `m:ss`
alakban. Csak a játék MÁSODIK felében jelenik meg (a `bus` fázisban, ahol már
ül valaki a buszon); a piramis alatt nincs.

Három helyen látszik, mindhárom UGYANAZT a számot mutatja: a host tábláján (a
lépés-számláló mellett), a nézőmód fejlécében és a buszozó játékos fejléc-sorában.

**⚠️ A kezdés időbélyege a SZOBÁBAN ül** (`busStartedAt`, a `startBus` írja ki),
nem eszközönként. Enélkül minden telefon mást számolna, és a később csatlakozó
0-ról indulna. A **ketyegés viszont helyi** (1 mp-es interval a `BusRideClock`-ban)
— másodpercenkénti Firestore-írás értelmetlen terhelés lenne.

Az eszközök órái között lehet eltérés, ezért a különbség **0-ra van vágva**:
egy előresiető telefon különben negatív időt mutatna.

**A felfelé számláló SEMLEGES színű.** Nincs határidő, amihez képest „kevés idő"
lenne — a zöld/borostyán/piros itt talált jelentést állítana. A `BOH_TIMER_TONES`
csak a visszaszámláló variánsokra vonatkozik.

Teszt: `node tests/bus_clock_test.js` — a `m:ss` alak, mindhárom felület, hogy a
piramisban NINCS óra, és hogy tényleg ketyeg.

## ⚠️ Blackjack: a telefon gyors koppintásai elvesztek (v10.331)
A tünet „az observernél nem működnek a gombok" volt. A Hit/Stand néha nem
csinált semmit — de **csak élesben, két készülékkel**.

**Az ok.** A telefon a LEGUTOLSÓ pillanatképből számolja a következő állapotot
(`bjDoHit(bj, …)`), a pillanatkép viszont csak a hálózati köridő (100–300 ms)
után ér vissza. Két gyors koppintás között a második még a RÉGI állapotot látta,
és a saját írása felülírta az elsőt — a lap nem jelent meg, a gomb „halottnak"
látszott. Lassan (1 mp-enként) koppintva minden működött, ezért tűnt esetlegesnek.

**A javítás — optimista visszhang jelölővel.** Minden írás `echoTok`-ot kap, a
telefon AZONNAL alkalmazza helyben (`bjAct`), és csak akkor engedi el, ha a SAJÁT
írása ért vissza. Ugyanaz a minta, mint a Kisebb/Nagyobb tipp-azonosítója.

**Bármelyik pillanatképre elengedni KEVÉS** — ez volt az első, hibás javításom:
az érkező pillanatkép lehet RÉGEBBI, mint amit már kiírtunk, és a visszhang
elengedése után a következő koppintás megint a régiből indul. Pont ez történik
két gyors koppintásnál.

Biztonsági háló: ha a saját írásunk soha nem ér vissza (a host közben felülírta),
4 mp után visszaállunk a szoba állapotára.

**⚠️ A hiba csak KÉSLELTETÉSSEL látszik.** A `fbstub` azonnal kézbesít, ezért a
`bj_race_test` maga tolja el a pillanatkép-kézbesítést 250 ms-mal. Enélkül a
hibás kód is átmegy — fejlesztés közben át is ment, kétszer.

Teszt: `node tests/bj_race_test.js` — lassú ÉS gyors koppintás-sorozat, két
mountolt készülékkel (host tábla + telefon) ugyanarra a szobára.

## Útvesztő: a csapda-leírás EGY forrásból (v10.332)
A leírás és a viselkedés két helyen élt, és el is csúszott:

| csapda | amit ÍRT | amit CSINÁL |
|---|---|---|
| 🧱 Fal | „3 lépés késés" | **5** lépés (3 megállás + 2 visszapattanás) |
| 🌀 Örvény | „2 mezővel visszadobja" | a pozíció NEM változik — **3** lépést veszít |
| 🔀 Teleport | „random pozícióra ugrik" | ez a **legenyhébb**: +1 lépés |

Innentől az `UTVESZTO_TRAPS` (modul-szintű, a `GAMES` tömb ELŐTT) hordozza a
`korty` / `delay` / `note` mezőket ÉS a `steps()` függvényt, ami **maga a
viselkedés** — a `buildAnim` ezt fűzi a sorba. A `delay` ugyanennek a hossza,
tehát a kiírt szám nem tud elszakadni attól, amit a játék csinál.

**Miért „lépés" a mértékegység?** A győztes az, akinek KEVESEBB lépése van
(`steps: seq.length`), tehát a késleltetés pontosan ennyi lépéssel ront. Nem
másodperc: az animáció tempója nem befolyásolja az eredményt.

A hatás **három helyen** látszik, mind ugyanabból a forrásból:
- a játék leírásában (`GAMES[].desc` — az info-lapon és a kártyán),
- az intró CSAPDÁK blokkjában (hatás + magyarázat),
- a **lerakó gombokon** — nem csak a kiválasztott alatt, hogy össze lehessen
  hasonlítani, mit érdemes hova rakni.

Teszt: `node tests/utveszto_traps_test.js` — a `steps()` hossza = a kiírt
`delay`, a konkrét számok, a leírás és a gombok.

## ⚠️ Fordított kör: a LEGACY result-alak kimaradt a cseréből (v10.333)
A Collect & Boom-ban a „Fordított kör" wildcard alatt a **könyvelés megfordult**
(a bombás kapott pontot, a többiek ittak), a **banner viszont a régi állást**
mutatta: „Sere csapta fel a bombát! · ISZIK". Két külön állítás ugyanarról a körről.

Az ok nem a játékban volt: a `PlayScreen` `onResult`-jában a csere kapuja a
`winners`/`losers` tömbre szűrt. A **legacy alak** — `{correct, playerName,
drinks, subtitle}` — egyiket sem viszi, tehát a feltétel hamis volt, és a banner
változatlanul ment tovább. A könyvelés (`advance`, `advancePaired`,
`advanceTeam`, `advanceLoverseny`) **mind** kezeli a reverse-t — ezért csúszott
szét a kettő.

**Ez 34 hívási helyet érintett (~15 játék)**, nem egyet. A kapu ezért most maga
normalizálja a legacy alakot (`playerName` + `correct` → egyelemű
`winners`/`losers`), ugyanúgy, ahogy a banner is teszi rendereléskor. Új játéknál
így nem kell erre gondolni — de a **teljes alak továbbra is jobb**: a legacy
alak csak EGY embert nevez meg, tehát a Collect & Boom bannere a többiek pontját
sosem mutatta. A `collect` ezért átállt `winners`/`losers`-re, és ezzel a
`onResult` → `onAdvance` **sorrend** is helyreállt (v10.318).

A `__wildcardTestEffect` fogódzó mellékesen javult: a `pool` kihagyja az éppen
aktív wildcardot, ezért egy újraidőzítésnél a kikényszerített effekt **magától
átváltott** volna másra. A teljes `WILDCARDS` listára is ránézünk, így a forced
effekt pinnelve marad.

Teszt: `node tests/wc_reverse_test.js` — a fogódzó a két állítás **egyezése**,
nem a konkrét oldal: aki a banneren nyertes, annak pontot kell kapnia és nem
ihat. Három blokk: `collect` fordított körben, `collect` wildcard nélkül
(kontroll), és a `mitval` — az **maradt legacy alak**, tehát az általánosított
kaput méri. A javítás előtt mindhárom blokk bukik.

## Időpárbaj: a saját telefonról is játszható (v10.334)
Ha a host egy laptop, a játékot addig senki nem tudta játszani — a stopper csak
a host képernyőjén volt. Most a szobához csatlakozott telefon kiválasztja, hogy
ki ő (`IdoparbajObserverView`, ugyanaz az avataros „Ki vagy?" választó, mint a
Tappernél), és onnan indít/állít.

**⚠️ A stopper a TELEFONON fut, nem a hoston.** Ez a döntő különbség a
Tapperhez képest: ott a telefon csak a nyomva tartás tényét küldi, és a hoston
fut az óra. Itt a **mért idő maga a játék**, 0,1 mp felbontással — egy 100–300
ms-os hálózati köridő indításnál ÉS megállításnál is torzítana, tehát ~0,5 mp-et
hazudna. Ezért a telefon helyben mér, és **csak a kész eredmény** megy fel
(`idoInput.<pid> = { st:'done', t, tok }`).

Ugyanezért a telefon a **saját helyi állapotából** rajzol (`localRun`), nem a
szoba fázisából: különben az „Indítás" után a „Stop" csak a pillanatkép
visszaérésekor jelenne meg, és a mérés első negyed másodpercében nem lehetne
megállítani. (Ugyanaz a lecke, mint a Blackjack optimista visszhangjánál.)

Két dolog, ami a többi szinkron-játékból jön, és itt is kell:
- **A párost a HOST küldi le** (`idoState.p1/p2`) — az ellenfelet a `PlayScreen`
  véletlenszerűen sorsolja, a telefon nem tudja kitalálni (ez volt a Tapper
  v10.319-es hibája);
- **minden bemenet jelölőt visz** (`tok`), és a host `seenTokRef`-fel dobja a
  már feldolgozottat. Enélkül ugyanaz a bemenet a következő pillanatképnél újra
  lefutna, sőt a kör visszaértekor magától elsülne (`kisebbGuess.ts` mintája).

A cél-lap **egy komponens** (`IdoparbajTargetCard`) — a host tábla és a telefon
ugyanazt rajzolja.

Teszt: `node tests/idoparbaj_phone_test.js` — két mountolt készülék (host tábla
+ telefon) ugyanarra a szobára, **250 ms-os mesterséges pillanatkép-késéssel**.
A fő fogódzó: egy 1,5 mp-es tartás után a szobában is 1,5 mp áll, nem 2,0.

## ⚠️ A `db` NEM látható az app szkriptjéből — a telefonos írások némán elhaltak (v10.334)
A `var db = firebase.firestore()` a Firebase-init **IIFE-jében** ül, egy külön
`<script>` blokkban. Az alkalmazás a `<script type="text/babel">` blokkban van,
onnan a `db` egyszerűen nincs hatókörben.

Öt helyen bare `db`-vel írtunk, mindegyik `typeof db === 'undefined'` őrzővel —
**az őrző mindig igaz volt**, tehát a függvény visszatért, és a telefon írása
nyom nélkül elveszett. **Nem volt hibaüzenet**, ez tette láthatatlanná.

Mérve: a `TapperObserverView`-ban egy valódi lenyomás után a szoba
`tapperInput` mezője `undefined` maradt. Érintett volt a **Tapper** (mindkét
irány) és a **Kisebb/Nagyobb** telefonos tippje is.

Ami MŰKÖDÖTT, és ezért nem tűnt fel: a `bjWrite` (Blackjack) és a `syncRoom` /
`subscribeRoom` — azok `firebase.firestore()`-t hívnak közvetlenül, illetve az
init-IIFE-n belül vannak. Ezért ment a Blackjack telefonról, a Tapper nem.

Innentől minden szoba-írás a **`bohRoomRef(code)`**-on keresztül megy. Aki új
telefonos írást ír, azt használja — bare `db`-t ne.

Teszt: `idoparbaj_phone_test.js` 6. blokkja. A fogódzó a **hiba aláírása**:
egyetlen `typeof db === 'undefined'` őrző sem maradhat a forrásban.

## ⚠️ Alkomponens a törzsben = minden rendereléskor ÚJRAMOUNT (v10.335)
Bejelentés: „Tappernél ugrálnak az avatarok. Mindig ráfrissül."

Ha egy alkomponens a szülő **törzsében** van definiálva, minden
újrarendereléskor ÚJ függvény-azonosságot kap. A React ezt **más
komponens-típusnak** látja: nem frissíti a meglévő fát, hanem leszedi és
újramountolja — az avatar `<img>` pedig ezzel együtt újratöltődik.

A Tappernél ez látható is: a visszaszámláló `setInterval` **40 ms-onként**
ketyeg, tehát másodpercenként 25-ször épült újra mindkét tábla.

**Ez már harmadszor jött elő** (Időpárbaj v10.315, Blackjack v10.325), ezért
most az összes olyan hely javult, ahol alkomponens ült a törzsben, JSX-ként
használjuk, ÉS a szülő gyakran renderel:

| hely | ütem | mi lett belőle |
|---|---|---|
| `TapperGame` `Btn` | 40 ms | `TapperBtn` (modul-szint) |
| `KisebbGame` `LargeCard` | 600 ms | törölve — egysoros burkoló volt a `KisebbCard` körül |
| `BeerPongObserverView` `PlayerChip` | 1000 ms | `BpObsPlayerChip`, a `hydObs` a hívási helyre került |
| `KoPapirGame` `PlayerCard` | 3000 ms | `KoPapirPlayerCard` — **árnyékolta** is az azonos nevű, modul-szintű `PlayerCard`-ot |

**A döntő különbség nem a definíció helye, hanem a HASZNÁLAT.** A result-banner
`Pile` / `Metric` / `Row` szándékosan a renderen belül keletkezik, DE **sima
függvényként** hívjuk (`Pile({...})`), nem JSX-ként — a React így nem lát külön
típust. Ezek maradnak.

Teszt: `node tests/avatar_remount_test.js`. A fogódzó **nem a geometria**:
a `tapper_press_test` az avatar pozícióját méri, az újramountolt kép viszont
UGYANOTT jelenik meg, tehát az a teszt a hibás verzión is átment. Itt a
DOM-csomópontot jelöljük meg, és azt nézzük, megvan-e a ketyegés után — a hibás
verzión **0 / 2** élte túl. A 2. blokk forrás-szinten őrzi a többi helyet.

## Beer Pong: a DÖNTŐ, és a bajnokság utáni kísértet-push (v10.336)

**A döntő mindig EGY meccs, és saját pohár-száma van.** A „Visszavágó" kapcsoló
szövege szerint minden meccs két menetes — a megerősítő gomb viszont az egyenes
kieséses ágban a **döntőt is** automatikusan két menetre bontotta (`isSEFinals`
mellől hiányzott a döntő-kivétel). Új beállítás: `finalCups` (alapból =
`maxCups`), és a döntő kimarad a két menetből.

**⚠️ A döntő felismerése két naiv szabályt is megbuktat**, mindkettőt valódi
felálláson — ezért van a `isSEFinalMatch` bejárása:
- **„egy meccs van a körben"** → 3 játékosnál a **0. kör is** egy meccs (a
  harmadik szabadkártyát kap), utána viszont még jön a döntő;
- **„nincs következő kör"** → 2 játékosnál a bracket MINDIG épít egy üres
  (`tbd`) második kört, tehát a valódi döntő is „nem utolsó"-nak látszana.

A tényleges szabály: a döntő az a meccs, ami után **nincs kivel játszani** —
nincs másik függőben lévő meccs, és nincs későbbi körben várakozó (szabadkártyás)
játékos rajtuk kívül.

**⚠️ A kísértet-push.** A néző-képernyő az **első pillanatképnél is** értesített:
a feltétel `!prev?.bpNotif` volt, `prev` viszont a szoba React-állapota, ami
mountoláskor még `null`. Így a szobában ÜLŐ, régi `bpNotif` **minden
megnyitáskor újra elsült** — a bajnokság vége után is, amikor már nincs
következő meccs. Ugyanez állt a `roundEvent` / `gameEvent` / `bpTimerAlert`
eseményekre is (a régi eredmény-banner is felugrott).

Innentől az első pillanatképnél csak **megjegyezzük** az időbélyegeket
(`seenEvtRef`), és a bajnokság lezárásakor a két beerpong-esemény **törlődik is**
a szobából. Aki új szoba-eseményt vezet be: az `_fresh(kulcs)` kapun menjen át,
ne a `prev`-hez hasonlítson.

Teszt: `node tests/bp_final_test.js` — 2 és 3 játékossal (a két naiv szabály
bukó esetei), és a push-blokk egy **már bent lévő** értesítéssel nyit szobát.
A javítás előtt mind az öt állítás bukik, a push-blokk épp a bejelentett
szöveggel: „🏓 Következő meccs! | Sere vs Kecsi".

## „Játék indítása" — a gomb megvárja a hálózatot (v10.337)
Bejelentés: „ha túl gyorsan nyomom a játékmenet után a játék indítása gombot,
beragad a szoba létrehozása képernyő. Valaminek a letöltése/betöltése nem
történt meg."

Két ok, és a **második** magyarázza a beragadást:

1. A szobanyitás az **első Firestore-körforduló**. Indulás után pár tizedig a
   csatorna még épül (persistence, long-polling felderítés), tehát a legelső
   írás a leglassabb.
2. **⚠️ A `config/dbMode` figyelő `location.reload()`-ot hív**, ha az eszköz
   gyorsítótárazott teszt/éles beállítása más, mint a szerveren lévő. Ez a
   pillanatkép a betöltés UTÁN pár tizeddel érkezik — pont abba az ablakba,
   amikor a gyors felhasználó már a „Töltjük a szobát" képernyőn áll. Az
   újratöltés **elvágja a folyamatban lévő szoba-írást**.

A javítás három részből áll:
- **`window.bohNetReady` + `onBohNetReady(cb)`** (a Firebase-init IIFE-ben).
  Készre áll az első `config/dbMode` pillanatképnél (hibánál is), **vagy 8 mp
  után**. Az időkorlát nem elhagyható: offline is el kell tudni indulni.
- A **két „Játék indítása" gomb** (Játékok és Játékmenet) addig letiltva,
  „Betöltés…" felirattal.
- Az **újratöltés halasztott**, amíg a szoba-létrehozás fut (`window.__bohBusy`);
  utána magától lefut (`__bohPendingReload`). A dbMode-váltás ritka, egy
  folyamatban lévő parti-indítást nem szakíthat meg.

**A `PrimaryButton` `disabled`-je eddig CSAK kozmetika volt**: elszürkítette a
gombot és levette az `onClick`-et, de a DOM-ban a gomb aktív maradt — a
billentyűzet és a képolvasó használhatónak látta. Most valódi `disabled` +
`aria-disabled` megy ki. A `netready_test` 2. blokkja pont ezt fogja: a régi
kódon a szürke gombra kattintva **elindult a parti**.

Teszt: `node tests/netready_test.js`. A 3. blokk fogódzója egy **jelölő az
ablakon**: ha az oldal újratöltődik, a jelölő eltűnik. Van hozzá kontroll-ág is
— foglaltság nélkül tényleg újratölt, tehát a mérés nem üresen fut át.

## Pontgyűjtés nélkül: nincs banner, Állás fül és Büntetés (v10.338)
A „Pontgyűjtés" mód (`gameMeta.modes` → `'points'`) kikapcsolva a `trackScores`
hamis, és a **könyvelés meg sem történik**: az `advance` / `advancePaired` /
`advanceTeam` / `advanceLoverseny` mind változatlanul hagyja a játékosokat —
se pont, se korty nem kerül fel.

Három felület viszont úgy viselkedett, mintha kerülne:
- a **result banner** „+1 pont"-ot és korty-számot hirdetett;
- a **MENÜ → Állás** fül végig nullákat mutatott;
- **⚠️ a Büntetés gomb TÉNYLEG írt a játékosokra.** A `givePenalty` nem nézi a
  `trackScores`-t, tehát pontgyűjtés nélkül a büntetés volt az **egyetlen**, ami
  számolt. Ez nem csak zavaró volt: csendben adatot keletkeztetett egy olyan
  partiban, ahol a játékok maguk semmit nem könyvelnek.

A banner kapuja az **`onResult` elején** van, nem lentebb: így a hang, a konfetti
és a nézőknek küldött `gameEvent` is elmarad. A wildcard-sáv **„Szabályszegő?"**
gombja ugyanazt a `PenaltyModal`-t nyitja, ezért az is kimarad.

A játékos-hozzáadás után a menü az Állás fülre ugrott — pontgyűjtés nélkül az
nem létezik, ott a Szerkesztés a célállomás.

Teszt: `node tests/nopoints_test.js`. Két dolog nélkül üresen futna át:
- a **kontroll-blokk** (pontgyűjtéssel mindhárom felület ott van) — enélkül egy
  „mindent elrejtő" regresszió is átmenne;
- a **hajtó bizonyítása**: a kontrollban a bannernek FEL KELL jönnie, különben a
  „nincs banner" akkor is igaz lenne, ha a játék el sem indult volna.

## 5 dolog: PÁROS játék licittel (v10.339)
A soros játékos **licitál**: megmondja, hány odaillő szót vállal (3–8). Ha
összejön, ő kap pontot és az ellenfele iszik — ha nem, fordítva. A játék
`category`-ja `Egyéni` → **`Páros`**, tehát a `PlayScreen` sorsol ellenfelet.

**⚠️ Az időablak `licit × PER_WORD`**, és a `PER_WORD` szándékosan úgy van
beállítva, hogy **5-ös liciten pontosan a régi ablak** jöjjön ki (9 / 7 / 5 / 4
mp). Alapértelmezett liciten a játék tehát változatlan — csak a licit mozdítja.

**Miért arányos az idő, ha a licit így nem szorítja a játékost?** Mert magasabb
liciten nem az IDŐ fogy el, hanem az ÖTLET: nyolc szerszámot mondani akkor is
nehéz, ha van rá idő. A kockázat **tudás-alapú, nem tempó-alapú** — így extrém
szinten sem válik játszhatatlanná. A `OTDOLOG_MIN_WINDOW = 4` alsó korlát kell:
extrém szinten a 3-as licit 2,4 mp lenne, amibe bejelölni sem lehet.

**A licit VAK döntés**: a kategória a licitálás alatt még satírozva van. Ha
látszana, nem lenne tét — a játékos a kategóriát ismerve pontosan tudná, mennyit
vállalhat.

A jelölő-sor a licit szerint méreteződik (6 fölött 52 px és kisebb szám, hogy
nyolc is kiférjen 360 px-en).

Teszt: `node tests/otdolog_licit_test.js`. Az 1. blokk a `PER_WORD`-öt őrzi —
ha valaki átírja, a „régi játék 5-ös liciten" ígéret némán elveszne.

**A `gameorder_test` bannerelemzője javult**: sor helyett **bejegyzés**-alapú.
A több sorba tördelt bejegyzések (a `kisebb` a `stakeOf` miatt) nyitó sorában
nincs `banner:`, ezért a régi szűrő hiányzónak jelentette őket, holott ott a kép.
Ez a teszt **v10.302 óta volt tartósan piros** emiatt.
