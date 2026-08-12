# v10.343 - A statuszsav is besotetedik, ha modal / bottom sheet nyilik
#
# A BEJELENTES (ket keperyokep): a „Beallitasok" bottom sheet es az „Admin
# belepes" modal alatt az egesz lap besotetedik, a FELSO STATUSZSAV viszont
# vilagos marad. A hatas kettevagja a kepernyot.
#
# ⚠️ AZ OK a dokumentalt iOS-csapda (docs/safe-area.md 1.): black-translucent
# PWA-ban a `position:fixed` retegek NEM festenek a statuszsav moge. A modalok
# sotetito hattere pontosan ilyen reteg, tehat a sav alatt ervenyet veszti.
# A sav szine csak FOLYAMBAN LEVO tartalombol (a gyoker konteneт hattere) es a
# `theme-color` metabol johet — vagyis tudnunk KELL, hogy nyitva van-e fedo
# reteg, es a `statusBarBg`-t magat kell besotetiteni.
#
# ⚠️ MIERT NEM REGISZTRACIOVAL? Mert NEGYVEN kulonbozo helyen van ilyen fedo
# reteg a forrasban, es egy uj modal irojatol nem varhato el, hogy erre
# gondoljon — ugyanugy elfelejtodne, ahogy a `banner:` mezo es a Paros
# kizaras-lista is elfelejtodott. Ezert a DOM-ot nezzuk: teljes kepernyos,
# ATLATSZO hatteru `position:fixed` elem = fedo reteg.
#
# A vizsgalat OLCSO: csak DOM-valtozasra fut (MutationObserver), rAF-fel
# osszevonva, es a jelolteket egy inline-stilus szelektor szuri elo — nem az
# egesz fat jarjuk be.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# --- 1. a detektor + a szinkevero ------------------------------------------
HELPER = r'''
// ── Fedő réteg (modal / bottom sheet) és a felső státuszsáv ──────────────────
// ⚠️ iOS black-translucent PWA-ban a `position:fixed` rétegek NEM festenek a
// státuszsáv mögé (docs/safe-area.md 1. szakasz). A modalok sötétítő háttere
// pontosan ilyen réteg: a lap besötétedik, a státuszsáv világos marad, és a
// kettő élesen elválik. A sáv színe csak FOLYAMBAN LÉVŐ tartalomból és a
// `theme-color`-ból jöhet — tehát a `statusBarBg`-t magát kell sötétíteni.
//
// ⚠️ NEM regisztrációval derítjük ki, hogy nyitva van-e réteg: negyven ilyen
// hely van a forrásban, és egy új modal írójától nem várható el, hogy erre
// gondoljon. A DOM-ot nézzük — teljes képernyős, ÁTLÁTSZÓ hátterű
// `position:fixed` elem = fedő réteg.
const BOH_OVERLAY_MIN_A = 0.15;   // ennél halványabb nem sötétít láthatóan
const BOH_OVERLAY_MAX_A = 0.96;   // a teljesen fedő lap nem „sötétítés"
function bohScanOverlayTint() {
  if (typeof document === 'undefined') return null;
  const vw = window.innerWidth, vh = window.innerHeight;
  let best = null, bestZ = -1;
  // Elovalogatas inline stilusra: a React ezekbe irja a `position: fixed`-et,
  // igy nem kell az egesz fat bejarni.
  document.querySelectorAll('[style*="fixed"]').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' || cs.visibility === 'hidden' || cs.display === 'none') return;
    const r = el.getBoundingClientRect();
    if (r.width < vw * 0.9 || r.height < vh * 0.9) return;      // nem teljes kepernyos
    const m = /^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)$/.exec(cs.backgroundColor || '');
    if (!m) return;
    const a = m[4] === undefined ? 1 : parseFloat(m[4]);
    if (!(a >= BOH_OVERLAY_MIN_A && a <= BOH_OVERLAY_MAX_A)) return;
    const z = parseInt(cs.zIndex, 10) || 0;
    if (z >= bestZ) { bestZ = z; best = { r:+m[1], g:+m[2], b:+m[3], a }; }
  });
  return best;
}
// A sav alapszine ALA keverjuk a fedo reteg szinet — ugyanaz az eredmeny, mint
// amit a lapon latni.
function bohBlendOver(hex, t) {
  if (!t) return hex;
  const h = String(hex).replace('#', '');
  const b = h.length === 3 ? h.split('').map(c => parseInt(c + c, 16))
                           : [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16));
  const mix = i => Math.round(b[i] * (1 - t.a) + [t.r, t.g, t.b][i] * t.a);
  return '#' + [0, 1, 2].map(i => mix(i).toString(16).padStart(2, '0')).join('');
}
function useOverlayTint() {
  const [tint, setTint] = React.useState(null);
  React.useEffect(() => {
    let raf = null;
    const rescan = () => {
      raf = null;
      const t = bohScanOverlayTint();
      setTint(prev => {
        const same = (!prev && !t) || (prev && t && prev.r === t.r && prev.g === t.g && prev.b === t.b && prev.a === t.a);
        return same ? prev : t;
      });
    };
    const kick = () => { if (raf === null) raf = requestAnimationFrame(rescan); };
    const mo = new MutationObserver(kick);
    mo.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['style'] });
    kick();
    return () => { mo.disconnect(); if (raf !== null) cancelAnimationFrame(raf); };
  }, []);
  return tint;
}

'''
sub1("function BottleApp() {", HELPER + "function BottleApp() {", 'detektor beszurasa')

# --- 2. a statusBarBg besotetedik ------------------------------------------
sub1(
"  const statusBarBg = (creatingRoom || screen === 'home' || screen === 'play') ? T.bg : T.surface;",
"""  // A sav alapszine: ahol NINCS fejlec -> a tema hattere, egyebkent feher.
  const baseBarBg = (creatingRoom || screen === 'home' || screen === 'play') ? T.bg : T.surface;
  // ...es ha fedo reteg (modal / bottom sheet) van nyitva, UGYANAZT a
  // sotetitest kapja, amit a lap — kulonben a statuszsav vilagos marad, es
  // elvalik a besotetedett laptol (docs/safe-area.md 1.).
  const overlayTint = useOverlayTint();
  const statusBarBg = bohBlendOver(baseBarBg, overlayTint);""",
'statusBarBg besotetites')

sub1("const APP_VERSION = 'v10.342';", "const APP_VERSION = 'v10.343';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_343 alkalmazva')
