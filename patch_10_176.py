# v10.176 — a hosszu nyomas / ceruza-gomb az UJ jatekoknal is nyit
#
# A v10.175-ben hat jatekot felvettem a GAME_CONFIG_DEFS-be, de a GamesScreen
# NEM abbol dolgozott: sajat CONFIG_OPENERS terkepe volt, a regi het setterrel.
# Igy az uj hatnal a ceruza megjelent (mert az a DEFS-bol jon), de a nyitas
# csendben elmaradt — csak kijelolte a jatekot.
#
# Pont az a hibafajta, ami ellen a GAME_CONFIG_DEFS keszult: KET lista ugyanarrol.
# Ezert most a GamesScreen is a mar meglevo GameConfigHost-ot hasznalja, es
# elfogy a het kulon allapot, a het accessor-par es a het mount.
import io, re

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── egyetlen allapot a het helyett ──
STATES = """  const [buszSheet, setBuszSheet] = useState(false);
  const [blackjackSheet, setBlackjackSheet] = useState(false);
  const [beerpongSheet, setBeerpongSheet] = useState(false);
  const [kisebbSheet, setKisebbSheet] = useState(false);
  const [collectSheet, setCollectSheet] = useState(false);
  const [ovfjSheet, setOvfjSheet] = useState(false);
  const [zeneSheet, setZeneSheet] = useState(false);
"""
assert s.count(STATES) == 1
s = s.replace(STATES, "  const [openCfg, setOpenCfg] = useState(null);   // melyik jatek beallito lapja van nyitva\n")

# ── a nyito fuggveny a nyilvantartasbol dolgozzon ──
OPENERS = """  const CONFIG_OPENERS = { busz: setBuszSheet, beerpong: setBeerpongSheet, kisebb: setKisebbSheet,
    collect: setCollectSheet, ovfj: setOvfjSheet, zene: setZeneSheet, blackjack: setBlackjackSheet };
  const openGameConfig = (id) => {
    if (!selectedGames.includes(id)) toggle(id);
    const open = CONFIG_OPENERS[id]; if (open) open(true);
  };"""
assert s.count(OPENERS) == 1
s = s.replace(OPENERS, """  const openGameConfig = (id) => {
    if (!selectedGames.includes(id)) toggle(id);
    setOpenCfg(id);
  };""")

# ── a het accessor-par elfogy ──
n = 0
for key in ['busz', 'kisebb', 'collect', 'ovfj', 'beerpong', 'zene', 'blackjack']:
    cap = key[0].upper() + key[1:]
    pair = ("  const %sConfig = gameMeta?.%sConfig || {};\n"
            "  const set%sConfig = cfg => setGameMeta(m => ({...m, %sConfig: typeof cfg === 'function' ? cfg(m?.%sConfig||{}) : cfg}));\n"
            % (key, key, cap, key, key))
    assert s.count(pair) == 1, key
    s = s.replace(pair, '')
    n += 1
assert n == 7

# ── a het mount helyett egy dispatcher ──
mounts = re.findall(r'^ *\{[a-z]+Sheet && <[A-Za-z]+ConfigSheet [^\n]*\n', s, re.M)
assert len(mounts) == 7, len(mounts)
first = s.index(mounts[0])
s = s.replace(mounts[0], """      <GameConfigHost openId={openCfg} onClose={() => setOpenCfg(null)}
        gameMeta={gameMeta} setGameMeta={setGameMeta} playerCount={(players || []).length} />
""")
for m in mounts[1:]:
    s = s.replace(m, '')

assert 'CONFIG_OPENERS' not in s and 'buszSheet' not in s and 'zeneConfig =' not in s

s = s.replace("const APP_VERSION = 'v10.175';", "const APP_VERSION = 'v10.176';", 1)
assert "v10.176" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — a GamesScreen is a nyilvantartasbol dolgozik')
