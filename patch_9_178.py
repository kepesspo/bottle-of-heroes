#!/usr/bin/env python3
"""patch_9_178.py — Tapper: observer view-on saját telefonnal is lehet nyomni"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.177';" in content
content = content.replace("const APP_VERSION = 'v9.177';", "const APP_VERSION = 'v9.178';")

# ── 1. Pass roomCode to TapperGame ──
OLD_TAPPER_RENDER = "if (gameId === 'tapper') return <TapperGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;"
NEW_TAPPER_RENDER = "if (gameId === 'tapper') return <TapperGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} roomCode={roomCode} />;"
assert OLD_TAPPER_RENDER in content, "TapperGame render not found"
content = content.replace(OLD_TAPPER_RENDER, NEW_TAPPER_RENDER, 1)

# ── 2. TapperGame: accept roomCode, sync Firestore inputs ──
OLD_TAPPER_FN = "function TapperGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {"
NEW_TAPPER_FN = "function TapperGame({ gameIdx, challenger, opponent, onAdvance, onResult, roomCode }) {"
assert OLD_TAPPER_FN in content, "TapperGame fn not found"
content = content.replace(OLD_TAPPER_FN, NEW_TAPPER_FN, 1)

# Insert Firestore listener after the existing reset useEffect
OLD_AFTER_RESET = """  React.useEffect(() => {
    setPhase('idle'); setP1Hold(false); setP2Hold(false);
    setCountdown(5.0); setP1Time(null); setP2Time(null);
    phaseRef.current = 'idle';
    p1HoldRef.current = false; p2HoldRef.current = false;
    p1TimeRef.current = null; p2TimeRef.current = null;
    clearInterval(ivRef.current);
    return () => clearInterval(ivRef.current);
  }, [gameIdx]);"""

NEW_AFTER_RESET = """  React.useEffect(() => {
    setPhase('idle'); setP1Hold(false); setP2Hold(false);
    setCountdown(5.0); setP1Time(null); setP2Time(null);
    phaseRef.current = 'idle';
    p1HoldRef.current = false; p2HoldRef.current = false;
    p1TimeRef.current = null; p2TimeRef.current = null;
    clearInterval(ivRef.current);
    // Clear tapper input in Firestore when game resets
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { tapperInput: null });
    return () => clearInterval(ivRef.current);
  }, [gameIdx]);

  // Listen to remote tapper inputs (observer phones)
  React.useEffect(() => {
    if (!roomCode || typeof subscribeRoom !== 'function') return;
    const unsub = subscribeRoom(roomCode, data => {
      if (!data?.tapperInput) return;
      const ti = data.tapperInput;
      const p1name = challenger?.name || '';
      const p2name = opponent?.name || '';
      const p1Remote = ti[p1name];
      const p2Remote = ti[p2name];
      if (p1Remote !== undefined) {
        if (p1Remote && !p1HoldRef.current) pressDown(1);
        else if (!p1Remote && p1HoldRef.current) pressUp(1);
      }
      if (p2Remote !== undefined) {
        if (p2Remote && !p2HoldRef.current) pressDown(2);
        else if (!p2Remote && p2HoldRef.current) pressUp(2);
      }
    });
    return () => unsub && unsub();
  }, [roomCode, gameIdx]);"""

assert OLD_AFTER_RESET in content, "TapperGame reset useEffect not found"
content = content.replace(OLD_AFTER_RESET, NEW_AFTER_RESET, 1)

# ── 3. Add TapperObserverView component before ObserverWatching ──
OLD_OBSERVER_WATCHING = "function ObserverWatching({ code, observerName, onLeave }) {"
NEW_OBSERVER_WATCHING = """function TapperObserverView({ code, room, observerName }) {
  const games = room.selectedGames || [];
  const gameIdx = room.gameIdx || 0;
  const p1 = room.players?.[0] || null;
  const p2 = room.players?.[1] || null;
  const challenger = room.players?.find(p => p.isCurrent) || room.players?.[gameIdx % Math.max(1, room.players?.length || 1)] || p1;
  const opponent = room.players?.find(p => p.id !== challenger?.id) || p2;

  const myPlayer = [challenger, opponent].find(p => p?.name === observerName) || null;
  const pNum = myPlayer?.id === challenger?.id ? 1 : 2;

  const [holding, setHolding] = React.useState(false);

  const setRemote = (down) => {
    if (!myPlayer || typeof syncRoom !== 'function') return;
    syncRoom(code, { tapperInput: { [myPlayer.name]: down } });
  };

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:24, background:T.bg, padding:24 }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.1em' }}>🍺 Tapper · {code}</div>
      {!myPlayer ? (
        <div style={{ textAlign:'center' }}>
          <div style={{ fontSize:40 }}>👀</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, color:T.ink, marginTop:12 }}>Megfigyelő mód</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:6 }}>A neved nem egyezik egyik játékossal sem.</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, marginTop:4 }}>Játékosok: {[challenger, opponent].filter(Boolean).map(p=>p.name).join(', ')}</div>
        </div>
      ) : (
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.inkSoft }}>{myPlayer.name}</div>
          <div
            onPointerDown={e => { e.preventDefault(); e.currentTarget.setPointerCapture(e.pointerId); setHolding(true); setRemote(true); }}
            onPointerUp={() => { setHolding(false); setRemote(false); }}
            onPointerCancel={() => { setHolding(false); setRemote(false); }}
            style={{
              width:200, height:200, borderRadius:100,
              background: myPlayer.color,
              boxShadow: holding
                ? `0 0 0 20px ${myPlayer.color}44, 0 0 0 40px ${myPlayer.color}18`
                : `0 0 0 12px rgba(255,255,255,0.8)`,
              display:'flex', alignItems:'center', justifyContent:'center',
              cursor:'pointer', userSelect:'none', WebkitUserSelect:'none', touchAction:'none',
              transform: holding ? 'scale(0.94)' : 'scale(1)',
              transition:'transform 0.1s, box-shadow 0.15s',
            }}
          >
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff', textAlign:'center', padding:'0 16px' }}>
              {holding ? '✊ TARTSD!' : '👇 NYOMJ!'}
            </div>
          </div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, textAlign:'center' }}>Tartsd lenyomva amíg bírod!</div>
        </div>
      )}
    </div>
  );
}

function ObserverWatching({ code, observerName, onLeave }) {"""

assert OLD_OBSERVER_WATCHING in content, "ObserverWatching not found"
content = content.replace(OLD_OBSERVER_WATCHING, NEW_OBSERVER_WATCHING, 1)

# ── 4. In ObserverWatching, detect tapper game and show TapperObserverView ──
OLD_OV_OVFJ = "  if (_ovCurG === 'ovfj') return <OVFJObserverView room={room} code={code} myName={observerName} onLeave={onLeave} />;"
NEW_OV_OVFJ = """  if (_ovCurG === 'ovfj') return <OVFJObserverView room={room} code={code} myName={observerName} onLeave={onLeave} />;
  if (_ovCurG === 'tapper') return <TapperObserverView code={code} room={room} observerName={observerName} />;"""
assert OLD_OV_OVFJ in content, "ovfj observer check not found"
content = content.replace(OLD_OV_OVFJ, NEW_OV_OVFJ, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.178 ready")
