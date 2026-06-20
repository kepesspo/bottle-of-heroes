#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. commitRound: selectedGames + roundEvent sync hozzáadása
old_commitround_sync = "    if (roomCode && typeof syncRoom==='function')\n      syncRoom(roomCode, { players:newPlayers, turn:newTurn, gameIdx:newGameIdx, round:newRound });"
new_commitround_sync = """    if (roomCode && typeof syncRoom==='function') {
      const roundEventData = (newRound > round) ? { round: newRound, ts: Date.now() } : null;
      syncRoom(roomCode, {
        players: newPlayers, turn: newTurn, gameIdx: newGameIdx, round: newRound,
        selectedGames,
        ...(roundEventData ? { roundEvent: roundEventData } : {}),
      });
    }"""
assert old_commitround_sync in html, "FAIL: commitRound sync"
html = html.replace(old_commitround_sync, new_commitround_sync, 1)

# ── 2. PlayScreen mount: selectedGames kezdeti sync (ha van roomCode)
old_playscreen_states = """  const [feedback, setFeedback] = useState(null);
  const [transitioning, setTransitioning] = useState(false);"""
new_playscreen_states = """  const [feedback, setFeedback] = useState(null);
  const [transitioning, setTransitioning] = useState(false);"""
# Actually let's add it in a useEffect after the state declarations
old_first_useeffect = """  React.useEffect(() => {
    const showCounter = gameMeta?.showRoundCounter !== false;
    if (showCounter) {
      setRoundPopup({ round: 1, wildcard: null, showRound: true, leaving: false });"""
new_first_useeffect = """  // Sync selectedGames on mount so observers know which games are selected
  React.useEffect(() => {
    if (roomCode && typeof syncRoom === 'function') {
      syncRoom(roomCode, { selectedGames, players, turn: 0, gameIdx: 0, round: 1 });
    }
  }, []);

  React.useEffect(() => {
    const showCounter = gameMeta?.showRoundCounter !== false;
    if (showCounter) {
      setRoundPopup({ round: 1, wildcard: null, showRound: true, leaving: false });"""
assert old_first_useeffect in html, "FAIL: first useEffect"
html = html.replace(old_first_useeffect, new_first_useeffect, 1)

# ── 3. onResult: gameEvent sync ha van roomCode
old_onresult = """  const onResult = (res) => {
    if (!res) { setGameResult(null); return; }
    const d = res.drinks ?? 0;
    const scaled = d > 0 ? d * diffDrinks : 0;
    // If subtitle hardcodes "egyet" or a drink count, drop it so ResultBanner auto-generates correctly
    const subtitle = (d === 1 && diffDrinks > 1) ? null : res.subtitle;
    setGameResult({ ...res, drinks: scaled, subtitle, ts: Date.now() });
  };"""
new_onresult = """  const onResult = (res) => {
    if (!res) { setGameResult(null); return; }
    const d = res.drinks ?? 0;
    const scaled = d > 0 ? d * diffDrinks : 0;
    const subtitle = (d === 1 && diffDrinks > 1) ? null : res.subtitle;
    const ts = Date.now();
    setGameResult({ ...res, drinks: scaled, subtitle, ts });
    if (roomCode && typeof syncRoom === 'function') {
      syncRoom(roomCode, { gameEvent: { correct: !!res.correct, playerName: res.playerName || null, drinks: scaled, subtitle: subtitle || null, ts } });
    }
  };"""
assert old_onresult in html, "FAIL: onResult"
html = html.replace(old_onresult, new_onresult, 1)

# ── 4. ObserverWatching: roundEvent + gameEvent detektálás + state
old_observer_states = """  const prevGameIdxRef = React.useRef(null);
  React.useEffect(() => {
    const idx = room?.gameIdx ?? null;
    if (prevGameIdxRef.current !== null && prevGameIdxRef.current !== idx) {
      setGroupUsed(false); setKortyUsed(false);
    }
    prevGameIdxRef.current = idx;
  }, [room?.gameIdx]);"""
new_observer_states = """  const [obsRoundPopup, setObsRoundPopup] = React.useState(null);
  const [obsGameEvent, setObsGameEvent] = React.useState(null);
  const prevGameIdxRef = React.useRef(null);
  React.useEffect(() => {
    const idx = room?.gameIdx ?? null;
    if (prevGameIdxRef.current !== null && prevGameIdxRef.current !== idx) {
      setGroupUsed(false); setKortyUsed(false);
    }
    prevGameIdxRef.current = idx;
  }, [room?.gameIdx]);"""
