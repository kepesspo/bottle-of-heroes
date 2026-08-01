#!/usr/bin/env python3
# v10.251 — Szerencsekerék: a kerék kitölti a képernyő szélességét
#
# A kerék mérete eddig egy beégetett 288 px volt, tehát egy 402 px széles
# telefonon a szélesség ~72%-át foglalta el, és köré maradt egy jókora üres sáv.
#
# Most a kerék MEGMÉRI a saját konténerét (ResizeObserver), és annak szélességét
# veszi fel. Minden belső méret ebből skálázódik (a 288-hoz képesti aránnyal):
# avatar, névméret, középső gomb, mutató. Így nagyobb kijelzőn is arányos marad,
# nem egy felnagyított kis kerék néhány pötty avatarral.
#
# Alsó/felső korlát: 240–520 px. Az alsó azért kell, hogy nagyon keskeny
# kijelzőn se essen szét, a felső azért, hogy tableten ne legyen groteszk.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. mért szélesség + arányos belső méretek ──
sub("""  const SIZE = 288, R = SIZE / 2, rad = R - 6;""",
    """  // A kerek a KONTENERE szelesseget veszi fel — igy kitolti a kepernyot.
  // Minden belso meret a 288-as alaphoz kepesti aranybol (k) szamolodik, hogy
  // nagyobb kereken ne maradjanak pottynyi avatarok.
  const wheelWrapRef = React.useRef(null);
  const [wheelW, setWheelW] = React.useState(0);
  React.useLayoutEffect(() => {
    const el = wheelWrapRef.current;
    if (!el) return;
    const upd = () => setWheelW(Math.round(el.getBoundingClientRect().width));
    upd();
    if (typeof ResizeObserver !== 'undefined') {
      const ro = new ResizeObserver(upd);
      ro.observe(el);
      return () => ro.disconnect();
    }
    window.addEventListener('resize', upd);
    return () => window.removeEventListener('resize', upd);
  }, []);
  const SIZE = Math.max(240, Math.min(wheelW || 288, 520));
  const k = SIZE / 288;
  const R = SIZE / 2, rad = R - 6 * k;""",
    'mert meret')

sub("""  const nameSize = n <= 4 ? 13 : n <= 7 ? 11.5 : 10;
  const avSize = n <= 4 ? 42 : n <= 7 ? 34 : 26;""",
    """  const nameSize = (n <= 4 ? 13 : n <= 7 ? 11.5 : 10) * k;
  const avSize = Math.round((n <= 4 ? 42 : n <= 7 ? 34 : 26) * k);""",
    'aranyos betu/avatar')

# ── 2. a konteneren a ref + teljes szelesseg ──
sub("""      <div style={{ position:'relative', width:SIZE, height:SIZE + 26 }}>""",
    """      <div ref={wheelWrapRef} style={{ position:'relative', width:'100%', height:SIZE + 26 * k }}>""",
    'kontener ref')

sub("""          <svg width="34" height="44" viewBox="0 0 26 34">""",
    """          <svg width={Math.round(34 * k)} height={Math.round(44 * k)} viewBox="0 0 26 34">""",
    'mutato meret')

sub("""        <div style={{ position:'absolute', top:26, left:0, width:SIZE, height:SIZE,""",
    """        <div style={{ position:'absolute', top:26 * k, left:'50%', marginLeft:-R, width:SIZE, height:SIZE,""",
    'kerek pozicio')

sub("""          style={{ position:'absolute', top:26 + R, left:R, transform:'translate(-50%,-50%)', zIndex:2,
                   width:92, height:92, borderRadius:'50%', border:'none', background:T.surface,""",
    """          style={{ position:'absolute', top:26 * k + R, left:'50%', transform:'translate(-50%,-50%)', zIndex:2,
                   width:Math.round(92 * k), height:Math.round(92 * k), borderRadius:'50%', border:'none', background:T.surface,""",
    'kozepso gomb')

sub("""          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={T.coral} strokeWidth="2.4"
               strokeLinecap="round" strokeLinejoin="round"
               style={{ animation: phase === 'spinning' ? 'spin 1s linear infinite' : 'none' }}>
            <path d="M20 12a8 8 0 1 1-2.6-5.9" /><path d="M20 4v4.5h-4.5" />
          </svg>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:T.coral, letterSpacing:'0.06em' }}>""",
    """          <svg width={Math.round(24 * k)} height={Math.round(24 * k)} viewBox="0 0 24 24" fill="none" stroke={T.coral} strokeWidth="2.4"
               strokeLinecap="round" strokeLinejoin="round"
               style={{ animation: phase === 'spinning' ? 'spin 1s linear infinite' : 'none' }}>
            <path d="M20 12a8 8 0 1 1-2.6-5.9" /><path d="M20 4v4.5h-4.5" />
          </svg>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:Math.round(11 * k), color:T.coral, letterSpacing:'0.06em' }}>""",
    'gomb belseje')

sub("""                <span style={{ fontFamily:T.font, fontWeight:800, fontSize:nameSize, color:T.ink,
                               maxWidth:76, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</span>""",
    """                <span style={{ fontFamily:T.font, fontWeight:800, fontSize:nameSize, color:T.ink,
                               maxWidth:Math.round(76 * k), overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</span>""",
    'nev szelesseg')

sub("""                      fill={tone} stroke={T.surface} strokeWidth="2.5" />""",
    """                      fill={tone} stroke={T.surface} strokeWidth={2.5 * k} />""",
    'cikkely-hatar')

sub("const APP_VERSION = 'v10.250';", "const APP_VERSION = 'v10.251';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a kerek kitolti a szelesseget')
