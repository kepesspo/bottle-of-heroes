#!/usr/bin/env python3
# v9.801 — BJ joining UI: mandatory stack choice, full-width pickers, compact QR row, hide round prompt
import io

P = 'index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global c
    assert c.count(old) == cnt, 'anchor not found or not unique (%d): %r' % (c.count(old), old[:80])
    c = c.replace(old, new, cnt)

# ── 1a. Remove the "Alap kortykészlet" card from JoiningView ──
OLD = """        <div style={{ background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Alap kortykészlet (aki nem választ) 🍺</div>
          <div style={{ display:'flex', gap:8 }}>
            {[5, 10, 20].map(v => (
              <button key={v} onClick={() => update({ ...bjState, startStack: v })} style={{ flex:1, padding:'12px 0', borderRadius:12, border:`2px solid ${(bjState.startStack || 10) === v ? T.mint : T.surfaceMuted}`, background: (bjState.startStack || 10) === v ? T.mintSoft : 'transparent', fontFamily:T.font, fontWeight:900, fontSize:17, color: (bjState.startStack || 10) === v ? T.mint : T.inkSoft, cursor:'pointer' }}>{v}</button>
            ))}
          </div>
          <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:8 }}>Kiszálláskor: aki ez alatt van, a különbséget issza — aki felette, kiosztja</div>
        </div>
"""
rep(OLD, '')

# ── 1b. Kezdés gated on everyone having chosen a stack ──
OLD = """  const JoiningView = () => {
    const joined = players.filter(p => takenIds.includes(p.id));
    return ("""
NEW = """  const JoiningView = () => {
    const joined = players.filter(p => takenIds.includes(p.id));
    const chosenCount = joined.filter(p => ((bjState && bjState.stacks) || {})[p.id] !== undefined).length;
    const allChosen = joined.length > 0 && chosenCount === joined.length;
    return ("""
rep(OLD, NEW)

OLD = """        <button onClick={hostStart} disabled={joined.length === 0} style={{ width:'100%', padding:'14px', borderRadius:16, background: joined.length ? T.mint : T.surfaceMuted, border:'none', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor: joined.length ? 'pointer' : 'default' }}>
          Kezdés ({joined.length} játékos)
        </button>"""
NEW = """        <button onClick={hostStart} disabled={!allChosen} style={{ width:'100%', padding:'14px', borderRadius:16, background: allChosen ? T.mint : T.surfaceMuted, border:'none', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor: allChosen ? 'pointer' : 'default' }}>
          {allChosen ? `Kezdés (${joined.length} játékos)` : joined.length === 0 ? 'Kezdés (0 játékos)' : `Várakozás a készlet-választásra… (${chosenCount}/${joined.length})`}
        </button>"""
rep(OLD, NEW)

# ── 1c. Joined list: show "választ…" until the player picked a stack ──
OLD = """              <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:12, fontWeight:T.weightTitle, color:T.mint }}>✓ Kész · {stackOf(p.id)} 🍺</span>"""
NEW = """              <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:12, fontWeight:T.weightTitle, color: ((bjState && bjState.stacks) || {})[p.id] !== undefined ? T.mint : T.inkSoft }}>{((bjState && bjState.stacks) || {})[p.id] !== undefined ? `✓ Kész · ${stackOf(p.id)} 🍺` : 'választ… 🍺'}</span>"""
rep(OLD, NEW)

# ── 3a. Compact header row in JoiningView (replaces big emoji + title, adds QR pill) ──
OLD = """      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ textAlign:'center', marginBottom:14 }}>
          <div style={{ fontSize:44 }}>🂡</div>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:T.ink, textTransform:'uppercase', letterSpacing:'0.04em', marginTop:4 }}>Csatlakozás</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:4 }}>A játékosok a telefonjukon válasszák ki magukat — mindenki a gép ellen játszik!</div>
        </div>"""
NEW = """      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:12 }}>
          <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontSize:12, color:T.inkSoft, lineHeight:1.35 }}>A játékosok a telefonjukon csatlakoznak — mindenki a gép ellen játszik!</div>
          {roomUrl && (
            <button onClick={() => setShowQR(true)} style={{ flexShrink:0, background:'transparent', border:`1.5px solid ${T.surfaceMuted}`, borderRadius:20, padding:'8px 14px', fontFamily:T.font, fontSize:13, fontWeight:800, color:T.inkSoft, cursor:'pointer', display:'flex', alignItems:'center', gap:6 }}>
              <span>📱</span> QR
            </button>
          )}
        </div>"""
