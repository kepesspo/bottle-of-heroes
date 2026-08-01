#!/usr/bin/env python3
# v10.273 — a buntetes-modal harom finomitasa
#
#   1. Egyszerre 5 sor latszik, onnantol gorgetheto.
#      Eddig `maxHeight:'42vh'` volt — keszulektol fuggoen hol 4, hol 7 sor
#      fert ki, es sosem allt meg pont egy sor hatarnal. Most sor-alapu a
#      korlat. A ket szam MERVE, nem tippelve: egy sor 48 px (34 px-es avatar
#      + 2×7 px padding), a res 8 px, tehat 5 sor = 5*48 + 4*8 = 272 px.
#      Konstansban all, hogy egyutt valtozzon a sor tenyleges meretevel.
#
#   2. A szam melle sorosbogre kerul:  −  [3 🍺]  +
#      A regi also lapon ez megvolt, a modalra atirasnal kiesett. A `minWidth`
#      egyszerre fogadja be a "–" es a "3 🍺" valtozatot, kulonben a sor
#      szelessege ugralna az elso koppintasnal.
#
#   3. A zaro gombrol lekerul a pipa ("2 korty kiosztva ✔" -> "2 korty kiosztva").
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. sor-alapu magassag ────────────────────────────────────────────────────
sub("""  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  const stepBtn = (extra) => ({ width:30, height:30, borderRadius:9, border:'none', flexShrink:0,
    fontFamily:T.font, fontSize:17, fontWeight:900, lineHeight:1, display:'grid', placeItems:'center', ...extra });""",
    """  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  // Egyszerre 5 sor latszik, onnantol gorgetheto. A szamok MERVE: egy sor
  // 48 px magas (34 px avatar + 2×7 px padding), a res 8 px. Ha a sor merete
  // valtozik, ITT kell kovetni — igy a lista mindig pont sor-hataron all meg.
  const ROW_H = 48, ROW_GAP = 8, VISIBLE_ROWS = 5;
  const listMax = VISIBLE_ROWS * ROW_H + (VISIBLE_ROWS - 1) * ROW_GAP;
  const stepBtn = (extra) => ({ width:30, height:30, borderRadius:9, border:'none', flexShrink:0,
    fontFamily:T.font, fontSize:17, fontWeight:900, lineHeight:1, display:'grid', placeItems:'center', ...extra });""",
    'sor konstansok')

sub("""        <div style={{ display:'flex', flexDirection:'column', gap:8, maxHeight:'42vh', overflowY:'auto' }}>
          {players.map(p => {
            const cnt = drinks[p.id]||0;""",
    """        <div style={{ display:'flex', flexDirection:'column', gap:ROW_GAP, maxHeight:listMax, overflowY:'auto' }}>
          {players.map(p => {
            const cnt = drinks[p.id]||0;""",
    'lista magassag')

# ── 2. sorosbogre a szam mellett ─────────────────────────────────────────────
sub("""                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, minWidth:30, textAlign:'center',
                                 color: cnt>0 ? T.coral : T.inkMute, fontVariantNumeric:'tabular-nums' }}>{cnt>0 ? cnt : '–'}</span>""",
    """                  {/* − [szam 🍺] + — a minWidth egyszerre fogadja be a "–"-t es a
                      "3 🍺"-t, kulonben a sor szelessege ugralna az elso koppintasnal */}
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, minWidth:44, textAlign:'center',
                                 color: cnt>0 ? T.coral : T.inkMute, fontVariantNumeric:'tabular-nums',
                                 display:'inline-flex', alignItems:'center', justifyContent:'center', gap:3 }}>
                    {cnt>0 ? <React.Fragment>{cnt}<BohIcon name="beer" size={14} /></React.Fragment> : '–'}
                  </span>""",
    'soros ikon')

# ── 3. pipa le a zaro gombrol ────────────────────────────────────────────────
sub("""          {total>0 ? `${total} korty kiosztva ✔` : 'Senki sem iszik ✔'}""",
    """          {total>0 ? `${total} korty kiosztva` : 'Senki sem iszik'}""",
    'pipa le')

sub("const APP_VERSION = 'v10.272';", "const APP_VERSION = 'v10.273';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — 5 sor + soros ikon + pipa nelkul')
