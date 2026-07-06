#!/usr/bin/env python3
# v9.803: BJ — dealer-only slow card animation, broke players can rebuy after round start
import io

P = 'index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global c
    assert c.count(old) == cnt, f'anchor not found or wrong count ({c.count(old)} != {cnt}): {old[:80]!r}'
    c = c.replace(old, new, cnt)

# ── 1) BJCardEl: animation only via `animate` prop, slower ──
rep("function BJCardEl({ card, faceDown, small }) {",
    "function BJCardEl({ card, faceDown, small, animate }) {")
rep("placeItems:'center', fontSize:small?18:24, flexShrink:0, animation:'bjDeal .3s ease-out' }}>🂠</div>",
    "placeItems:'center', fontSize:small?18:24, flexShrink:0, animation: animate ? 'bjDeal .7s ease-out' : undefined }}>🂠</div>")
rep("padding:'3px 5px', flexShrink:0, userSelect:'none', animation:'bjDeal .3s ease-out' }}>",
    "padding:'3px 5px', flexShrink:0, userSelect:'none', animation: animate ? 'bjDeal .7s ease-out' : undefined }}>")

# host PlayingView dealer hand
rep("{(bjState.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} faceDown={i === 1 && !revealed} />)}",
    "{(bjState.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} faceDown={i === 1 && !revealed} animate={i >= 1 && revealed} />)}")
# host ResultsView dealer hand
rep("{(bjState.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} small />)}",
    "{(bjState.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} small animate={i >= 1} />)}")
# observer dealer hand
rep("{(bj.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} faceDown={i === 1 && !revealed} small />)}",
    "{(bj.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} faceDown={i === 1 && !revealed} small animate={i >= 1 && revealed} />)}")

# ── 2) brokeDrank flag + broke rebuy after round start ──

# guestRebuy: skip booking if already drank; clear flag on re-seed
rep("""  const guestRebuy = (drinkN, newStack) => {
    if (drinkN > 0) bjBookDrinksRemote(code, playerId, drinkN);
    bjWrite(code, { ...bj, stacks: { ...(bj.stacks || {}), [playerId]: newStack }, chips: { ...(bj.chips || {}), [playerId]: newStack }, cashedOut: { ...(bj.cashedOut || {}), [playerId]: false } });""",
    """  const guestRebuy = (drinkN, newStack) => {
    if (drinkN > 0 && !(bj.brokeDrank || {})[playerId]) bjBookDrinksRemote(code, playerId, drinkN);
    bjWrite(code, { ...bj, stacks: { ...(bj.stacks || {}), [playerId]: newStack }, chips: { ...(bj.chips || {}), [playerId]: newStack }, cashedOut: { ...(bj.cashedOut || {}), [playerId]: false }, brokeDrank: { ...(bj.brokeDrank || {}), [playerId]: false } });""")

# observer results broke "Kiszállok": guard + set flag
rep("onClick={() => { bjBookDrinksRemote(code, playerId, startStack); bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } }); }}",
    "onClick={() => { if (!(bj.brokeDrank || {})[playerId]) bjBookDrinksRemote(code, playerId, startStack); bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true }, brokeDrank: { ...(bj.brokeDrank || {}), [playerId]: true } }); }}")

# host offline hostRebuy: guard + clear flag
rep("""  function hostRebuy(pid, mustDrink, newStack) {
    if (mustDrink) bookDrinks(pid, stackOf(pid));
    update({ ...bjState, stacks: { ...(bjState.stacks || {}), [pid]: newStack }, chips: { ...(bjState.chips || {}), [pid]: newStack }, cashedOut: { ...(bjState.cashedOut || {}), [pid]: false } });""",
    """  function hostRebuy(pid, mustDrink, newStack) {
    if (mustDrink && !(bjState.brokeDrank || {})[pid]) bookDrinks(pid, stackOf(pid));
    update({ ...bjState, stacks: { ...(bjState.stacks || {}), [pid]: newStack }, chips: { ...(bjState.chips || {}), [pid]: newStack }, cashedOut: { ...(bjState.cashedOut || {}), [pid]: false }, brokeDrank: { ...(bjState.brokeDrank || {}), [pid]: false } });""")

