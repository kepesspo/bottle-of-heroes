# v10.175 — hat tovabbi jatek kap sajat beallitast
#
# Eddig 45-bol 7 volt allithato. Ezek a jatekok mind fix, kodba egetett
# ertekekkel mentek, pedig a ertekuk tarsasagfuggo (hany par, mekkora palya,
# hany kor, melyik temakor).
#
# A Kviz KIVETEL: az mar olvasta a gameMeta?.quizConfig?.cats-ot, csak
# beallito lapja nem volt es nem szerepelt a nyilvantartasban — ott csak a
# felulet hianyzott.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── 1) gameMeta atadasa a routerben ──
ROUTES = [
    ("<MemoriaGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />",
     "<MemoriaGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />"),
    ("<RitmusGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} players={players||[]} onAdvance={onAdvance} onResult={onResult} />",
     "<RitmusGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />"),
    ("<MeduzaGame key={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />",
     "<MeduzaGame key={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />"),
]
for old, new in ROUTES:
    assert s.count(old) == 1, old[:45]
    s = s.replace(old, new)

for marker in ["<UtvesztoGame key={gameIdx}", "<CardBattleGame key={gameIdx}"]:
    i = s.index(marker)
    j = s.index('/>', i)
    seg = s[i:j]
    assert 'gameMeta' not in seg, marker
    s = s[:j] + 'gameMeta={gameMeta} ' + s[j:]

# ── 2) komponens-szignaturak + a konstansok konfigbol ──
SIGS = [
    ("function MemoriaGame({ gameIdx, players, onAdvance, onResult }) {",
     "function MemoriaGame({ gameIdx, players, onAdvance, onResult, gameMeta }) {"),
    ("function RitmusGame({ gameIdx, players, challenger, opponent, onAdvance, onResult }) {",
     "function RitmusGame({ gameIdx, players, challenger, opponent, onAdvance, onResult, gameMeta }) {"),
    ("function UtvesztoGame({ gameIdx, challenger, opponent, players, onAdvance, onResult, onSetHideFooter }) {",
     "function UtvesztoGame({ gameIdx, challenger, opponent, players, onAdvance, onResult, onSetHideFooter, gameMeta }) {"),
    ("function MeduzaGame({ players, onAdvance, onResult }) {",
     "function MeduzaGame({ players, onAdvance, onResult, gameMeta }) {"),
    ("function CardBattleGame({ gameIdx, challenger, opponent, onAdvance, onResult, onSetHideFooter }) {",
     "function CardBattleGame({ gameIdx, challenger, opponent, onAdvance, onResult, onSetHideFooter, gameMeta }) {"),
]
for old, new in SIGS:
    assert s.count(old) == 1, old[:50]
    s = s.replace(old, new)

CONSTS = [
    # Memoria: 12 emoji van, tehat legfeljebb 12 par
    ("  const PAIR_COUNT = 8;",
     "  const PAIR_COUNT = Math.min(EMOJIS.length, gameMeta?.memoriaConfig?.pairs || 8);"),
    # Ritmus
    ("  const GRID = 12;\n  const DURATION = 30;",
     "  const GRID = gameMeta?.ritmusConfig?.grid || 12;\n  const DURATION = gameMeta?.ritmusConfig?.duration || 30;"),
    ("  const TRAP_CHANCE = 0.2;",
     "  const TRAP_CHANCE = gameMeta?.ritmusConfig?.trapChance ?? 0.2;"),
    # Utveszto
    ("  const GRID = 5;\n  const START_IDX = 0;",
     "  const GRID = gameMeta?.utvesztoConfig?.grid || 5;\n  const START_IDX = 0;"),
    # Meduza — ot jatekban van "TOTAL_ROUNDS = 5", ezert a szignaturahoz
    # horgonyzunk (a signaturat feljebb mar atirtuk)
    ("function MeduzaGame({ players, onAdvance, onResult, gameMeta }) {\n  const TOTAL_ROUNDS = 5;",
     "function MeduzaGame({ players, onAdvance, onResult, gameMeta }) {\n  const TOTAL_ROUNDS = gameMeta?.meduzaConfig?.rounds || 5;"),
    # Kartyacsata
    ("  const VALS = [3,4,5,6,7];\n  const NR = 5;",
     "  const VALS = [3,4,5,6,7];\n  const NR = gameMeta?.cardbattleConfig?.rounds || 5;"),
]
for old, new in CONSTS:
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — bekotes kesz')
