#!/usr/bin/env python3
# v10.285 — Szólánc: a szín MOST MAR a tetet is jelenti
#
# Eddig a hofok-lap szine nott a lanccal, a tet viszont vegig 1 korty volt.
# A szin tehat eszkalaciot igert, amit a jatek nem valtott be.
#
# Mostantol EGY SZIN = EGY TET:
#     zold   1 korty · sarga 2 korty · rozsa 3 korty     (× nehezseg × wildcard)
#
# A HATAROKAT IS AT KELLETT RENDEZNI
#   A lanc 8 szonal er veget (`chainPool` a kevert lista fele, ceil(15/2)=8),
#   tehat osszesen HET szint van: 2..8. A regi 2-4 / 5-7 / 8+ felosztas 3/3/1-et
#   adott — a rozsaszin tier pontosan egy szintet fedett, a legutolsot, amit a
#   legtobb parti sosem er el. Ugy eszkalacio helyett csak egy elmeleti felso
#   fokozat volt. Az uj 2-3 / 4-6 / 7+ felosztas 2/3/2 — a felso tier elerheto.
#
# A `stake` is igazodik: [1,1] -> [1,3], kulonben a korty-korong tovabbra is
# fix "1 korty"-ot igerne, miközben a jatek 3-at is kioszthat. (A korong a
# nehezseggel felszoroz, tehat nehez fokozaton "3-9 korty" lesz.)
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. A paletta: minden fokozathoz tartozik egy tet
# ─────────────────────────────────────────────────────────────────────────────
sub("""const SZ_TONES = [
  { max: 4,        bg:'#C9E8D2', badge:'#4FA97F' },
  { max: 7,        bg:'#F5E0AC', badge:'#D69A2E' },
  { max: Infinity, bg:'#F2C4C4', badge:'#D46A6A' },
];""",
    """// A `korty` mezo miatt EGY SZIN = EGY TET: a lap szine nem csak azt mondja,
// milyen hosszu a sor, hanem azt is, mennyibe kerul elrontani.
// A hatarok 2/3/2-re vannak osztva a het szint (2..8) kozott — a regi 2-4/5-7/8+
// 3/3/1 volt, tehat a felso fokozat egyetlen, szinte sosem elert szintet fedett.
const SZ_TONES = [
  { max: 3,        bg:'#C9E8D2', badge:'#4FA97F', korty: 1 },
  { max: 6,        bg:'#F5E0AC', badge:'#D69A2E', korty: 2 },
  { max: Infinity, bg:'#F2C4C4', badge:'#D46A6A', korty: 3 },
];""",
    'paletta')

# ─────────────────────────────────────────────────────────────────────────────
# 2. A bukas a fokozat tetjet viszi (a szorzast az advanceLoverseny vegzi)
# ─────────────────────────────────────────────────────────────────────────────
sub("""        if (onAdvance) onAdvance({ [pid]: 1 }, pm);
        if (onResult) onResult({ correct: false, playerName: curPlayer?.name, drinks: 1,
                                 subtitle: (curPlayer?.name || 'Valaki') + ' elrontotta!' });
        setDone({ failName: curPlayer?.name, chain, badIdx: S.tapped.length });""",
    """        // A tet a FOKOZATBOL jon, nem fix 1-bol. A nehezseggel es a wildcarddal
        // valo felszorzast az `advanceLoverseny` es az `onResult` vegzi — ide
        // NYERS szamot kell adni, kulonben duplan szorodna.
        if (onAdvance) onAdvance({ [pid]: tone.korty }, pm);
        if (onResult) onResult({ correct: false, playerName: curPlayer?.name, drinks: tone.korty,
                                 subtitle: (curPlayer?.name || 'Valaki') + ' elrontotta!' });
        setDone({ failName: curPlayer?.name, chain, badIdx: S.tapped.length, korty: tone.korty });""",
    'bukas tet')

sub("""              iszik {mult} kortyot""",
    """              iszik {(done.korty || 1) * mult} kortyot""",
    'bukas lap szam')

# ─────────────────────────────────────────────────────────────────────────────
# 3. A tet MAR AZ ATADASNAL latszik — ott dol el, hogy belevagsz-e
# ─────────────────────────────────────────────────────────────────────────────
sub("""            <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:700, color:T.inkMute, marginTop:7 }}>
              {S.chainLen} szó jön{S.chainLen > 2 ? ` — ${S.chainLen - 2} szintet már vittek` : ' — ez az első kör'}
            </div>""",
    """            {/* A haladast a letra mar elmondja, ide a TET kell: ez az egyetlen
                pillanat, amikor a jatekos meg tudja, mibe vag bele. */}
            <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:700, color:T.inkMute, marginTop:7 }}>
              {S.chainLen} szó — a tét{' '}
              <span style={{ color:tone.badge, fontWeight:900 }}>{tone.korty * mult} korty</span>
            </div>""",
    'atadas tet')

# ─────────────────────────────────────────────────────────────────────────────
# 4. A korty-korong is a valos tartomanyt igerje
# ─────────────────────────────────────────────────────────────────────────────
sub("""  { id:'szolánc', stake:[1,1],""",
    """  { id:'szolánc', stake:[1,3],""",
    'stake tartomany')

sub("const APP_VERSION = 'v10.284';", "const APP_VERSION = 'v10.285';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — egy szín = egy tét (1 / 2 / 3 korty)')