# host offline broke "Megitta — kiszáll" button: set flag
rep("<button onClick={() => update({ ...bjState, cashedOut: { ...(bjState.cashedOut || {}), [pid]: true } })} style={{ flex:1, padding:'9px', borderRadius:10, border:'none', background:'#555', fontFamily:T.font, fontWeight:800, fontSize:12, color:'#fff', cursor:'pointer' }}>🚪 Megitta — kiszáll</button>",
    "<button onClick={() => update({ ...bjState, cashedOut: { ...(bjState.cashedOut || {}), [pid]: true }, brokeDrank: { ...(bjState.brokeDrank || {}), [pid]: true } })} style={{ flex:1, padding:'9px', borderRadius:10, border:'none', background:'#555', fontFamily:T.font, fontWeight:800, fontSize:12, color:'#fff', cursor:'pointer' }}>🚪 Megitta — kiszáll</button>")

# startRound: clear brokeDrank for players seeded with chips>0
rep("""    const parts = claimed.filter(pid => !(bjState.cashedOut || {})[pid] && chips[pid] > 0);
    if (!parts.length) return;
    const bets = {}; parts.forEach(pid => bets[pid] = Math.max(1, Math.min((bjState.bets || {})[pid] || 1, chips[pid])));
    update({ ...bjState, phase:'betting', participants: parts, chips, bets, betsDone: {}, deck: bjNewDeck(), hands: {}, dealerHand: [], stood: {}, bust: {}, doubled: {}, currentTurn: null });""",
    """    const parts = claimed.filter(pid => !(bjState.cashedOut || {})[pid] && chips[pid] > 0);
    if (!parts.length) return;
    const brokeDrank = { ...(bjState.brokeDrank || {}) };
    claimed.forEach(pid => { if (chips[pid] > 0) delete brokeDrank[pid]; });
    const bets = {}; parts.forEach(pid => bets[pid] = Math.max(1, Math.min((bjState.bets || {})[pid] || 1, chips[pid])));
    update({ ...bjState, phase:'betting', participants: parts, chips, bets, betsDone: {}, deck: bjNewDeck(), hands: {}, dealerHand: [], stood: {}, bust: {}, doubled: {}, currentTurn: null, brokeDrank });""")

# observer not-inRound branch: broke rebuy UI when !amOut && myChips === 0
OLD_NOTIN = """        {bj.phase !== 'joining' && !inRound && (
          <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:44 }}>{amOut ? '🚪' : '⏳'}</div>"""
NEW_NOTIN = """        {bj.phase !== 'joining' && !inRound && !amOut && myChips === 0 && (
          <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:44 }}>💀</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.coral, marginTop:8 }}>Elfogyott a készleted!</div>
            <div style={{ fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.coral, marginTop:6 }}>Igyál {startStack} kortyot!</div>
            {!rebuyPick && (
              <div style={{ display:'flex', gap:8, marginTop:14 }}>
                <button onClick={() => setRebuyPick({ drinkN: startStack })} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🔄 Megittam — újra beszállok</button>
                <button onClick={() => { if (!(bj.brokeDrank || {})[playerId]) bjBookDrinksRemote(code, playerId, startStack); bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true }, brokeDrank: { ...(bj.brokeDrank || {}), [playerId]: true } }); }} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:'#555', fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🚪 Kiszállok</button>
              </div>
            )}
            {rebuyPick && (
              <BJStackPicker onConfirm={v => guestRebuy(rebuyPick.drinkN, v)} onCancel={() => setRebuyPick(null)} />
            )}
          </div>
        )}

        {bj.phase !== 'joining' && !inRound && (amOut || myChips > 0) && (
          <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:44 }}>{amOut ? '🚪' : '⏳'}</div>"""
rep(OLD_NOTIN, NEW_NOTIN)

# ── version bump ──
assert c.count('v9.802') == 1, c.count('v9.802')
c = c.replace('v9.802', 'v9.803')

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
