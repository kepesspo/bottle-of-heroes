#!/usr/bin/env python3
# v10.279b — a PenaltyModal is a KOZOS sort hasznalja
#
# A v10.279-ben letrejott a `PlayerDrinkRow`, de a `PenaltyModal` meg a sajat,
# szo szerint azonos markupjat rajzolta. Ha csak a DrinkDistributor hasznalna,
# az egesz egysegesites elveszne az elso modositasnal — ezert a modal is atall
# ra. Ezzel a sor markupja EGY helyen van, es a lista-korlat is a kozos
# konstansokbol jon (DRINK_ROW_H / DRINK_ROW_GAP / DRINK_ROWS_VISIBLE).
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  // Egyszerre 5 sor latszik, onnantol gorgetheto. A szamok MERVE: egy sor
  // 48 px magas (34 px avatar + 2×7 px padding), a res 8 px. Ha a sor merete
  // valtozik, ITT kell kovetni — igy a lista mindig pont sor-hataron all meg.
  const ROW_H = 48, ROW_GAP = 8, VISIBLE_ROWS = 5;
  const listMax = VISIBLE_ROWS * ROW_H + (VISIBLE_ROWS - 1) * ROW_GAP;
  const stepBtn = (extra) => ({ width:30, height:30, borderRadius:9, border:'none', flexShrink:0,
    fontFamily:T.font, fontSize:17, fontWeight:900, lineHeight:1, display:'grid', placeItems:'center', ...extra });""",
    """  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  // A sor es a lista-korlat a KOZOS forrasbol jon (v10.279): ugyanaz a
  // `PlayerDrinkRow` es ugyanaz az 5 soros hatar, mint a jatekokban.""",
    'modal konstansok')

OLD_ROWS = """        <div style={{ display:'flex', flexDirection:'column', gap:ROW_GAP, maxHeight:listMax, overflowY:'auto' }}>
          {players.map(p => {
            const cnt = drinks[p.id]||0;
            return (
              <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, padding:'7px 10px',
                                       background:T.surfaceMuted, borderRadius:14 }}>
                <PlayerAvatar player={p} size={34} />
                <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink,
                              overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
                {/* − szám + — a te elrendezesed: avatar, nev, a masik oldalon a lepteto */}
                <div style={{ display:'flex', alignItems:'center', gap:6, flexShrink:0 }}>
                  <button onClick={()=>remove(p.id)} disabled={cnt===0}
                    style={stepBtn({ background: cnt>0 ? T.surface : 'transparent',
                                     color: cnt>0 ? T.inkSoft : T.inkMute,
                                     boxShadow: cnt>0 ? T.shadowPill : 'none',
                                     cursor: cnt>0 ? 'pointer' : 'default' })}>−</button>
                  {/* − [szam 🍺] + — a minWidth egyszerre fogadja be a "–"-t es a
                      "3 🍺"-t, kulonben a sor szelessege ugralna az elso koppintasnal */}
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, minWidth:44, textAlign:'center',
                                 color: cnt>0 ? T.coral : T.inkMute, fontVariantNumeric:'tabular-nums',
                                 display:'inline-flex', alignItems:'center', justifyContent:'center', gap:3 }}>
                    {cnt>0 ? <React.Fragment>{cnt}<BohIcon name="beer" size={14} /></React.Fragment> : '–'}
                  </span>
                  <button onClick={(e)=>{ add(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, `+${(drinks[p.id]||0)+1} 🍺`, T.coral); }}
                    style={stepBtn({ background: T.coral+'22', color:T.coral, cursor:'pointer' })}>+</button>
                </div>
              </div>
            );
          })}
        </div>"""

NEW_ROWS = """        <div style={{ display:'flex', flexDirection:'column', gap:DRINK_ROW_GAP, maxHeight:DRINK_LIST_MAX, overflowY:'auto' }}>
          {players.map(p => (
            <PlayerDrinkRow key={p.id} p={p} cnt={drinks[p.id]||0} onAdd={add} onRemove={remove} />
          ))}
        </div>"""
sub(OLD_ROWS, NEW_ROWS, 'modal sorok')

open(P, 'w', encoding='utf-8').write(src)
print('OK — a modal is a kozos sort hasznalja')
