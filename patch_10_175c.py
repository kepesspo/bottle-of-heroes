# v10.175 (c) — az Utveszto csapdaszama kovesse a palyameretet
#
# A csapdak szama ot helyen volt beegetve 5-re. Az uj palyameret-beallitassal ez
# elromlana: 4x4-en (16 mezo) 5 csapda tulzsufolt, 7x7-en (49 mezo) elveszik.
# A sugoszoveg is fixen "5×5-ös pályádon"-t irt, fuggetlenul a beallitastol.
#
# Aranyszam: a mezok otode, de legalabb 3.
#   4×4 → 3 · 5×5 → 5 · 6×6 → 7 · 7×7 → 10
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

old_grid = "  const GRID = gameMeta?.utvesztoConfig?.grid || 5;\n  const START_IDX = 0;"
assert s.count(old_grid) == 1
s = s.replace(old_grid, """  const GRID = gameMeta?.utvesztoConfig?.grid || 5;
  // A csapdaszam kovesse a palyat: a mezok otode, de legalabb 3.
  const TRAPS = Math.max(3, Math.round(GRID * GRID / 5));
  const START_IDX = 0;""")

FIX = [
    ("    if (!alreadyHas && total >= 5) return;",
     "    if (!alreadyHas && total >= TRAPS) return;"),
    ("""          {['1️⃣ Helyezz el 5 csapdát a saját 5×5-ös pályádon','2️⃣ Az ellenfél vakon rajzolja az útját'""",
     """          {[`1️⃣ Helyezz el ${TRAPS} csapdát a saját ${GRID}×${GRID}-ös pályádon`,'2️⃣ Az ellenfél vakon rajzolja az útját'"""),
    ("    const canPlace = (id) => !board1.includes(id) && placed < 5;",
     "    const canPlace = (id) => !board1.includes(id) && placed < TRAPS;"),
    ("Helyezz el {5-placed} csapdát · Start mező védett",
     "Helyezz el {TRAPS-placed} csapdát · Start mező védett"),
    ("""fontSize:16,color:T.mint}}>{placed}/5</div>""",
     """fontSize:16,color:T.mint}}>{placed}/{TRAPS}</div>"""),
]
for old, new in FIX:
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)

# a masodik jatekos palyaja is ugyanennyi csapdat kap
n = len(__import__('re').findall(r"\bplaced2? < 5\b|>= 5\)", s))
assert 'placed < 5' not in s and 'total >= 5' not in s, 'maradt beegetett 5'

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — a csapdaszam a palyameretbol jon')
