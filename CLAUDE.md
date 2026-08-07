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
