# v10.348 - A DNR felulet az ALAPERTELMEZES a jatekvalasztoban
#
# A jatekvalaszto megnyitaskor a DNR reflektor-modban all: a lista helyen a
# DNR exkluziv jatekok allnak, kedvenc-soros alakban. A teljes kinalathoz a
# DNR gombot kell KIkapcsolni (a gomb bekapcsolva arany, kikapcsolva sotet —
# tehat latszik, hogy egy bekapcsolt szurofele allapotbol lehet kilepni).
#
# ⚠️ EGY sor valtozik (`useState(false)` -> `useState(true)`), de a kovetkezmenye
# nem apro: mind az ot DNR jatek EGYEDUL jatszhato (`SOLO_IDS`), tehat a
# nyitokepernyon egymast kizaro jatekok allnak. Aki vegyes partit akar, elobb
# ki kell kapcsolja a modot. Ez tulajdonosi dontes, nem mellekhatas.
#
# A mod a kepernyo allapota, nem mentett beallitas: a `GamesScreen` kilepeskor
# lebomlik, tehat visszaterve megint a DNR felulet jon fel. Pontosan ezt jelenti
# az „alapbol".
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

sub1(
"""  // DNR reflektor-mod: a lista helyen CSAK a DNR exkluziv jatekok allnak,
  // kedvenc-soros (FavTile) alakban. Kolcsonosen kizaro a Szuressel — lasd a
  // `toggleDnrMode` / `toggleFilter` parost.
  const [dnrMode, setDnrMode] = useState(false);""",
"""  // DNR reflektor-mod: a lista helyen CSAK a DNR exkluziv jatekok allnak,
  // kedvenc-soros (FavTile) alakban. Kolcsonosen kizaro a Szuressel — lasd a
  // `toggleDnrMode` / `toggleFilter` parost.
  // ⚠️ ALAPBOL BE (v10.348): a jatekvalaszto a DNR felulettel nyit, a teljes
  // kinalathoz a gombot KI kell kapcsolni. A mod a kepernyo allapota, nem
  // mentett beallitas — a `GamesScreen` kilepeskor lebomlik, tehat visszaterve
  // megint a DNR felulet jon fel.
  const [dnrMode, setDnrMode] = useState(true);""",
'dnrMode alapbol BE')

sub1("const APP_VERSION = 'v10.347';", "const APP_VERSION = 'v10.348';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_348 alkalmazva')
