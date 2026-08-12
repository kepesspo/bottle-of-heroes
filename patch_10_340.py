# v10.340 - Halott kod kivezetese: Buntetes-lista es app-design kapcsolo
#
# 1) BUNTETES-LISTA
#    A v10.326 kivette az admin fulet, de az egesz gepezet bent maradt:
#      • az `AdminPunishments` komponens (59 sor) — SEHONNAN nincs ra hivatkozas;
#      • a `PUNISHMENTS` valtozoba HAROM helyen irunk, es SEHOL nem olvassuk
#        (nincs `PUNISHMENTS[...]`, nincs `.map` / `.filter` fogyaszto);
#      • es indulaskor MINDEN alkalommal lefut egy Firestore-olvasas
#        (`config/punishments`), hogy feltoltse ezt a senki altal nem hasznalt
#        valtozot. Pont az indulas az, amit a v10.337-ben lassunak talaltunk.
#
#    A `config/punishments` DOKUMENTUM a Firestore-ban marad — kod nem torol
#    adatot. Csak nem olvassuk es nem irjuk tobbe.
#
# 2) APP-DESIGN KAPCSOLO
#    A `playful` mod megszunt, de maradt egy store feliratkozokkal, egy setter,
#    egy init-hook es egy `useAppDesign` hook — aminek NULLA hivoja van. A
#    `_setAppDesign` ráadásul mar konstans `'classic'`-ot ir felul, tehat a
#    feliratkozok soha nem sulnek el. Egy kapcsolo, aminek egy allasa van.
#
#    Vele megy a `config/homeDesign` harom hozzaferoje is (`getHomeDesign` /
#    `setHomeDesign` / `onHomeDesign`) — egyiket sem hivja senki.
#
# VISELKEDES NEM VALTOZIK. Ez tisztan takaritas: egy indulasi Firestore-olvasas
# es ~150 sor tunik el.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def cut(old, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, '')

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# --- 1a. a Firestore-hozzaferok ---------------------------------------------
cut("""  window.getPunishments = function() {
    return db.collection('config').doc('punishments').get().then(function(d) {
      return d.exists ? (d.data().list || null) : null;
    }).catch(function() { return null; });
  };
  window.setPunishments = function(list) {
    return db.collection('config').doc('punishments').set({ list: list }).catch(function(e) { console.warn('setPunishments', e); });
  };
""", 'getPunishments/setPunishments')

# --- 1b. a lista, a valtozo es a BOOT-OLVASAS -------------------------------
i = src.index('// Testreszabható büntetés-lista')
j = src.index('} catch(e) {}\n', i) + len('} catch(e) {}\n')
assert src[i:j].count('PUNISHMENTS_DEFAULT') >= 2 and 'getPunishments' in src[i:j], 'buntetes-lista blokk hatara'
src = src[:i] + src[j:]

# --- 1c. az AdminPunishments komponens --------------------------------------
i = src.index('// ── Admin: testreszabható büntetés-lista (nem teljesített feladatokhoz) ──')
k = src.index('function AdminPunishments()')
d = 0; m = src.index('{', k)
while m < len(src):
    if src[m] == '{': d += 1
    elif src[m] == '}':
        d -= 1
        if d == 0: break
    m += 1
assert 'PUNISHMENTS_DEFAULT' in src[k:m], 'AdminPunishments torzs'
src = src[:i] + src[m + 2:]

# --- 2a. a homeDesign hozzaferok --------------------------------------------
cut("""  window.getHomeDesign = function() {
    return db.collection('config').doc('homeDesign').get().then(function(d) {
      return d.exists ? (d.data().design || 'classic') : 'classic';
    }).catch(function() { return 'classic'; });
  };
  window.setHomeDesign = function(design) {
    return db.collection('config').doc('homeDesign').set({ design: design }).catch(function(e) { console.warn('setHomeDesign', e); });
  };
  window.onHomeDesign = function(cb) {
    return db.collection('config').doc('homeDesign').onSnapshot(function(d) {
      cb(d.exists ? (d.data().design || 'classic') : 'classic');
    });
  };
""", 'homeDesign hozzaferok')

# --- 2b. a store + a hook (nulla hivoval) -----------------------------------
cut("""// ── App-wide design ('classic' | 'playful') — global store fed by Firebase config/homeDesign ──
let _appDesign = 'classic'; // Egy dizájn — a playful mód megszűnt, minden felület a közös stílust használja
let _appDesignInit = false;
const _appDesignSubs = new Set();
function _setAppDesign(d) {
  const v = 'classic'; // egy dizájn — a playful érték már nem kapcsol át semmit
  if (v === _appDesign) return;
  _appDesign = v;
  try { localStorage.setItem('boh_home_design', v); } catch(e) {}
  _appDesignSubs.forEach(fn => { try { fn(v); } catch(e) {} });
}
function useAppDesign() {
  const [d, setD] = React.useState(_appDesign);
  React.useEffect(() => {
    _appDesignSubs.add(setD);
    setD(_appDesign);
    if (!_appDesignInit && typeof window.onHomeDesign === 'function') {
      _appDesignInit = true;
      window.onHomeDesign(x => _setAppDesign(x));
    }
    return () => { _appDesignSubs.delete(setD); };
  }, []);
  return d;
}

""", 'appDesign store')

# --- 2c. az arvan maradt kommentar (mar nem letezo tokenekrol) ---------------
cut("""// Mód-függő kontúr/árnyék tokenek EGY helyen definiálva.
// Szabály: ink kontúr + kemény eltolt árnyék = Playful; lágy szórt árnyék = Classic.
// (Az ikonok és a kabala márkaelemek — mindkét módban azonosak.)
""", 'arva kommentar')

# --- 2d. tovabbi arvak: kommentar es egy soha nem atadott prop -------------
cut("""  // Home screen design — global, admin-controlled via Firebase ('classic' default | 'playful')
  // localStorage is only a cache to avoid a flash before the Firestore snapshot arrives.

""", 'arva homeDesign kommentar')

# A `playful` propot SENKI nem adja at, es a torzs sem olvassa.
sub1(
"function PlayerCard({ p, onEdit, onRemove, index, badge, recentBadge, playful, onLongPress }",
"function PlayerCard({ p, onEdit, onRemove, index, badge, recentBadge, onLongPress }",
'PlayerCard playful prop')

sub1("const APP_VERSION = 'v10.339';", "const APP_VERSION = 'v10.340';", 'verzio')

# --- ellenorzes: egyik nev sem maradhat a forrasban -------------------------
for name in ('AdminPunishments', 'PUNISHMENTS_DEFAULT', 'getPunishments', 'setPunishments',
             'useAppDesign', '_appDesign', '_setAppDesign', 'onHomeDesign',
             'getHomeDesign', 'setHomeDesign', 'boh_home_design', 'playful', 'Playful'):
    assert name not in src, 'bennmaradt: ' + name

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_340 alkalmazva (%d sorral rovidebb)' % (orig.count('\n') - src.count('\n')))
