#!/usr/bin/env python3
# v9.807: BJ — separate "Tét" and chip-stack (zseton) info into two distinct pills
import io

PATH = 'index.html'
c = io.open(PATH, encoding='utf-8').read()

def rep(old, new):
    global c
    assert old in c, 'OLD not found: ' + old[:80]
    assert c.count(old) == 1, 'OLD not unique: ' + old[:80]
    c = c.replace(old, new)

PILL = "background:T.surfaceMuted, borderRadius:10, padding:'4px 8px'"

# 1) Observer "Én sáv" top row — Tét pill + chips pill
OLD1 = """            <span style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:8 }}>
              {inRound && <span style={{ fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.inkSoft }}>Tét: {myBet}</span>}
              <BJChipStack count={myChips} size={54} />
            </span>"""
NEW1 = """            <span style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:8 }}>
              {inRound && <span style={{ display:'inline-flex', alignItems:'center', """ + PILL + """, fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.inkSoft, whiteSpace:'nowrap' }}>Tét: {myBet} 🍺</span>}
              <span style={{ display:'inline-flex', alignItems:'center', """ + PILL + """ }}><BJChipStack count={myChips} size={54} /></span>
            </span>"""
rep(OLD1, NEW1)

# 2) Host PlayingView player rows — split "· tét X" + chip stack into two pills
OLD2 = """                  <span style={{ color:T.inkSoft, fontWeight:400, whiteSpace:'nowrap' }}>· tét {bjState.bets[pid] || 1}</span>
                  <BJChipStack count={(bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid)} size={34} />"""
NEW2 = """                  <span style={{ display:'inline-flex', alignItems:'center', """ + PILL + """, fontSize:11, color:T.inkSoft, fontWeight:700, whiteSpace:'nowrap' }}>Tét {bjState.bets[pid] || 1} 🍺</span>
                  <span style={{ display:'inline-flex', alignItems:'center', """ + PILL + """ }}><BJChipStack count={(bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid)} size={34} /></span>"""
rep(OLD2, NEW2)

# 3) Host ResultsView rows — delta pill + chips pill (was one merged span)
OLD3 = """                <span style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:6, fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft }}>
                  <span>{res.delta > 0 ? '+' : ''}{res.delta} →</span>
                  <BJChipStack count={chips} size={34} />
                </span>"""
NEW3 = """                <span style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:6, fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft }}>
                  <span style={{ display:'inline-flex', alignItems:'center', """ + PILL + """, whiteSpace:'nowrap' }}>{res.delta > 0 ? '+' : ''}{res.delta} 🍺</span>
                  <span style={{ display:'inline-flex', alignItems:'center', """ + PILL + """ }}><BJChipStack count={chips} size={34} /></span>
                </span>"""
rep(OLD3, NEW3)

# Version bump
assert c.count("'v9.805'") == 1
c = c.replace("'v9.805'", "'v9.807'")

io.open(PATH, 'w', encoding='utf-8').write(c)
print('patch_bj_pills OK')
