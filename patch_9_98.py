#!/usr/bin/env python3
import sys
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# FIX 1 — Version bump
old = "const APP_VERSION = 'v9.97';"
new = "const APP_VERSION = 'v9.98';"
assert old in content, f'FIX 1 FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 1 FAILED: new string not in content'
print('FIX 1 done: version bump to v9.98')

# FIX 2 — Időpárbaj: show both players in idle phase
old = """      {/* Player result cards */}
      {(t1 !== null || t2 !== null || phase === 'result') && ("""
new = """      {/* Player result cards — always show in any phase */}
      {("""
assert old in content, 'FIX 2 FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 2 FAILED: new string not in content'
print('FIX 2 done: Időpárbaj player cards always shown')

# FIX 3 — Imposztor: make "Mindenki mondott" button prominent
old = """                <button onClick={() => { setTimerLeft(0); setVoteReady(true); }}
                  style={{ padding:'8px 20px', background:'rgba(255,255,255,0.08)', border:`1.5px solid rgba(255,255,255,0.18)`, color:'rgba(255,255,255,0.6)', fontFamily:T.font, fontWeight:600, fontSize:13, borderRadius:12, cursor:'pointer' }}>
                  Mindenki mondott → Szavazás
                </button>"""
new = """                <button onClick={() => { setTimerLeft(0); setVoteReady(true); }}
                  style={{ padding:'10px 22px', background:T.coral, border:'none', color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:14, borderRadius:12, cursor:'pointer', boxShadow:T.shadow }}>
                  ⏹ Mindenki mondott → Szavazás
                </button>"""
assert old in content, 'FIX 3 FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 3 FAILED: new string not in content'
print('FIX 3 done: Imposztor Mindenki mondott button made prominent')

# FIX 4a — Loverseny: remove auto-finish when winnerPool === 0
old = """  useEffect(() => {
    if (phase !== 'result') return;
    if (winnerPool === 0) {
      const t = setTimeout(() => finishGame(giftsRef.current), 400);
      return () => clearTimeout(t);
    }"""
new = """  useEffect(() => {
    if (phase !== 'result') return;
    if (winnerPool === 0) {
      // Don't auto-finish — show "everyone lost" banner, user must press button
      return;
    }"""
assert old in content, 'FIX 4a FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 4a FAILED: new string not in content'
print('FIX 4a done: Loverseny no auto-finish on winnerPool===0')

# FIX 4b — Loverseny: add "Mindenki veszített" banner in result phase
old = """        {winnerPool > 0 && remaining > 0 && (
          <div style={{ textAlign:'center', fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft }}>
            Még {remaining} korty kiosztható
          </div>
        )}
      </div>
    );
  }"""
new = """        {winnerPool > 0 && remaining > 0 && (
          <div style={{ textAlign:'center', fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft }}>
            Még {remaining} korty kiosztható
          </div>
        )}
        {winnerPool === 0 && (
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>
            <div style={{ textAlign:'center', padding:'14px 16px', borderRadius:16, background:`${T.coral}15`, border:`2px solid ${T.coral}`, animation:'popIn .4s' }}>
              <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:18, color:T.coral }}>😔 Mindenki veszített!</div>
              <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:4 }}>Senki sem fogadott a nyerő lóra</div>
            </div>
            <button onClick={() => finishGame(giftsRef.current)} style={{ width:'100%', padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, borderRadius:14, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
              Tovább →
            </button>
          </div>
        )}
      </div>
    );
  }"""
assert old in content, 'FIX 4b FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 4b FAILED: new string not in content'
print('FIX 4b done: Loverseny Mindenki veszített banner added')

# FIX 5 — Sohanem: auto-prime Kövi by calling onAdvance({}) on mount
old = """function SohanemGame({ gameIdx, onAdvance }) {
  const card = SOHANEM_CARDS[gameIdx % SOHANEM_CARDS.length];
  const cardNum = (gameIdx % SOHANEM_CARDS.length) + 1;
  const total = SOHANEM_CARDS.length;"""
