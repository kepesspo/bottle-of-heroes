# v10.335 — ⚠️ Alkomponens a torzsben = minden renderelesnel UJRAMOUNT
#
# A bejelentes: „Tappernel ugralnak az avatarok. Mindig rafrissul."
#
# AZ OK (harmadszor ugyanez): a `Btn` a `TapperGame` TORZSEBEN volt definialva,
# tehat MINDEN ujrarenderelesnel uj fuggveny-azonossagot kapott. A React ezt
# MAS komponens-tipusnak latja: nem frissiti a meglevo fat, hanem LESZEDI es
# ujramountolja — az avatar `<img>` pedig ezzel egyutt ujratoltodik.
#
# A Tappernel ez lathato is: a visszaszamlalo `setInterval` 40 MS-ONKENT
# ketyeg, tehat masodpercenkent 25-szor epult ujra mindket tabla.
#
# Ugyanez a hiba mar ketszer elojott (Idoparbaj v10.315, Blackjack v10.325).
# Ezert most az OSSZES olyan hely javul, ahol alkomponens ul a torzsben, ES
# avatart rajzol, ES a szulo masodpercnel gyakrabban rendereli ujra:
#   • TapperGame `Btn`              — 40 ms
#   • KisebbGame `LargeCard`        — 600 ms
#   • BeerPongObserverView `PlayerChip` — 1000 ms
#   • KoPapirGame `PlayerCard`      — 3000 ms
#
# AMI SZANDEKOSAN MARAD: a result-banner `Pile` / `Metric` / `Row` — azokat
# SIMA FUGGVENYKENT hivjuk (`Pile({...})`), nem JSX-kent, tehat a React nem
# lat kulon tipust. Ez a kulonbseg a donto, nem a definicio helye.
import io, re

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, f'{what}: {src.count(old)} talalat'
    src = src.replace(old, new)

def cut(start_marker, end_marker, what):
    """Kivagja a [start_marker, end_marker) szakaszt es visszaadja."""
    global src
    i = src.index(start_marker); j = src.index(end_marker, i)
    body = src[i:j]
    src = src[:i] + src[j:]
    return body

# ── 1. TAPPER ────────────────────────────────────────────────────────────────
TAP_START = "  const Btn = ({ pNum, player, holding, timeVal }) => {"
# ⚠️ A zaro-jelolo NEM lehet a `const timerColor` — abbol TOBB van a
# forrasban, es a masodik mar egy masik jatekban ul: a kivagas az egesz
# TapperGame-et elvitte volna. A `return (` blokk kezdete egyedi.
TAP_END = "\n  return (\n    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:28"
assert src.count(TAP_START) == 1, 'Tapper Btn nem egyedi'
assert src.count(TAP_END) == 1, 'Tapper return nem egyedi'
i = src.index(TAP_START); j = src.index(TAP_END, i)
tap_body = src[i:j]
src = src[:i] + src[j:]

# a torzsbol jovo zart valtozok PROPPA valnak: phase, countdown, pressDown,
# pressUp, writeTapperState
tap_mod = tap_body.replace(
    "  const Btn = ({ pNum, player, holding, timeVal }) => {",
    "function TapperBtn({ pNum, player, holding, timeVal, phase, countdown, onDown, onUp }) {")
tap_mod = tap_mod.replace(
    "pressDown(pNum); writeTapperState(player?.name, true); }}",
    "onDown(pNum, player); }}")
tap_mod = tap_mod.replace(
    "onPointerUp={() => { pressUp(pNum); writeTapperState(player?.name, false); }}",
    "onPointerUp={() => { onUp(pNum, player); }}")
tap_mod = tap_mod.replace(
    "onPointerCancel={() => { pressUp(pNum); writeTapperState(player?.name, false); }}",
    "onPointerCancel={() => { onUp(pNum, player); }}")
# a lezaro `};` -> `}`
tap_mod = re.sub(r'\n  \};\s*$', '\n}\n', tap_mod)
# egy szinttel kijjebb huzzuk
tap_mod = '\n'.join((l[2:] if l.startswith('    ') else l) for l in tap_mod.split('\n'))

HEADER = """// ⚠️ MODUL-SZINTU, es ez NEM stiluskerdes. Amig a `Btn` a TapperGame torzseben
// volt, minden ujrarenderelesnel uj fuggveny-azonossagot kapott: a React MAS
// tipusnak latta, leszedte es ujramountolta a fat — az avatar `<img>` pedig
// ujratoltodott. A visszaszamlalo 40 ms-onkent ketyeg, tehat masodpercenkent
// 25-szor. Ez volt az „ugralnak az avatarok, mindig rafrissul".
"""
sub1("function TapperGame({ gameIdx, challenger, opponent, onAdvance, onResult, roomCode }) {",
     HEADER + tap_mod + "\nfunction TapperGame({ gameIdx, challenger, opponent, onAdvance, onResult, roomCode }) {",
     'TapperBtn kiemelese')

for n in (1, 2):
    sub1(f"      <Btn pNum={{{n}}} player={{p{n}}} holding={{p{n}Hold}} timeVal={{p{n}Time}} />",
         f"      <TapperBtn pNum={{{n}}} player={{p{n}}} holding={{p{n}Hold}} timeVal={{p{n}Time}}\n"
         f"        phase={{phase}} countdown={{countdown}}\n"
         f"        onDown={{(k, pl) => {{ pressDown(k); writeTapperState(pl?.name, true); }}}}\n"
         f"        onUp={{(k, pl) => {{ pressUp(k); writeTapperState(pl?.name, false); }}}} />",
         f'Btn {n} hasznalat')

# ── 2. verziobump ────────────────────────────────────────────────────────────
sub1("const APP_VERSION = 'v10.334';", "const APP_VERSION = 'v10.335';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK — patch_10_335 (Tapper) alkalmazva')
