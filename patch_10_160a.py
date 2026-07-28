# v10.160 (a) — EGY forras arrol, melyik jateknak van sajat beallitasa
#
# Eddig harom kulon inline ternary sorolta fel a beallithato jatekokat (racs-,
# Netflix- es kedvencek-nezet). Ez mar el is csuszott: a kedvencek-sorban csak
# negy jatek nyilt meg a hetbol (kisebb, collect, ovfj kimaradt). Ugyanaz a
# hibafajta, mint a haromfele tema-lista volt.
#
# Mostantol egy lista, es ebbol dolgozik a hosszu nyomas, a kartya
# fogaskerek-jelzese es a Jatekmenet oldal jatek-szekcioja is.
import io, re

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── 1) modul-szintu lista, kozvetlenul a GamesScreen ele ──
anchor = "function GamesScreen({ selectedGames, setSelectedGames, gameMeta, setGameMeta, go }) {"
assert s.count(anchor) == 1
s = s.replace(anchor, """// Melyik jateknak van sajat beallito lapja. EGY forras: ebbol dolgozik a
// hosszu nyomas, a kartya fogaskerek-jelzese es a Jatekmenet oldal is.
const GAME_CONFIG_IDS = ['busz', 'beerpong', 'kisebb', 'collect', 'ovfj', 'zene', 'blackjack'];
const hasGameConfig = (id) => GAME_CONFIG_IDS.indexOf(id) !== -1;

""" + anchor)

# ── 2) egyetlen nyito-fuggveny a GamesScreen-ben ──
hook = "  const [filterSheet, setFilterSheet] = useState(false);"
assert s.count(hook) == 1
s = s.replace(hook, hook + """
  // A het beallito lap egy helyen. A hosszu nyomas es a kartyan levo
  // fogaskerek is ezt hivja, igy nem tudnak elcsuszni egymastol.
  const CONFIG_OPENERS = { busz: setBuszSheet, beerpong: setBeerpongSheet, kisebb: setKisebbSheet,
    collect: setCollectSheet, ovfj: setOvfjSheet, zene: setZeneSheet, blackjack: setBlackjackSheet };
  const openGameConfig = (id) => {
    if (!selectedGames.includes(id)) toggle(id);
    const open = CONFIG_OPENERS[id]; if (open) open(true);
  };
  const longPressFor = (id) => hasGameConfig(id) ? () => openGameConfig(id) : undefined;""")

# ── 3) a harom inline ternary lecserelese ──
# racs- es Netflix-nezet: egy soros, `: undefined}` a vege
pat = re.compile(r"onLongPress=\{g\.id==='busz' \?.*?: undefined\}")
n = len(pat.findall(s))
assert n == 2, f'egysoros ternary: {n} talalat (2 kellene)'
s = pat.sub("onLongPress={longPressFor(g.id)}", s)

# kedvencek-sor: tobbsoros valtozo
fav = """                  const longPress = g.id==='busz' ? ()=>{ if(!selectedGames.includes('busz')) toggle('busz'); setBuszSheet(true); }
                    : g.id==='beerpong' ? ()=>{ if(!selectedGames.includes('beerpong')) toggle('beerpong'); setBeerpongSheet(true); }
                    : g.id==='zene' ? ()=>{ if(!selectedGames.includes('zene')) toggle('zene'); setZeneSheet(true); }
                    : g.id==='blackjack' ? ()=>{ if(!selectedGames.includes('blackjack')) toggle('blackjack'); setBlackjackSheet(true); }
                    : undefined;"""
assert s.count(fav) == 1, 'kedvencek-sor ternary nem talalhato'
s = s.replace(fav, "                  const longPress = longPressFor(g.id);")

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — egy forras, 3 hasznalati hely atallitva')
