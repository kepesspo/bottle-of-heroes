#!/usr/bin/env python3
# v9.802 — BJ: host plays via view switch + casino chip stack design
import io

P = 'index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global c
    assert old in c, 'MISSING ANCHOR: ' + old[:80]
    assert c.count(old) == cnt, 'ANCHOR COUNT %d != %d: %s' % (c.count(old), cnt, old[:80])
    c = c.replace(old, new)

# ── 0) Version bump ──
assert c.count("'v9.801'") == 1
rep("'v9.801'", "'v9.802'")

# ── A1) GameContent route: pass onSetBuszSwitch to BlackjackGame ──
rep("if (gameId === 'blackjack') return <BlackjackGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={roomCode} gameMeta={gameMeta} onAdvance={onAdvance} onSetHideFooter={onSetHideFooter} onLiveDrinkUpdate={onLiveDrinkUpdate} />;",
    "if (gameId === 'blackjack') return <BlackjackGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={roomCode} gameMeta={gameMeta} onAdvance={onAdvance} onSetHideFooter={onSetHideFooter} onLiveDrinkUpdate={onLiveDrinkUpdate} onSetBuszSwitch={onSetBuszSwitch} />;")

# ── B1) BJChipStack component + A2) BlackjackGame signature ──
OLD_SIG = "function BlackjackGame({ players, roomCode, gameIdx, gameMeta, onAdvance, onSetHideFooter, onLiveDrinkUpdate }) {"
NEW = """// ── Kaszinó zseton — kortykészlet vizuál ──
function BJChipStack({ count, size }) {
  const s = size || 44;
  const n = count || 0;
  const grey = n === 0;
  const col = grey ? '#B7BCC2' : n <= 5 ? '#F4977A' : n <= 12 ? '#E8B36A' : T.mint;
  return (
    <div style={{ width:s, height:s, borderRadius:'50%', background:col, position:'relative', display:'grid', placeItems:'center', flexShrink:0, boxShadow:'0 2px 6px rgba(0,0,0,0.2)' }}>
      <div style={{ position:'absolute', inset:Math.max(2, Math.round(s*0.05)), borderRadius:'50%', border:`${Math.max(2, Math.round(s*0.065))}px dashed rgba(255,255,255,0.92)`, boxSizing:'border-box' }} />
      <div style={{ position:'absolute', inset:Math.max(5, Math.round(s*0.2)), borderRadius:'50%', background:'rgba(255,255,255,0.94)' }} />
      <div style={{ position:'relative', textAlign:'center', lineHeight:1 }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:Math.round(s*0.32), color: grey ? '#8a8f94' : col }}>{n}</div>
        <div style={{ fontSize:Math.max(8, Math.round(s*0.18)), marginTop:1 }}>🍺</div>
      </div>
    </div>
  );
}

function BlackjackGame({ players, roomCode, gameIdx, gameMeta, onAdvance, onSetHideFooter, onLiveDrinkUpdate, onSetBuszSwitch }) {"""
rep(OLD_SIG, NEW)

# ── A3) hostViewMode state + switch registration (Busz-stílus) ──
rep("  const [hostRebuyPick, setHostRebuyPick] = React.useState(null); // pid — újra-beszállás készlet-választó",
"""  const [hostRebuyPick, setHostRebuyPick] = React.useState(null); // pid — újra-beszállás készlet-választó
  const [hostViewMode, setHostViewMode] = React.useState('host'); // 'host' | 'player' — a házigazda is játszhat
  const hostSelfIdRef = React.useRef(null); // a host által választott játékos-id, váltások közt megmarad
  React.useEffect(() => {
    if (onSetBuszSwitch) onSetBuszSwitch(isOnline ? { fn: () => setHostViewMode(m => m === 'host' ? 'player' : 'host'), badge: 0 } : null);
  }, [isOnline]);
  React.useEffect(() => () => { onSetBuszSwitch && onSetBuszSwitch(null); }, []);""")

# ── A4) render switch: host player-nézet (hookok UTÁN, csak a JSX vált) ──
rep("""  if (!bjState) return (
    <div style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center' }}>
      <span style={{ fontFamily:T.font, fontSize:16, color:T.inkSoft }}>Betöltés…</span>
    </div>
  );""",
"""  if (isOnline && hostViewMode === 'player' && room) {
    return <BlackjackObserverView room={room} code={roomCode} onLeave={() => setHostViewMode('host')} keepClaimOnUnmount={true} initialPlayerId={hostSelfIdRef.current} onPlayerIdChange={pid => { hostSelfIdRef.current = pid; }} />;
  }

  if (!bjState) return (
    <div style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center' }}>
      <span style={{ fontFamily:T.font, fontSize:16, color:T.inkSoft }}>Betöltés…</span>
    </div>
  );""")

