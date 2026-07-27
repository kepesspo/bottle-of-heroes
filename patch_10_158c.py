# v10.158 (c) — a sajat szinevel kitoltott pirulak
#
# A LEVEL_BANDS / nehezsegi szintek pirulai a szoveget ES a hatteret UGYANABBOL
# a szinbol keverik (`${c}1F` hatter + `c` szoveg). Ez elvbol nem tud egyszerre
# jo lenni: ami feher kartyan olvashato sotet arnyalat, az a sotet feluleten
# beleolvad — es forditva. A meres pontosan ezt mutatta: a "Rutinos" mentazold
# 1.99 vilagos temaban, a "Legenda" lila 1.65 a sotetben.
#
# Ezert nem a paletta szineit irjuk at (azok jelentest hordoznak es a
# folyamatjelzo savon jol neznek ki), hanem SZOVEGKENT igazitjuk oket a
# temahoz: a szinezet marad, csak annyit vilagosodik/sotetedik, amennyi a
# 3.5-os aranyhoz kell az aktualis felulettel szemben.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

HELPER = """const tierInk = (hex, over) => {
  const rgb = h => { h = String(h || '#000').replace('#', '');
    if (h.length === 3) h = h[0]+h[0]+h[1]+h[1]+h[2]+h[2];
    return [parseInt(h.slice(0,2),16)||0, parseInt(h.slice(2,4),16)||0, parseInt(h.slice(4,6),16)||0]; };
  const lum = c => { const f = x => { x /= 255; return x <= 0.03928 ? x/12.92 : Math.pow((x+0.055)/1.055, 2.4); };
    return 0.2126*f(c[0]) + 0.7152*f(c[1]) + 0.0722*f(c[2]); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x,y)+0.05) / (Math.min(x,y)+0.05); };
  const bg = rgb(over || T.surface || '#fff');
  const lighten = lum(bg) < 0.18;
  let c = rgb(hex);
  for (let i = 0; i < 24 && ratio(c, bg) < 3.5; i++)
    c = lighten ? c.map(v => v + (255 - v) * 0.09) : c.map(v => v * 0.91);
  return '#' + c.map(v => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, '0')).join('');
};
const themeSwatch = (key) => {"""

assert s.count("const themeSwatch = (key) => {") == 1
s = s.replace("const themeSwatch = (key) => {", HELPER)

# Csak a SZOVEG-hasznalatok. A hatter/keret/savkitoltes marad telitett — ott a
# szin dekoracio, nem olvasando informacio.
SITES = [
    ("fontSize: sm ? 10 : 11.5, color:lvl.color }}>{lvl.level}",
     "fontSize: sm ? 10 : 11.5, color:tierInk(lvl.color) }}>{lvl.level}"),
    ("fontSize:20, color:u.lvl.color, lineHeight:0.95 }}>+{u.gain}",
     "fontSize:20, color:tierInk(u.lvl.color), lineHeight:0.95 }}>+{u.gain}"),
    ("fontSize:14, color:lvl.color, overflow:'hidden'",
     "fontSize:14, color:tierInk(lvl.color), overflow:'hidden'"),
    ("fontSize:17, color:lvl.color, lineHeight:1 }}>{lvl.level}",
     "fontSize:17, color:tierInk(lvl.color), lineHeight:1 }}>{lvl.level}"),
    ("fontSize:14, color:lvl.color }}>{lvl.title}",
     "fontSize:14, color:tierInk(lvl.color) }}>{lvl.title}"),
    ("fontSize:11, color:lv.color, letterSpacing:'0.06em' }}>{lv.label}",
     "fontSize:11, color:tierInk(lv.color), letterSpacing:'0.06em' }}>{lv.label}"),
    ("fontSize:13, color:r.lvl.color, overflow:'hidden'",
     "fontSize:13, color:tierInk(r.lvl.color), overflow:'hidden'"),
]
for old, new in SITES:
    n = s.count(old)
    assert n == 1, f'{old[:50]!r}: {n} talalat (1 kellene)'
    s = s.replace(old, new)

# a szintlepes-lapon ketszer szerepel ugyanaz a span (uj szint + uj cim)
n = s.count("<span style={{ color:u.lvl.color }}>")
assert n == 2, f'LevelUpSheet span: {n} talalat (2 kellene)'
s = s.replace("<span style={{ color:u.lvl.color }}>", "<span style={{ color:tierInk(u.lvl.color) }}>")

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — tierInk alkalmazva %d helyen' % (len(SITES) + 2))
