# v10.354 - Kviz: a halott ajandek-kioszto kivezetese
#
# ⚠️ EZ EGY MEGCAFOLT FELTETELEZESBOL NOTT KI, es a meres forditotta meg.
#
# Amit hittem: a Kviz `confirmGift`-je VALODI konyvelest kuld, a bannert viszont
# a LEGACY alakban (`playerName:null`) — tehat „Fordított kör" wildcard alatt a
# konyveles megfordul, a banner nem (a v10.333-as csalad).
#
# Amit a meres mutatott: a `wc_reverse_test` uj Kviz-blokkja a REGI kodon is
# atment. Az ok: a jatekban KET ajandek-megerosito fuggveny van, es a
# felhasznalo a MASIKAT eri el:
#   • `confirmGifts` (tobbes szam, 62954) — ez van gombra kotve, es ez MAR a
#     teljes `winners`/`losers` alakot kuldi (v10.318 ota);
#   • `confirmGift` (egyes szam) — ezt SEMMI nem hivja.
#
# Sot, az egesz furt elerhetetlen: az `openGiftPool` sincs sehonnan meghivva,
# tehat a `giftPool` allapot MINDIG `null`. Nem banner-hiba volt, hanem halott
# kod — a v10.315 elotti kioszto maradeka.
#
# Ezert nem javitunk, hanem KIVEZETUNK (ugyanaz a takaritas, mint a v10.340):
# `giftPool` allapot + `openGiftPool` + `giveOneDrink` + `takeOneDrink` +
# `confirmGift`. A viselkedes NEM valtozik — nem volt elerheto.
#
# A `wc_reverse_test` uj 4-5. blokkja MARAD: az a LIVE agat (`confirmGifts`)
# meri, es most mar bizonyitottan mukodik forditott korben is.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. Az allapot ───────────────────────────────────────────────────────────
sub1(
"""  const [giftPool, setGiftPool] = React.useState(null); // {pool, assigned:{}}
""",
"""""",
'giftPool allapot')

# ── 2. A negy fuggveny ──────────────────────────────────────────────────────
sub1(
"""  const openGiftPool = () => {
    const others = players.filter(p => p.id !== challenger?.id);
    const assigned = {};
    others.forEach(p => { assigned[p.id] = 0; });
    setGiftPool({ pool: kortyok, assigned });
  };

  const giveOneDrink = (pid) => {
    setGiftPool(g => g.pool <= 0 ? g : { pool: g.pool-1, assigned: {...g.assigned, [pid]: (g.assigned[pid]||0)+1} });
  };
  const takeOneDrink = (pid) => {
    setGiftPool(g => (g.assigned[pid]||0) <= 0 ? g : { pool: g.pool+1, assigned: {...g.assigned, [pid]: g.assigned[pid]-1} });
  };
  const confirmGift = () => {
    if (!giftPool) return;
    const drinkMap = {};
    Object.entries(giftPool.assigned).forEach(([pid,n]) => { if(n>0) drinkMap[pid]=n; });
    if (onAdvance) onAdvance(drinkMap, { [challenger?.id]: 1 });
    const names = Object.entries(giftPool.assigned)
      .filter(([,n])=>n>0)
      .map(([pid,n]) => { const p=players.find(x=>x.id===pid); return `${p?.name||'?'} iszik ${n} kortyt`; });
    if (onResult) onResult({ correct: false, playerName: null, drinks: 0, subtitle: names.join(' · ') || 'Kiosztva!' });
    setGiftPool(null);
    setPhase('done');
  };

""",
"""  // A regi ajandek-kioszto (`giftPool` + `openGiftPool` + `giveOneDrink` +
  // `takeOneDrink` + `confirmGift`) KIKERULT (v10.354): az `openGiftPool`-t
  // semmi nem hivta, tehat a `giftPool` mindig `null` volt, es vele az egesz
  // furt elerhetetlen. A jatekban hasznalt kioszto a `confirmGifts` (tobbes
  // szam) lentebb — az a KOZOS `PlayerDrinkRow`-ra epul (v10.315), es a teljes
  // `winners`/`losers` alakot kuldi (v10.318).

""",
'halott ajandek-kioszto')

# ⚠️ A reset-effektben is maradt egy hivo — ezt a MEGLEVO `quiz_test` kapta el
# (a jatek ErrorBoundary-ra futott: „setGiftPool is not defined"). Erdemes tudni,
# hogy a hiba NEM latszott „JS hibakent": a hatarolo elnyelte, a teszt sajat
# allitasai buktak el.
sub1(
"""  React.useEffect(() => { setStreak(0); setQIdx(0); setGiftPool(null); setGifts({}); setDistributeTarget(null); }, [gameIdx]);""",
"""  React.useEffect(() => { setStreak(0); setQIdx(0); setGifts({}); setDistributeTarget(null); }, [gameIdx]);""",
'reset-effekt')

sub1("const APP_VERSION = 'v10.353';", "const APP_VERSION = 'v10.354';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_354 alkalmazva')