rep(OLD, NEW)

# ── 3b. Remove standalone centered QR button row from outer return ──
OLD = """      {isOnline && roomUrl && bjState.phase === 'joining' && (
        <div style={{ display:'flex', justifyContent:'center', marginBottom:8 }}>
          <button onClick={() => setShowQR(true)} style={{ background:'transparent', border:`1.5px solid ${T.surfaceMuted}`, borderRadius:20, padding:'6px 16px', fontFamily:T.font, fontSize:13, color:T.inkSoft, cursor:'pointer', display:'flex', alignItems:'center', gap:6 }}>
            <span>📱</span> QR kód — csatlakozás
          </button>
        </div>
      )}
"""
rep(OLD, '')

# ── 2a. Observer joining picker: full-width vertical boxes ──
OLD = """              <div style={{ display:'flex', gap:8 }}>
                {[5, 10, 20].map(v => {
                  const sel = stackOf(playerId) === v;
                  return (
                    <button key={v} onClick={() => { if (typeof syncRoom === 'function') syncRoom(code, { bjState: { stacks: { [playerId]: v } } }); }} style={{ flex:1, padding:'12px 0', borderRadius:12, border:`2px solid ${sel ? T.mint : T.surfaceMuted}`, background: sel ? T.mintSoft : 'transparent', fontFamily:T.font, fontWeight:900, fontSize:17, color: sel ? T.mint : T.inkSoft, cursor:'pointer' }}>{v}</button>
                  );
                })}
              </div>"""
NEW = """              <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                {[5, 10, 20].map(v => {
                  const sel = ((bj && bj.stacks) || {})[playerId] === v;
                  return (
                    <button key={v} onClick={() => { if (typeof syncRoom === 'function') syncRoom(code, { bjState: { stacks: { [playerId]: v } } }); }} style={{ width:'100%', padding:'14px 0', borderRadius:12, border:`2px solid ${sel ? T.mint : T.surfaceMuted}`, background: sel ? T.mintSoft : 'transparent', fontFamily:T.font, fontWeight:900, fontSize:19, color: sel ? T.mint : T.inkSoft, cursor:'pointer' }}>{v} 🍺</button>
                  );
                })}
              </div>"""
rep(OLD, NEW)

# ── 2b. BJStackPicker (rebuy): full-width vertical boxes ──
OLD = """      <div style={{ display:'flex', gap:6 }}>
        {[5, 10, 20].map(v => (
          <button key={v} onClick={() => setSel(v)} style={{ flex:1, padding:'9px 0', borderRadius:10, border:`2px solid ${sel === v ? T.mint : 'transparent'}`, background: sel === v ? T.mintSoft : T.surface, fontFamily:T.font, fontWeight:900, fontSize:15, color: sel === v ? T.mint : T.inkSoft, cursor:'pointer' }}>{v}</button>
        ))}
      </div>"""
NEW = """      <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
        {[5, 10, 20].map(v => (
          <button key={v} onClick={() => setSel(v)} style={{ width:'100%', padding:'14px 0', borderRadius:10, border:`2px solid ${sel === v ? T.mint : 'transparent'}`, background: sel === v ? T.mintSoft : T.surface, fontFamily:T.font, fontWeight:900, fontSize:17, color: sel === v ? T.mint : T.inkSoft, cursor:'pointer' }}>{v} 🍺</button>
        ))}
      </div>"""
rep(OLD, NEW)

# ── 4. Hide "Ki nyert a körben?" prompt for blackjack ──
OLD = """        {currentGameId !== 'busz' && currentGameId !== 'utveszto' && (
          <div style={{ fontFamily:T.font, fontSize:14, fontWeight:600, color:T.inkSoft, textAlign:'center', maxWidth:280, lineHeight:1.4, alignSelf:'center' }}>
            {scenario.prompt}
          </div>
        )}"""
NEW = """        {currentGameId !== 'busz' && currentGameId !== 'utveszto' && currentGameId !== 'blackjack' && (
          <div style={{ fontFamily:T.font, fontSize:14, fontWeight:600, color:T.inkSoft, textAlign:'center', maxWidth:280, lineHeight:1.4, alignSelf:'center' }}>
            {scenario.prompt}
          </div>
        )}"""
rep(OLD, NEW)

# ── Version bump ──
assert c.count('v9.800') == 1
c = c.replace('v9.800', 'v9.801')
assert c.count('v9.801') == 1

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
