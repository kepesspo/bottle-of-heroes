# v10.359 - Orszag-Varos: a kortyok VEGRE felkerulnek, PLAFONNAL
#
# ⚠️ MERVE, nem feltetelezve. Egy vegigjatszott korben (host + egy telefonos
# valasz) a banner ezt irta: „Alfa: 3 korty", `drinks: 3`-mal — kozben a jatek
# EGYETLEN konyvelo hivast sem kuldott. Se `onAdvance` valodi terkeppel, se
# `onLiveDrinkUpdate`; a `onAdvance({})` egyszer fut, a legvegen, URESEN.
# Vagyis az Orszag-Varos kortyai SOHA nem kerultek fel a `players[].drinks`
# mezore, tehat a parti vegi statisztikaba sem.
#
# A csatorna az `onLiveDrinkUpdate`, mint a Kisebb/Nagyobbnal (v10.317): az a
# dokumentalt ut a jatek KOZBENI konyvelesre. A jatek sajat, belso korokben megy,
# tehat az `onAdvance` (ami kort leptet) nem hasznalhato ra.
#
# ⚠️ PLAFON (tulajdonosi dontes): a kod eddigi megjegyzese szerint „a teljes
# pontkulonbseg korty… tobb valasznal ez egy korben husz is lehet". Amig semmi
# nem kerult fel, ez nem latszott; elesitve viszont brutalis lenne. Ezert
# `OVFJ_MAX_DRINKS = 5` vagja le JATEKOSONKENT ES KORONKENT.
#
# ⚠️ HAROM helyen kell UGYANANNAK a szamnak lennie, kulonben a banner mast
# mond, mint amennyi felkerul:
#   • a konyveles      -> `n * drinkMult`  (az `onLiveDrinkUpdate` NEM szoroz)
#   • a banner szama   -> `n`             (az `onResult` MAGA szoroz)
#   • a felirat szamai -> `n * drinkMult` (kezi szoveg, nem megy at a szorzon)
#
# ⚠️ A LEGACY `playerName:null` alak SZANDEKOSAN MARAD. A konyveles az
# `onLiveDrinkUpdate`-en megy, amit a „Fordított kör" wildcard NEM fordit meg.
# `winners`/`losers`-t kuldve a BANNER megfordulna, a KONYVELES nem — pont az az
# ellentmondas, amit a v10.333 es a v10.354 javitott. Ez a tizedik legacy hivasi
# hely, es ez az egyetlen, amelyik nem no ki belole.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. A ket hianyzo prop a bekotesnel ──────────────────────────────────────
sub1(
"""   if (gameId === 'ovfj') return <OVFJGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={roomCode} gameMeta={gameMeta} onAdvance={onAdvance} onResult={onResult} />;""",
"""   if (gameId === 'ovfj') return <OVFJGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={roomCode} gameMeta={gameMeta} onAdvance={onAdvance} onResult={onResult} onLiveDrinkUpdate={onLiveDrinkUpdate} drinkMult={drinkMult} />;""",
'OVFJ bekotes')

sub1(
"""function OVFJGame({ players, gameIdx, onAdvance, onResult, roomCode, gameMeta }) {""",
"""// Korty-plafon JATEKOSONKENT ES KORONKENT. ⚠️ A jatek a teljes pontkulonbseget
// osztana ki kortyban, ami tobb valasznal egy korben husz is lehet — amig semmi
// nem kerult fel, ez nem latszott (v10.359).
const OVFJ_MAX_DRINKS = 5;

function OVFJGame({ players, gameIdx, onAdvance, onResult, roomCode, gameMeta, onLiveDrinkUpdate, drinkMult = 1 }) {""",
'OVFJ propok + plafon')

