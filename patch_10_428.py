# v10.428 — Imposztor: csonka/hibás szavak javítása a bankban („Laborató" → „Laboratórium"…)
# és a hosszú szavak a lapon kisebb betűvel, tördelve férnek ki.
import re
f = 'app.src.html'; s = open(f, encoding='utf8').read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)

FIX = {  # régi → új (a kategória-tipp marad, ahol nincs megadva más)
  'Laborató': 'Laboratórium', 'Cirkuszpor': 'Cirkuszsátor', 'Medvebölcső': 'Jegesmedve',
  'Útlap': 'Útlevél', 'Sajtárda': 'Sajttál', 'Trachoma': 'Patika', 'Tüzijáték': 'Tűzijáték',
  'Surf': 'Szörf', 'Lovagló': 'Lovaglás',
}
a = s.index('const IMPOSZTOR_SZAVAK = ['); b = s.index('];', a)
bank = s[a:b]
for o, n in FIX.items():
    assert bank.count("'%s'" % o) == 1, o
    bank = bank.replace("'%s'" % o, "'%s'" % n)
# a második 'Tengerész' duplikátum volt (két körben ugyanaz a szó) → Halász
i1 = bank.index("'Tengerész'"); i2 = bank.index("'Tengerész'", i1 + 1)
bank = bank[:i2] + "'Halász'" + bank[i2 + len("'Tengerész'"):]
assert bank.count("'Tengerész'") == 1
s = s[:a] + bank + s[b:]

a = s.index('const IMPOSZTOR_TIPPEK = {'); b = s.index('\n};', a)
tbl = s[a:b]
for o, n in FIX.items():
    assert tbl.count("'%s':" % o) == 1, o
    tbl = tbl.replace("'%s':" % o, "'%s':" % n)
tbl = tbl.replace("'Útlevél':'Közlekedés'", "'Útlevél':'Utazás'")
assert tbl.count("'Tengerész':'Foglalkozás',") == 1
tbl = tbl.replace("'Tengerész':'Foglalkozás',", "'Tengerész':'Foglalkozás', 'Halász':'Foglalkozás',")
s = s[:a] + tbl + s[b:]

# hosszú szó: méret a hosszból, és tördelhető (ne lógjon ki a lapról)
rep("function ImposztorHint({ hint }) {", """// A szó betűmérete a hosszából: 10 betűig az alap, fölötte arányosan kisebb (min. 60%).
const impWordSize = (w, base) => { const n = String(w || '').length; return n <= 10 ? base : Math.max(Math.round(base * 0.6), Math.round(base * 10 / n)); };

function ImposztorHint({ hint }) {""")
rep("""<div style={{ fontFamily:T.font, fontWeight:800, fontSize:36, color:'#fff', letterSpacing:'0.02em' }}>{isImpostor ? oddWord : word}</div>""",
    """<div data-imp-word style={{ fontFamily:T.font, fontWeight:800, fontSize:impWordSize(isImpostor ? oddWord : word, 36), lineHeight:1.15, color:'#fff', letterSpacing:'0.02em', overflowWrap:'anywhere' }}>{isImpostor ? oddWord : word}</div>""")
rep("""<div style={{ fontFamily:T.font, fontWeight:900, fontSize:26, color:'#fff' }}>{myRole.word}</div>""",
    """<div data-imp-word style={{ fontFamily:T.font, fontWeight:900, fontSize:impWordSize(myRole.word, 26), lineHeight:1.15, color:'#fff', overflowWrap:'anywhere' }}>{myRole.word}</div>""")
rep("const APP_VERSION = 'v10.427';", "const APP_VERSION = 'v10.428';")
open(f, 'w', encoding='utf8').write(s)
print('ok')