assert old_observer_states in html, "FAIL: observer states"
html = html.replace(old_observer_states, new_observer_states, 1)

# ── 5. ObserverWatching subscribeRoom: roundEvent + gameEvent kezelése
old_obs_bpnotif = """          // Beer pong match notification
          if (data.bpNotif && (!prev?.bpNotif || data.bpNotif.ts !== prev.bpNotif.ts)) {"""
new_obs_bpnotif = """          // Round popup event
          if (data.roundEvent && (!prev?.roundEvent || data.roundEvent.ts !== prev.roundEvent.ts)) {
            setObsRoundPopup({ round: data.roundEvent.round, leaving: false });
            setTimeout(() => setObsRoundPopup(p => p ? {...p, leaving:true} : p), 1500);
            setTimeout(() => setObsRoundPopup(null), 2000);
          }
          // Game result event
          if (data.gameEvent && (!prev?.gameEvent || data.gameEvent.ts !== prev.gameEvent.ts)) {
            setObsGameEvent(data.gameEvent);
            setTimeout(() => setObsGameEvent(null), 3500);
          }
          // Beer pong match notification
          if (data.bpNotif && (!prev?.bpNotif || data.bpNotif.ts !== prev.bpNotif.ts)) {"""
assert old_obs_bpnotif in html, "FAIL: observer bpNotif"
html = html.replace(old_obs_bpnotif, new_obs_bpnotif, 1)

# ── 6. ObserverWatching JSX: round popup + game event banner megjelenítése
old_obs_return = """  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', position:'relative', overflow:'hidden' }}>
      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch' }}>
      <div style={{ padding:'12px 18px 12px',"""
new_obs_return = """  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', position:'relative', overflow:'hidden' }}>
      {/* Round popup overlay */}
      {obsRoundPopup && (
        <div style={{ position:'fixed', inset:0, zIndex:9998, pointerEvents:'none', display:'flex', alignItems:'center', justifyContent:'center' }}>
          <div style={{ animation: obsRoundPopup.leaving ? 'roundPopOut 0.5s ease-in forwards' : 'roundPopIn 0.5s cubic-bezier(.2,.9,.3,1.2) forwards', background:T.surface, borderRadius:24, padding:'24px 40px', boxShadow:'0 8px 40px rgba(0,0,0,0.25)', textAlign:'center' }}>
            <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, letterSpacing:'0.12em', textTransform:'uppercase', marginBottom:4 }}>📡 Körváltás</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:48, color:T.ink, lineHeight:1 }}>{obsRoundPopup.round}.</div>
            <div style={{ fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft, marginTop:4 }}>Kör</div>
          </div>
        </div>
      )}
      {/* Game event banner */}
      {obsGameEvent && (
        <div style={{ position:'fixed', top:16, left:16, right:16, zIndex:9999, animation:'slideDown .3s cubic-bezier(.2,.9,.3,1)' }}>
          <div style={{ borderRadius:16, padding:'12px 16px', display:'flex', alignItems:'center', gap:12, background: obsGameEvent.correct ? 'rgba(80,168,130,0.95)' : 'rgba(220,80,80,0.95)', boxShadow:'0 4px 20px rgba(0,0,0,0.3)' }}>
            <div style={{ fontSize:28 }}>{obsGameEvent.correct ? '🎉' : '🍺'}</div>
            <div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:'#fff' }}>{obsGameEvent.correct ? 'Helyes! +1 pont' : 'Inni kell!'}</div>
              {obsGameEvent.playerName && <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.85)', marginTop:2 }}>{obsGameEvent.playerName}{!obsGameEvent.correct && obsGameEvent.drinks > 0 ? ` — ${obsGameEvent.drinks} korty` : ''}</div>}
            </div>
          </div>
        </div>
      )}
      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch' }}>
      <div style={{ padding:'12px 18px 12px',"""
assert old_obs_return in html, "FAIL: observer return"
html = html.replace(old_obs_return, new_obs_return, 1)

html = html.replace("const APP_VERSION = 'v9.314';", "const APP_VERSION = 'v9.315';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.315 — Observer sync: selectedGames, roundEvent popup, gameEvent banner")