new = """function SohanemGame({ gameIdx, onAdvance }) {
  const card = SOHANEM_CARDS[gameIdx % SOHANEM_CARDS.length];
  const cardNum = (gameIdx % SOHANEM_CARDS.length) + 1;
  const total = SOHANEM_CARDS.length;
  React.useEffect(() => { onAdvance && onAdvance({}); }, [gameIdx]);"""
assert old in content, 'FIX 5 FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 5 FAILED: new string not in content'
print('FIX 5 done: Sohanem auto-primes Kövi on mount')

# FIX 6a — Menu: add menuAddName and gameRestartKey state
old = "  const [showMenu, setShowMenu] = useState(false);"
new = """  const [showMenu, setShowMenu] = useState(false);
  const [menuAddName, setMenuAddName] = useState('');
  const [gameRestartKey, setGameRestartKey] = useState(0);"""
assert old in content, 'FIX 6a FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 6a FAILED: new string not in content'
print('FIX 6a done: Menu state vars added')

# FIX 6b — GameContent key includes gameRestartKey
old = "          <GameContent key={currentGameId + gameIdx} gameId={currentGameId}"
new = "          <GameContent key={currentGameId + gameIdx + '_' + gameRestartKey} gameId={currentGameId}"
assert old in content, 'FIX 6b FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 6b FAILED: new string not in content'
print('FIX 6b done: GameContent key includes gameRestartKey')

# FIX 6c — Menu: replace old 3-button row with new layout including add player + restart
old = """              <div style={{ display:'flex', gap:8 }}>
                <button onClick={() => { undoLast(); setShowMenu(false); }} disabled={!undoRef.current} style={{ flex:1, minHeight:56, border:`2px solid ${undoRef.current ? T.inkMute+'88' : T.inkMute+'33'}`, background:'transparent', color: undoRef.current ? T.inkSoft : T.inkMute+'55', fontFamily:T.font, fontWeight:700, fontSize:13, borderRadius:14, cursor: undoRef.current ? 'pointer' : 'default', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2 }}>
                  <span style={{ fontSize:16 }}>↩</span>
                  <span>Vissza</span>
                </button>
                <button onClick={() => { setGameIdx(g=>g+1); setShowMenu(false); }} style={{ flex:1, minHeight:56, border:`2px solid ${T.ink}`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, borderRadius:14, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2 }}>
                  <span style={{ fontSize:16 }}>⏭</span>
                  <span>Következő</span>
                </button>
                <button onClick={() => { setShowMenu(false); go('end'); }} style={{ flex:2, minHeight:56, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, borderRadius:14, cursor:'pointer', boxShadow:T.shadow }}>🏁 Kilépés</button>
              </div>
              <div style={{ height:52 }} />"""
