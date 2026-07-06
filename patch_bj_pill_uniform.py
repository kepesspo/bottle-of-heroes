#!/usr/bin/env python3
# v9.808 — BJ uniform pill sizing: shared pill style per site, hideCount on BJChipStack
import io

P = '/home/user/bottle-of-heroes/index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new):
    global c
    assert old in c, 'OLD not found: ' + old[:80]
    assert c.count(old) == 1, 'OLD not unique: ' + old[:80]
    c = c.replace(old, new)

# 1) BJChipStack: hideCount prop
rep("function BJChipStack({ count, size }) {",
    "function BJChipStack({ count, size, hideCount }) {")
rep("""      <span style={{ display:'inline-flex', alignItems:'baseline', gap:2, fontFamily:T.font, fontWeight:900, fontSize:Math.round(s*0.34), color: grey ? '#8a8f94' : col, lineHeight:1, whiteSpace:'nowrap' }}>
        {n}<span style={{ fontSize:Math.max(9, Math.round(s*0.26)) }}>🍺</span>
      </span>""",
    """      {!hideCount && <span style={{ display:'inline-flex', alignItems:'baseline', gap:2, fontFamily:T.font, fontWeight:900, fontSize:Math.round(s*0.34), color: grey ? '#8a8f94' : col, lineHeight:1, whiteSpace:'nowrap' }}>
        {n}<span style={{ fontSize:Math.max(9, Math.round(s*0.26)) }}>🍺</span>
      </span>}""")

PILL_SMALL = "{ display:'inline-flex', alignItems:'center', gap:4, background:T.surfaceMuted, borderRadius:10, padding:'0 10px', height:26, fontFamily:T.font, fontWeight:800, fontSize:11, color:T.ink }"
PILL_BIG = "{ display:'inline-flex', alignItems:'center', gap:4, background:T.surfaceMuted, borderRadius:10, padding:'0 10px', height:40, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }"

# 2) Host PlayingView row (~46321-46329): shared pillS + uniform pills
rep("          const canDouble = hand.length === 2 && !bjState.doubled[pid];",
    "          const canDouble = hand.length === 2 && !bjState.doubled[pid];\n"
    "          const rowChips = (bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid);\n"
    "          const pillS = " + PILL_SMALL + ";")
rep("""<span style={{ display:'inline-flex', alignItems:'center', background:T.surfaceMuted, borderRadius:10, padding:'4px 8px', fontSize:11, color:T.inkSoft, fontWeight:700, whiteSpace:'nowrap' }}>Tét {bjState.bets[pid] || 1} 🍺</span>
                  <span style={{ display:'inline-flex', alignItems:'center', background:T.surfaceMuted, borderRadius:10, padding:'4px 8px' }}><BJChipStack count={(bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid)} size={34} /></span>""",
    """<span style={{ ...pillS, whiteSpace:'nowrap' }}>Tét {bjState.bets[pid] || 1} 🍺</span>
                  <span style={{ ...pillS, whiteSpace:'nowrap' }}><BJChipStack count={rowChips} size={20} hideCount /><span>{rowChips} 🍺</span></span>""")

# 3) Host ResultsView row (~46378-46393): shared pillS + uniform pills
rep("          const diff = chips - startStack;",
    "          const diff = chips - startStack;\n"
    "          const pillS = " + PILL_SMALL + ";")
rep("""<span style={{ display:'inline-flex', alignItems:'center', background:T.surfaceMuted, borderRadius:10, padding:'4px 8px', whiteSpace:'nowrap' }}>{res.delta > 0 ? '+' : ''}{res.delta} 🍺</span>
                  <span style={{ display:'inline-flex', alignItems:'center', background:T.surfaceMuted, borderRadius:10, padding:'4px 8px' }}><BJChipStack count={chips} size={34} /></span>""",
    """<span style={{ ...pillS, whiteSpace:'nowrap' }}>{res.delta > 0 ? '+' : ''}{res.delta} 🍺</span>
                  <span style={{ ...pillS, whiteSpace:'nowrap' }}><BJChipStack count={chips} size={20} hideCount /><span>{chips} 🍺</span></span>""")

# 4) Observer "Én sáv" (~46652-46653): shared pillS + uniform pills
rep("  const setMyBet = (v) => { if (typeof syncRoom === 'function') syncRoom(code, { bjState: { bets: { [playerId]: Math.max(1, Math.min(myChips, v)) } } }); };",
    "  const setMyBet = (v) => { if (typeof syncRoom === 'function') syncRoom(code, { bjState: { bets: { [playerId]: Math.max(1, Math.min(myChips, v)) } } }); };\n"
    "  const pillS = " + PILL_BIG + ";")
rep("""{inRound && <span style={{ display:'inline-flex', alignItems:'center', background:T.surfaceMuted, borderRadius:10, padding:'4px 8px', fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.inkSoft, whiteSpace:'nowrap' }}>Tét: {myBet} 🍺</span>}
              <span style={{ display:'inline-flex', alignItems:'center', background:T.surfaceMuted, borderRadius:10, padding:'4px 8px' }}><BJChipStack count={myChips} size={54} /></span>""",
    """{inRound && <span style={{ ...pillS, whiteSpace:'nowrap' }}>Tét: {myBet} 🍺</span>}
              <span style={{ ...pillS, whiteSpace:'nowrap' }}><BJChipStack count={myChips} size={30} hideCount /><span>{myChips} 🍺</span></span>""")

# 5) Version bump
assert c.count("v9.807") == 1
c = c.replace("const APP_VERSION = 'v9.807';", "const APP_VERSION = 'v9.808';")

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