# ── 2. A konyveles + a plafon + az egyezo szamok ────────────────────────────
sub1(
"""    if (onResult) {
      const maxRs = Math.max(0, ...Object.values(rs));
      // Nincs kortyplafon, és ez SZÁNDÉKOS: a teljes pontkülönbség korty. Több
      // válasznál ez egy körben húsz is lehet — aki sokkal kevesebbet írt,
      // sokkal többet iszik. Ez a tét, nem hiba.
      const drinkParts = pl.filter(p => claimedPids.has(p.id))
        .map(p => ({ p, drinks: maxRs - (rs[p.id]||0) }))
        .filter(({drinks}) => drinks > 0)
        .sort((a,b) => b.drinks - a.drinks);
      if (drinkParts.length > 0) {
        const subtitle = drinkParts.map(({p,drinks}) => `${p.name}: ${drinks} korty`).join(' · ');
        onResult({ correct: false, playerName: null, drinks: drinkParts[0].drinks, subtitle });
      } else {
        onResult({ correct: true, playerName: null, drinks: 0, subtitle: 'Mindenki ugyanannyit kapott!' });
      }
    }""",
"""    const maxRs = Math.max(0, ...Object.values(rs));
    // A korty a pontkulonbseg — de PLAFONNAL. A `OVFJ_MAX_DRINKS` nelkul egy
    // sok valaszos kor husz kortyot is adhatna egy emberre.
    const drinkParts = pl.filter(p => claimedPids.has(p.id))
      .map(p => ({ p, drinks: Math.min(OVFJ_MAX_DRINKS, maxRs - (rs[p.id]||0)) }))
      .filter(({drinks}) => drinks > 0)
      .sort((a,b) => b.drinks - a.drinks);

    // ⚠️ A KONYVELES (v10.359). Eddig SEMMI nem kerult fel: a banner kortyot
    // igert, de a szam nem jutott el a `players[].drinks` mezoig, tehat a parti
    // vegi statisztikaba sem. A jatek sajat, belso korokben megy, ezert az
    // `onAdvance` (ami kort leptet) nem hasznalhato — az `onLiveDrinkUpdate` a
    // dokumentalt ut a jatek KOZBENI konyvelesre (Kisebb/Nagyobb, v10.317).
    // Az NEM szoroz, ezert ITT kell felszorozni.
    if (drinkParts.length > 0 && typeof onLiveDrinkUpdate === 'function') {
      const dm = {};
      drinkParts.forEach(({p, drinks}) => { dm[p.id] = drinks * drinkMult; });
      onLiveDrinkUpdate(dm);
    }

    if (onResult) {
      if (drinkParts.length > 0) {
        // ⚠️ A feliratban a MAR FELSZORZOTT szam all: ez kezi szoveg, nem megy
        // at az `onResult` szorzojan. Nyersen hagyva nehez szinten mast mondana,
        // mint amennyi felkerult (ugyanaz, mint az Ultimatum `loseNote`-jánál).
        const subtitle = drinkParts.map(({p,drinks}) => `${p.name}: ${drinks * drinkMult} korty`).join(' · ');
        // ⚠️ A LEGACY alak (nev nelkul) SZANDEKOS es marad. A konyveles az
        // `onLiveDrinkUpdate`-en megy, amit a „Fordított kör" wildcard NEM
        // fordit meg. `winners`/`losers`-t kuldve a banner megfordulna, a
        // konyveles nem — pont az az ellentmondas, amit a v10.333/354 javitott.
        onResult({ correct: false, playerName: null, drinks: drinkParts[0].drinks, subtitle });
      } else {
        onResult({ correct: true, playerName: null, drinks: 0, subtitle: 'Mindenki ugyanannyit kapott!' });
      }
    }""",
'OVFJ konyveles + plafon')

# ── 3. A leiras is mondja meg a plafont ─────────────────────────────────────
sub1(
"""desc:'Betűsorsolás, mindenki a saját telefonján tölti ki a 8 kategóriát.""",
"""desc:'Betűsorsolás, mindenki a saját telefonján tölti ki a 8 kategóriát. A kör végén a pontkülönbség a korty — de legfeljebb 5 egy körben.""",
'OVFJ leiras')

sub1("const APP_VERSION = 'v10.358';", "const APP_VERSION = 'v10.359';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_359 alkalmazva')
