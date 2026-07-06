#!/usr/bin/env python3
# v9.798 — Blackjack: per-player starting stack choice (5/10/20) for phone joiners
import io

P = '/home/user/bottle-of-heroes/index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new, n=1):
    global c
    assert c.count(old) == n, 'count %d != %d for: %r' % (c.count(old), n, old[:90])
    c = c.replace(old, new)

# ── 1) stacks: {} in both init sites ──
OLD = "currentTurn: null, startStack: 10, chips, cashedOut: {}, roundsPlayed: 0 });"
assert OLD in c
rep(OLD, "currentTurn: null, startStack: 10, stacks: {}, chips, cashedOut: {}, roundsPlayed: 0 });")

OLD = "currentTurn: null, startStack: 10, chips: {}, cashedOut: {}, roundsPlayed: 0 },"
assert OLD in c
rep(OLD, "currentTurn: null, startStack: 10, stacks: {}, chips: {}, cashedOut: {}, roundsPlayed: 0 },")

# ── 2) host: stackOf helper ──
OLD = """  function startRound() {
    const claimed = isOnline"""
assert OLD in c
rep(OLD, """  const stackOf = pid => ((bjState && bjState.stacks) || {})[pid] || (bjState && bjState.startStack) || 10;

  function startRound() {
    const claimed = isOnline""")

# ── 3) host startRound chip seeding ──
OLD = """    const chips = { ...(bjState.chips || {}) };
    const startStack = bjState.startStack || 10;
    claimed.forEach(pid => { if (chips[pid] === undefined) chips[pid] = startStack; });"""
assert OLD in c
rep(OLD, """    const chips = { ...(bjState.chips || {}) };
    claimed.forEach(pid => { if (chips[pid] === undefined) chips[pid] = stackOf(pid); });""")

# ── 4) host dealer-effect results chip fallback ──
OLD = """      const chips = { ...(bjState.chips || {}) };
      const startStack = bjState.startStack || 10;
      (bjState.participants || []).forEach(pid => {
        const r = bjResultFor(preState, pid);
        chips[pid] = Math.max(0, (chips[pid] === undefined ? startStack : chips[pid]) + r.delta);"""
assert OLD in c
rep(OLD, """      const chips = { ...(bjState.chips || {}) };
      (bjState.participants || []).forEach(pid => {
        const r = bjResultFor(preState, pid);
        chips[pid] = Math.max(0, (chips[pid] === undefined ? stackOf(pid) : chips[pid]) + r.delta);""")

# ── 5) hostCashOut ──
OLD = """  function hostCashOut(pid) {
    const startStack = bjState.startStack || 10;
    const ch = (bjState.chips || {})[pid] || 0;
    const diff = ch - startStack;"""
assert OLD in c
rep(OLD, """  function hostCashOut(pid) {
    const ch = (bjState.chips || {})[pid] || 0;
    const diff = ch - stackOf(pid);""")

# ── 6) hostRebuy ──
OLD = """  function hostRebuy(pid, mustDrink) {
    const startStack = bjState.startStack || 10;
    if (mustDrink) bookDrinks(pid, startStack);
    update({ ...bjState, chips: { ...(bjState.chips || {}), [pid]: startStack }, cashedOut: { ...(bjState.cashedOut || {}), [pid]: false } });
  }"""
assert OLD in c
rep(OLD, """  function hostRebuy(pid, mustDrink) {
    const st = stackOf(pid);
    if (mustDrink) bookDrinks(pid, st);
    update({ ...bjState, chips: { ...(bjState.chips || {}), [pid]: st }, cashedOut: { ...(bjState.cashedOut || {}), [pid]: false } });
  }""")

# ── 7) host BettingView + PlayingView chip fallback (2x identical) ──
OLD = "(bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : (bjState.startStack || 10)"
rep(OLD, "(bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid)", n=2)

# ── 8) host ResultsView per-player stack ──
OLD = """          const res = bjResultFor(bjState, pid);
          const startStack = bjState.startStack || 10;"""
assert OLD in c
rep(OLD, """          const res = bjResultFor(bjState, pid);
          const startStack = stackOf(pid);""")

# ── 9) host JoiningView: show chosen stack per joined player ──
OLD = "fontWeight:T.weightTitle, color:T.mint }}>✓ Kész</span>"
assert OLD in c
rep(OLD, "fontWeight:T.weightTitle, color:T.mint }}>✓ Kész · {stackOf(p.id)} 🍺</span>")

# ── 10) host JoiningView caption relabel ──
OLD = "letterSpacing:'0.07em', marginBottom:10 }}>Kezdő kortykészlet 🍺</div>"
assert OLD in c
rep(OLD, "letterSpacing:'0.07em', marginBottom:10 }}>Alap kortykészlet (aki nem választ) 🍺</div>")

# ── 11) observer: stackOf helper ──
OLD = """function BlackjackObserverView({ room, code, onLeave }) {
  const bj = room.bjState || null;"""
assert OLD in c
rep(OLD, """function BlackjackObserverView({ room, code, onLeave }) {
  const bj = room.bjState || null;
  const stackOf = pid => ((bj && bj.stacks) || {})[pid] || (bj && bj.startStack) || 10;""")

# ── 12) observer: my startStack per-player ──
OLD = """  const startStack = bj.startStack || 10;
  const myChips = (bj.chips || {})[playerId] !== undefined ? bj.chips[playerId] : startStack;"""
assert OLD in c
rep(OLD, """  const startStack = stackOf(playerId);
  const myChips = (bj.chips || {})[playerId] !== undefined ? bj.chips[playerId] : startStack;""")

# ── 13) observer "Többiek" results chip fallback ──
OLD = "${(bj.chips || {})[pid] !== undefined ? bj.chips[pid] : startStack} 🍺"
assert OLD in c
rep(OLD, "${(bj.chips || {})[pid] !== undefined ? bj.chips[pid] : stackOf(pid)} 🍺")

# ── 14) observer joining card: add stack picker ──
OLD = """        {bj.phase === 'joining' && (
          <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:44 }}>✅</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginTop:8 }}>Csatlakoztál!</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:6 }}>Várj, amíg a házigazda elindítja a játékot…</div>
          </div>
        )}"""
assert OLD in c
NEW = """        {bj.phase === 'joining' && (
          <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:44 }}>✅</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginTop:8 }}>Csatlakoztál!</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:6 }}>Várj, amíg a házigazda elindítja a játékot…</div>
            <div style={{ marginTop:20, paddingTop:16, borderTop:`1px solid ${T.surfaceMuted}` }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, marginBottom:10 }}>Mennyi kortyval szállsz be? 🍺</div>
              <div style={{ display:'flex', gap:8 }}>
                {[5, 10, 20].map(v => {
                  const sel = stackOf(playerId) === v;
                  return (
                    <button key={v} onClick={() => { if (typeof syncRoom === 'function') syncRoom(code, { bjState: { stacks: { [playerId]: v } } }); }} style={{ flex:1, padding:'12px 0', borderRadius:12, border:`2px solid ${sel ? T.mint : T.surfaceMuted}`, background: sel ? T.mintSoft : 'transparent', fontFamily:T.font, fontWeight:900, fontSize:17, color: sel ? T.mint : T.inkSoft, cursor:'pointer' }}>{v}</button>
                  );
                })}
              </div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:8 }}>Kezdésig bármikor módosíthatod</div>
            </div>
          </div>
        )}"""
rep(OLD, NEW)

# ── version bump ──
rep("const APP_VERSION = 'v9.797';", "const APP_VERSION = 'v9.798';")

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
