# v10.158 (b) — a kontraszt-meres tovabbi talalatai
#
# Az elso kor a `background:T.ink` + hardcode `color:'#fff'` parost javitotta
# (1.13-as arany). A mereshez irt teszt viszont tovabbi hibakat is kidobott:
#
#  1) slate.inkMute (#4A6078) a slate feluleten 1.68 — a "Szezon" ful es a
#     "PONT" cimke gyakorlatilag olvashatatlan. Ez ugyanaz a hibaosztaly, amit
#     a felhasznalo jelzett, csak a masik sotet temaban.
#  2) T.yellow szovegkent vilagos kartyan: a warm temaban 1.57 (a legnagyobb
#     szam a Statisztikan, a "640 PONT"). A tobbi vilagos tema mar sotetebb
#     sargat hasznal — a warm volt a kilogo. Kulon `yellowText` token, mert a
#     T.yellow HATTERKENT is szerepel 29 helyen, ott a vilagos sarga a helyes.
#  3) 59571: `background:T.ink` + `color:T.yellow` — sotet temaban vilagos sarga
#     a majdnem feher inken. Az elso kor csak a '#fff' parokat kereste.
import re, io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

def sub1(old, new, what):
    global s
    assert s.count(old) == 1, f'{what}: {s.count(old)} talalat (1 kellene)'
    s = s.replace(old, new)

# ── 1) slate.inkMute: 1.68 → 3.44 a feluleten (es marad az inkSoft alatt) ──
sub1("ink: '#E0EAF4', inkSoft: '#8AA0B8', inkMute: '#4A6078',",
     "ink: '#E0EAF4', inkSoft: '#8AA0B8', inkMute: '#7A93AE',",
     'slate.inkMute')

# ── 2) yellowText minden temanak ──
# Vilagos temak: sotetitett sarga, hogy feher kartyan is olvashato legyen.
# Sotet temak: valtozatlan — ott a vilagos sarga a sotet feluleten 5.2-7.0.
YT = {
    'warm':     '#A87C0C',   # 1.57 → 3.78
    'peach':    '#A8700C',   # 2.28 → 4.21
    'lemon':    '#8A7400',   # 2.12 → 4.59
    'ice':      '#96781C',   # 2.53 → 4.20
    'jade':     '#8F7808',   # 2.54 → 4.32
    'dark':     '#F4C95A',   # sotet feluleten 5.66 — marad
    'slate':    '#F0C040',   # sotet feluleten 6.41 — marad
    'midnight': '#E8B840',   # sotet feluleten — marad
}
for key, val in YT.items():
    # a tema blokkjan belul az elso `yellow: '...'` utan szurjuk be
    m = re.search(r"^  " + key + r": \{", s, re.M)
    assert m, f'nincs {key} tema'
    ym = re.search(r"yellow: '(#[0-9A-Fa-f]{6})'", s[m.start():m.start() + 3000])
    assert ym, f'{key}: nincs yellow'
    at = m.start() + ym.end()
    s = s[:at] + f", yellowText: '{val}'" + s[at:]

# ── 3) inkIsLight() kiemelese, hogy ne csak a feher szoveg tudjon igazodni ──
sub1("""const onInk = () => {
  const h = String(T.ink || '#000').replace('#', '');
  const r = parseInt(h.slice(0,2),16) || 0, g = parseInt(h.slice(2,4),16) || 0, b = parseInt(h.slice(4,6),16) || 0;
  return (0.2126*r + 0.7152*g + 0.0722*b) > 140 ? (T.bg || '#1E2A38') : '#fff';
};""",
"""const inkIsLight = () => {
  const h = String(T.ink || '#000').replace('#', '');
  const r = parseInt(h.slice(0,2),16) || 0, g = parseInt(h.slice(2,4),16) || 0, b = parseInt(h.slice(4,6),16) || 0;
  return (0.2126*r + 0.7152*g + 0.0722*b) > 140;
};
const onInk = () => (inkIsLight() ? (T.bg || '#1E2A38') : '#fff');""",
'onInk → inkIsLight')

# ── 4) T.yellow SZOVEGKENT vilagos kartyan → yellowText ──
TEXT_SITES = [
    ("fontSize:15, color:T.yellow||'#F59E0B', lineHeight:1 }}>{x.pts}",
     "fontSize:15, color:(T.yellowText||T.yellow), lineHeight:1 }}>{x.pts}"),
    ("fontSize:30, color:T.yellow||'#F59E0B', lineHeight:0.95",
     "fontSize:30, color:(T.yellowText||T.yellow), lineHeight:0.95"),
    ("fontSize:26, color:T.yellow||'#F0C74E', lineHeight:0.95 }}>{mvp.pts}",
     "fontSize:26, color:(T.yellowText||T.yellow), lineHeight:0.95 }}>{mvp.pts}"),
    ("fontSize:15, color:T.yellow }}>Big Pick",
     "fontSize:15, color:(T.yellowText||T.yellow) }}>Big Pick"),
    ("fontSize:20, color:T.yellow, letterSpacing:T.letterDisplay, textTransform:'uppercase' }}>Big Pick",
     "fontSize:20, color:(T.yellowText||T.yellow), letterSpacing:T.letterDisplay, textTransform:'uppercase' }}>Big Pick"),
    ("fontWeight:700, color:T.yellow }}>🏆 {bp.champion.name}",
     "fontWeight:700, color:(T.yellowText||T.yellow) }}>🏆 {bp.champion.name}"),
]
for old, new in TEXT_SITES:
    sub1(old, new, old[:40])

# a szezon-allapot cimke ket helyen szerepel (Liga + Admin), mindketto kartyan
n = s.count(": (T.yellow||'#F59E0B') }}>")
assert n == 2, f'szezon-allapot: {n} talalat (2 kellene)'
s = s.replace(": (T.yellow||'#F59E0B') }}>", ": (T.yellowText||T.yellow) }}>")

# a harom "Pont" oszlopfejlec ugyanaz a minta
n = s.count("{...hdr, color:T.yellow}")
assert n == 3, f'hdr Pont fejlec: {n} talalat (3 kellene)'
s = s.replace("{...hdr, color:T.yellow}", "{...hdr, color:(T.yellowText||T.yellow)}")

# ── 5) T.ink hatteren a sarga is igazodjon (a '#fff' korrekcio parja) ──
sub1("background: T.ink, color: T.yellow, fontFamily:T.font, fontWeight:900, fontSize:11.5",
     "background: T.ink, color: inkIsLight() ? (T.yellowText||T.yellow) : T.yellow, fontFamily:T.font, fontWeight:900, fontSize:11.5",
     'wcPunish gomb')

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — patch alkalmazva')