# ── A5) ObserverView: új propok ──
rep("function BlackjackObserverView({ room, code, onLeave }) {",
    "function BlackjackObserverView({ room, code, onLeave, keepClaimOnUnmount, initialPlayerId, onPlayerIdChange }) {")
rep("""  const [playerId, setPlayerId] = React.useState(null);
  const [pendingId, setPendingId] = React.useState(null);""",
"""  const [playerId, setPlayerId] = React.useState(initialPlayerId || null);
  const [pendingId, setPendingId] = React.useState(null);""")
rep("""  React.useEffect(() => { playerIdRef.current = playerId; }, [playerId]);
  const [giftPool, setGiftPool] = React.useState(null); // kiszállási nyereség kiosztása""",
"""  React.useEffect(() => { playerIdRef.current = playerId; }, [playerId]);
  React.useEffect(() => { if (typeof onPlayerIdChange === 'function') onPlayerIdChange(playerId); }, [playerId]);
  const [giftPool, setGiftPool] = React.useState(null); // kiszállási nyereség kiosztása""")
rep("""bjTakenIds: firebase.firestore.FieldValue.arrayRemove(pid) }); } catch(e) {}
  }, [code]);
  React.useEffect(() => () => { releasePlayer(playerIdRef.current); }, []);""",
"""bjTakenIds: firebase.firestore.FieldValue.arrayRemove(pid) }); } catch(e) {}
  }, [code]);
  React.useEffect(() => () => { if (!keepClaimOnUnmount) releasePlayer(playerIdRef.current); }, []);""")

# ── B2) Observer Én sáv: zseton + Tét ──
rep("""          {bj.phase !== 'joining' && <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:13, color:T.inkSoft }}>Készlet: <b style={{ color: myChips < startStack ? T.coral : T.mint }}>{myChips}</b> 🍺{inRound ? ` · Tét: ${myBet}` : ''}</span>}""",
"""          {bj.phase !== 'joining' && (
            <span style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:8 }}>
              {inRound && <span style={{ fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.inkSoft }}>Tét: {myBet}</span>}
              <BJChipStack count={myChips} size={54} />
            </span>
          )}""")

# ── B3) Observer tét-kártya: zseton a stepper mellett ──
rep("""            <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:16 }}>A tét a kortykészletedből megy — max {myChips} 🍺</div>""",
"""            <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:12 }}>A tét a kortykészletedből megy — max {myChips} 🍺</div>
            <div style={{ display:'flex', justifyContent:'center', marginBottom:14 }}><BJChipStack count={myChips} size={44} /></div>""")

# ── B4) Observer results: zseton a "→ készleted" sorban ──
rep("""                      <div style={{ fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft, marginTop:4 }}>
                        {res.delta > 0 ? '+' : ''}{res.delta} 🍺 → készleted: {myChips}
                      </div>""",
"""                      <div style={{ fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft, marginTop:6, display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
                        <span>{res.delta > 0 ? '+' : ''}{res.delta} 🍺 → készleted:</span>
                        <BJChipStack count={myChips} size={34} />
                      </div>""")

# ── B5) Host BettingView sor: zseton ──
rep("""              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>Készlet: {chips} 🍺</div>
            </div>""",
"""              <div style={{ display:'flex', alignItems:'center', gap:6, marginTop:3 }}>
                <BJChipStack count={chips} size={34} />
                <span style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>készlet</span>
              </div>
            </div>""")

# ── B6) Host PlayingView sor: zseton ──
rep("""                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.ink, flex:1 }}>{p?.name || pid} <span style={{ color:T.inkSoft, fontWeight:400 }}>· tét {bjState.bets[pid] || 1} · készlet {(bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid)} 🍺</span></span>""",
"""                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.ink, flex:1, display:'flex', alignItems:'center', gap:6, minWidth:0 }}>
                  <span style={{ whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{p?.name || pid}</span>
                  <span style={{ color:T.inkSoft, fontWeight:400, whiteSpace:'nowrap' }}>· tét {bjState.bets[pid] || 1}</span>
                  <BJChipStack count={(bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid)} size={34} />
                </span>""")

# ── B7) Host ResultsView sor: zseton ──
rep("""                <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft }}>
                  {res.delta > 0 ? '+' : ''}{res.delta} → {chips} 🍺
                </span>""",
"""                <span style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:6, fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft }}>
                  <span>{res.delta > 0 ? '+' : ''}{res.delta} →</span>
                  <BJChipStack count={chips} size={34} />
                </span>""")

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
