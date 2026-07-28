#!/usr/bin/env python3
# v10.180 (2. resz) — a rejtett kapcsolo a kezdokepernyon
#
# A coll() mar keszen all (patch_10_180.py), csak eddig semmi nem allitotta at.
# A kapcsolo a verzioszamon van: harom koppintas. Rejtett, mert nem napi
# funkcio — de ha be van kapcsolva, a felirat maga mutatja, hogy teszt modban
# vagyunk. Enelkul a marker nelkul konnyu eszrevetlenul bentragadni.
import re, sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

# ─── 1) allapot + koppintas-kezelo a HomeScreen-be ───
ANCHOR = """  const greetHi = 'Szia, csapat!';
  const _greetDays = ['Vasárnap','Hétfő','Kedd','Szerda','Csütörtök','Péntek','Szombat'];
  const greetSub = `${_greetDays[new Date().getDay()]} · ${APP_VERSION}`;
"""
assert src.count(ANCHOR) == 1, 'greetSub blokk: %d' % src.count(ANCHOR)

NEW = ANCHOR + """
  // Teszt adatbázis — rejtett kapcsoló a verziószámon (3 koppintás 1,5 mp-en belül).
  // Alapból ÉLES: aki nem nyúl hozzá, annak minden statisztikája élesbe megy.
  const testDb = typeof window !== 'undefined' && !!(window.isTestDb && window.isTestDb());
  const [dbToast, setDbToast] = React.useState(null);
  const dbTaps = React.useRef({ n: 0, t: 0 });
  const tapVersion = () => {
    if (!window.setTestDb) return;
    const now = Date.now(), s = dbTaps.current;
    s.n = (now - s.t < 1500) ? s.n + 1 : 1;
    s.t = now;
    if (s.n < 3) return;
    s.n = 0;
    const on = !testDb;
    window.setTestDb(on);
    setDbToast(on);
    // Ujratoltes: a mar betoltott statisztikak a MASIK adatbazisbol jonnenek,
    // vagyis a kepernyon teszt-adat allna, mikozben az iras mar elesbe menne.
    setTimeout(() => { try { window.location.reload(); } catch (e) {} }, 1500);
  };
"""
src = src.replace(ANCHOR, NEW, 1)

# ─── 2) a verzio-sor kattinthato lesz + teszt jelzes ───
OLD_LINE = """            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkSoft, marginTop:2 }}>{greetSub}</div>"""
assert src.count(OLD_LINE) == 1, 'verzio-sor: %d' % src.count(OLD_LINE)

NEW_LINE = """            <div onClick={tapVersion} style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkSoft, marginTop:2, cursor:'pointer', userSelect:'none', WebkitTapHighlightColor:'transparent', display:'flex', alignItems:'center', gap:6 }}>
              {greetSub}
              {testDb && (
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, letterSpacing:'0.1em', color:'#fff', background:T.coral, borderRadius:999, padding:'2px 7px' }}>TESZT DB</span>
              )}
            </div>"""
src = src.replace(OLD_LINE, NEW_LINE, 1)

# ─── 3) a visszajelzo sav ───
TOAST_ANCHOR = """      {showInstall && <InstallModal onClose={() => setShowInstall(false)} />}"""
assert src.count(TOAST_ANCHOR) == 1, 'toast horgony: %d' % src.count(TOAST_ANCHOR)

TOAST = TOAST_ANCHOR + """
      {dbToast !== null && (
        <Toast tone="info" wide offset={120} icon={dbToast ? '🧪' : '🎯'}>
          {dbToast
            ? 'Teszt adatbázis bekapcsolva — a statisztika mostantól a teszt-adatokhoz megy.'
            : 'Éles adatbázis — a statisztika mostantól élesbe megy.'}
        </Toast>
      )}"""
src = src.replace(TOAST_ANCHOR, TOAST, 1)

open(P, 'w', encoding='utf-8').write(src)
print('OK — 3-koppintasos kapcsolo, TESZT DB jelzes es visszajelzo sav bekerult')