new = """              {/* Add player row */}
              <div style={{ display:'flex', gap:8 }}>
                <input
                  value={menuAddName}
                  onChange={e => setMenuAddName(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && menuAddName.trim()) {
                      const PLAYER_COLORS = ['#5BA0DB','#E985B8','#F4C95A','#4FC2A0','#F97316','#A78BFA','#EF4444','#14B8A6','#F59E0B','#EC4899'];
                      const newP = { id: Date.now().toString(), name: menuAddName.trim(), drinks: 0, points: 0, color: PLAYER_COLORS[players.length % PLAYER_COLORS.length] };
                      setPlayers(prev => [...prev, newP]);
                      setMenuAddName('');
                    }
                  }}
                  placeholder="Új játékos neve..."
                  style={{ flex:1, padding:'12px 14px', border:`1.5px solid ${T.inkMute}44`, borderRadius:14, fontFamily:T.font, fontSize:14, color:T.ink, background:T.surface, outline:'none' }}
                />
                <button
                  disabled={!menuAddName.trim()}
                  onClick={() => {
                    if (!menuAddName.trim()) return;
                    const PLAYER_COLORS = ['#5BA0DB','#E985B8','#F4C95A','#4FC2A0','#F97316','#A78BFA','#EF4444','#14B8A6','#F59E0B','#EC4899'];
                    const newP = { id: Date.now().toString(), name: menuAddName.trim(), drinks: 0, points: 0, color: PLAYER_COLORS[players.length % PLAYER_COLORS.length] };
                    setPlayers(prev => [...prev, newP]);
                    setMenuAddName('');
                  }}
                  style={{ padding:'0 18px', borderRadius:14, border:'none', background: menuAddName.trim() ? T.mint : T.surfaceMuted, color: menuAddName.trim() ? '#fff' : T.inkMute, fontFamily:T.font, fontWeight:700, fontSize:14, cursor: menuAddName.trim() ? 'pointer' : 'default' }}>
                  ➕
                </button>
              </div>
              {/* Action buttons — 2 rows */}
              <div style={{ display:'flex', gap:8 }}>
                <button onClick={() => { undoLast(); setShowMenu(false); }} disabled={!undoRef.current} style={{ flex:1, minHeight:52, border:`2px solid ${undoRef.current ? T.inkMute+'88' : T.inkMute+'33'}`, background:'transparent', color: undoRef.current ? T.inkSoft : T.inkMute+'55', fontFamily:T.font, fontWeight:700, fontSize:13, borderRadius:14, cursor: undoRef.current ? 'pointer' : 'default', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2 }}>
                  <span style={{ fontSize:16 }}>↩</span>
                  <span>Vissza</span>
                </button>
                <button onClick={() => { setPendingCommit(null); setGameRestartKey(k=>k+1); setShowMenu(false); }} style={{ flex:1, minHeight:52, border:`2px solid ${T.ink}44`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:700, fontSize:13, borderRadius:14, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2 }}>
                  <span style={{ fontSize:16 }}>🔄</span>
                  <span>Játék újra</span>
                </button>
                <button onClick={() => { setGameIdx(g=>g+1); setShowMenu(false); }} style={{ flex:1, minHeight:52, border:`2px solid ${T.ink}`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, borderRadius:14, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2 }}>
                  <span style={{ fontSize:16 }}>⏭</span>
                  <span>Következő</span>
                </button>
              </div>
              <button onClick={() => { setShowMenu(false); go('end'); }} style={{ width:'100%', minHeight:52, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, borderRadius:14, cursor:'pointer', boxShadow:T.shadow }}>🏁 Kilépés</button>
              <div style={{ height:52 }} />"""
assert old in content, 'FIX 6c FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 6c FAILED: new string not in content'
print('FIX 6c done: Menu add player + restart buttons added')

# FIX 7a — OVFJ ObserverView: pre-fill previous round answers
old = """  React.useEffect(() => {
    if (ovfj.round && lastRoundRef.current !== ovfj.round) {
      lastRoundRef.current = ovfj.round;
      setLocalAns({}); setSubmitted(false); setMyVotes({});
    }
  }, [ovfj.round]);"""
new = """  const prevLocalAnsRef = React.useRef({});
  React.useEffect(() => {
    if (ovfj.round && lastRoundRef.current !== ovfj.round) {
      // Keep previous answers as defaults for new round
      const prev = lastRoundRef.current ? {...prevLocalAnsRef.current} : {};
      lastRoundRef.current = ovfj.round;
      setLocalAns(prev); setSubmitted(false); setMyVotes({});
    }
  }, [ovfj.round]);
  React.useEffect(() => { prevLocalAnsRef.current = localAns; }, [localAns]);"""
assert old in content, 'FIX 7a FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 7a FAILED: new string not in content'
print('FIX 7a done: OVFJ ObserverView pre-fills previous round answers')

# FIX 7b — OVFJ ObserverView: fix letter phase text
old = "        <div style={{fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,color:T.inkSoft,textAlign:'center'}}>A host felfedi a betűt...</div>"
new = "        <div style={{fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,color:T.inkSoft,textAlign:'center'}}>{ovfj.letter ? '✅ Betű kisorsolt — várj a startjelre!' : 'A host felfedi a betűt...'}</div>"
assert old in content, 'FIX 7b FAILED: old string not found'
content = content.replace(old, new, 1)
assert new in content, 'FIX 7b FAILED: new string not in content'
print('FIX 7b done: OVFJ letter phase text updated')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('v9.98 patch done!')
