# v10.352 - A DNR mod TULELI a kepernyo-valtast
#
# Bejelentes: „ha Jatekmenetrol visszalepek, akkor mindig a DNR felulet jon be,
# nem pedig az, ahol kivalasztottam a jatekot."
#
# ⚠️ AZ OK: a `BottleApp` a kepernyoket felteteles rendereléssel valtja
# (`{screen==='games' && <GamesScreen …/>}`), tehat a Jatekmenetre lepve a
# `GamesScreen` LEBOMLIK. Visszaterve uj peldany keletkezik, a `dnrMode`
# allapota pedig az alapertelmezesevel indul — ami a v10.348 ota `true`.
# Vagyis a felhasznalo kikapcsolta a modot, kivalasztotta a jatekokat, es a
# visszalepes csendben visszakapcsolta.
#
# A javitas MODUL-SZINTU emlekezet (`_dnrModeMemo`), nem localStorage — es ez a
# kulonbseg szandekos:
#   • modul-szintu: FRISS inditasnal marad a DNR alapertelmezes (v10.348), de a
#     parti kozbeni oda-vissza lepes megorzi, amit a felhasznalo beallitott;
#   • localStorage-ban tarolva egyetlen kikapcsolas utan SOHA tobbe nem nyilna
#     a DNR felulettel — az visszacsinalna a v10.348-at.
#
# A kiindulo ertek (`DNR_MODE_DEFAULT`) igy egy helyen all, es a memo is ebbol
# indul — ket kulon `true` konnyen elcsuszna egymastol.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. Modul-szintu emlekezet az isDnrGame melle ────────────────────────────
sub1(
"""function isDnrGame(g) { return !!g && (g.id === 'busz' || !!g.dnr); }""",
"""function isDnrGame(g) { return !!g && (g.id === 'busz' || !!g.dnr); }

// A DNR reflektor-mod kiindulo allapota (v10.348: a jatekvalaszto ezzel nyit).
const DNR_MODE_DEFAULT = true;
// ⚠️ MODUL-SZINTU emlekezet, mert a `BottleApp` a kepernyoket felteteles
// renderelessel valtja: a Jatekmenetre lepve a `GamesScreen` LEBOMLIK, es
// visszaterve uj peldany keletkezik. Enelkul a visszalepes csendben
// visszakapcsolta a DNR felületet arra, aki epp kikapcsolta.
// Nem `localStorage`: friss inditasnal maradjon a DNR az alapertelmezes —
// tarolva egyetlen kikapcsolas utan soha tobbe nem nyilna azzal.
let _dnrModeMemo = DNR_MODE_DEFAULT;""",
'dnrMode memo')

# ── 2. A kepernyo ebbol indul, es ebbe is ir ────────────────────────────────
sub1(
"""  // ⚠️ ALAPBOL BE (v10.348): a jatekvalaszto a DNR felulettel nyit, a teljes
  // kinalathoz a gombot KI kell kapcsolni. A mod a kepernyo allapota, nem
  // mentett beallitas — a `GamesScreen` kilepeskor lebomlik, tehat visszaterve
  // megint a DNR felulet jon fel.
  const [dnrMode, setDnrMode] = useState(true);""",
"""  // ⚠️ ALAPBOL BE (v10.348): a jatekvalaszto a DNR felulettel nyit, a teljes
  // kinalathoz a gombot KI kell kapcsolni. A kiindulo ertek a MODUL-SZINTU
  // emlekezetbol jon (v10.352), kulonben a Jatekmenetrol visszalepve — ahol a
  // kepernyo lebomlik es ujra mountolodik — visszakapcsolna magat.
  const [dnrMode, setDnrMode] = useState(_dnrModeMemo);""",
'dnrMode kezdoertek')

sub1(
"""  const toggleDnrMode = () => { const next = !dnrMode; setDnrMode(next); if (next) setActiveFilters([]); };""",
"""  const toggleDnrMode = () => { const next = !dnrMode; _dnrModeMemo = next; setDnrMode(next); if (next) setActiveFilters([]); };""",
'toggleDnrMode memo iras')

# A szuro is kikapcsolja a modot — az emlekezetnek AZT is kovetnie kell,
# kulonben a visszalepes a szuro utan is DNR-t nyitna.
sub1(
"""  const toggleFilter = f => { setDnrMode(false); setActiveFilters(fs => fs.includes(f) ? fs.filter(x=>x!==f) : [...fs, f]); };""",
"""  const toggleFilter = f => { _dnrModeMemo = false; setDnrMode(false); setActiveFilters(fs => fs.includes(f) ? fs.filter(x=>x!==f) : [...fs, f]); };""",
'toggleFilter memo iras')

sub1("const APP_VERSION = 'v10.351';", "const APP_VERSION = 'v10.352';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_352 alkalmazva')
