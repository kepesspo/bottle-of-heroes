#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. BottleApp: add scoreHistory state
old = """  const [lastGameRound, setLastGameRound] = React.useState(1);"""
new = """  const [lastGameRound, setLastGameRound] = React.useState(1);
  const [scoreHistory, setScoreHistory] = React.useState([]);"""
assert old in html, "FAIL: lastGameRound state"
html = html.replace(old, new, 1)

# ── 2. resetGame: clear scoreHistory
old2 = """  const resetGame = () => { setPlayers(players.map(p => ({...p,drinks:0,points:0}))); setScreen('play'); };"""
new2 = """  const resetGame = () => { setPlayers(players.map(p => ({...p,drinks:0,points:0}))); setScoreHistory([]); setScreen('play'); };"""
assert old2 in html, "FAIL: resetGame"
html = html.replace(old2, new2, 1)

# ── 3. Pass setScoreHistory to PlayScreen
old3 = """        {screen==='play'     && <PlayScreen     go={go} players={players} setPlayers={setPlayers} selectedGames={selectedGames} roomCode={roomCode} gameMeta={gameMeta} setGameMeta={setGameMeta} setLastGameRound={setLastGameRound} />}"""
new3 = """        {screen==='play'     && <PlayScreen     go={go} players={players} setPlayers={setPlayers} selectedGames={selectedGames} roomCode={roomCode} gameMeta={gameMeta} setGameMeta={setGameMeta} setLastGameRound={setLastGameRound} setScoreHistory={setScoreHistory} />}"""
assert old3 in html, "FAIL: PlayScreen props"
html = html.replace(old3, new3, 1)

# ── 4. Pass scoreHistory to EndScreen
old4 = """        {screen==='end'      && <EndScreen      go={go} players={players} resetGame={resetGame} lastRound={lastGameRound} />}"""
new4 = """        {screen==='end'      && <EndScreen      go={go} players={players} resetGame={resetGame} lastRound={lastGameRound} scoreHistory={scoreHistory} />}"""
assert old4 in html, "FAIL: EndScreen props"
html = html.replace(old4, new4, 1)

# ── 5. PlayScreen: accept setScoreHistory prop
old5 = """function PlayScreen({ players, setPlayers, selectedGames, go, roomCode, gameMeta, setGameMeta, setLastGameRound }) {"""
new5 = """function PlayScreen({ players, setPlayers, selectedGames, go, roomCode, gameMeta, setGameMeta, setLastGameRound, setScoreHistory }) {"""
assert old5 in html, "FAIL: PlayScreen signature"
html = html.replace(old5, new5, 1)

# ── 6. commitRound: snapshot scores
old6 = """    setPlayers(newPlayers);
    try { localStorage.setItem('boh_session', JSON.stringify({ players: newPlayers, turn: newTurn, gameIdx: newGameIdx, round: newRound, selectedGames, gameMeta })); } catch(e) {}"""
new6 = """    setPlayers(newPlayers);
    if (setScoreHistory) setScoreHistory(prev => [...prev, newPlayers.map(p => ({ id: p.id, name: p.name, color: p.color, pts: p.points }))]);
    try { localStorage.setItem('boh_session', JSON.stringify({ players: newPlayers, turn: newTurn, gameIdx: newGameIdx, round: newRound, selectedGames, gameMeta })); } catch(e) {}"""
assert old6 in html, "FAIL: commitRound setPlayers"
html = html.replace(old6, new6, 1)

# ── 7. EndScreen: accept scoreHistory + add chart before leaderboard
old7 = """function EndScreen({ players, go, resetGame, lastRound }) {"""
new7 = """function EndScreen({ players, go, resetGame, lastRound, scoreHistory }) {"""
assert old7 in html, "FAIL: EndScreen signature"
html = html.replace(old7, new7, 1)

# ── 8. EndScreen: insert chart before Full leaderboard
old8 = """        {/* Full leaderboard */}
        <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
          {sorted.map((p,i) => <LeaderRow key={p.id} p={p} rank={i+1} maxScore={maxScore} />)}
        </div>"""
new8 = """        {/* Pont grafikon */}
        {scoreHistory && scoreHistory.length > 2 && (() => {
          const W = 320, H = 140, PAD = 28;
          const steps = scoreHistory.length;
          const allPts = scoreHistory.flatMap(snap => snap.map(p => p.pts));
          const minPt = Math.min(0, ...allPts);
          const maxPt = Math.max(1, ...allPts);
          const px = i => PAD + (i / (steps - 1)) * (W - PAD * 2);
          const py = v => H - PAD - ((v - minPt) / (maxPt - minPt)) * (H - PAD * 2);
          const playerIds = scoreHistory[0].map(p => p.id);
          return (
            <div style={{ background:T.surface, borderRadius:16, padding:'14px 12px 10px', boxShadow:T.shadow }}>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:8 }}>📈 Pontok alakulása</div>
              <svg viewBox={`0 0 ${W} ${H}`} style={{ width:'100%', height:'auto', overflow:'visible' }}>
                {/* Y gridlines */}
                {[0,0.5,1].map(f => {
                  const yv = minPt + f * (maxPt - minPt);
                  const y = py(yv);
                  return <g key={f}>
                    <line x1={PAD} x2={W-PAD} y1={y} y2={y} stroke={T.bgSoft} strokeWidth="1" />
                    <text x={PAD-4} y={y+4} textAnchor="end" fontSize="9" fill={T.inkMute} fontFamily={T.font}>{Math.round(yv)}</text>
                  </g>;
                })}
                {/* Player lines */}
                {playerIds.map(pid => {
                  const info = scoreHistory[0].find(p => p.id === pid);
                  if (!info) return null;
                  const pts = scoreHistory.map(snap => (snap.find(p => p.id === pid) || {pts:0}).pts);
                  const d = pts.map((v,i) => `${i===0?'M':'L'}${px(i).toFixed(1)},${py(v).toFixed(1)}`).join(' ');
                  const lastX = px(steps-1), lastY = py(pts[steps-1]);
                  return <g key={pid}>
                    <path d={d} fill="none" stroke={info.color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                    <circle cx={lastX} cy={lastY} r="4" fill={info.color} />
                  </g>;
                })}
              </svg>
              {/* Legend */}
              <div style={{ display:'flex', flexWrap:'wrap', gap:'6px 12px', marginTop:6 }}>
                {scoreHistory[0].map(p => (
                  <div key={p.id} style={{ display:'flex', alignItems:'center', gap:5 }}>
                    <div style={{ width:10, height:10, borderRadius:'50%', background:p.color, flexShrink:0 }} />
                    <span style={{ fontFamily:T.font, fontSize:11, color:T.ink, fontWeight:700 }}>{p.name}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })()}

        {/* Full leaderboard */}
        <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
          {sorted.map((p,i) => <LeaderRow key={p.id} p={p} rank={i+1} maxScore={maxScore} />)}
        </div>"""
assert old8 in html, "FAIL: leaderboard"
html = html.replace(old8, new8, 1)

# ── 9. StatsScreen profilRows: add gold/silver/bronze badge on avatar
old9 = """                      <div style={{ width:40, height:40, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff', flexShrink:0, overflow:'hidden' }}>
                        {p.img ? <img src={p.img} style={{ width:40, height:40, objectFit:'cover' }} /> : p.name.charAt(0).toUpperCase()}
                      </div>"""
new9 = """                      <div style={{ position:'relative', flexShrink:0 }}>
                        <div style={{ width:40, height:40, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff', overflow:'hidden' }}>
                          {p.img ? <img src={p.img} style={{ width:40, height:40, objectFit:'cover' }} /> : p.name.charAt(0).toUpperCase()}
                        </div>
                        {i < 3 && <div style={{ position:'absolute', bottom:-3, right:-4, fontSize:13, lineHeight:1 }}>{['🥇','🥈','🥉'][i]}</div>}
                      </div>"""
assert old9 in html, "FAIL: profil avatar badge"
html = html.replace(old9, new9, 1)

# ── 10. Offline banner — add to BottleApp render
old10 = """  return (
    <div style={{ minHeight:'100dvh', width:'100%', position:'relative', fontFamily:T.font, color:T.ink, WebkitFontSmoothing:'antialiased', background:T.bg }} data-theme={appTheme}>
      <BubbleBackground />
      <div key={screen} style={{ height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}>"""
new10 = """  const [isOnline, setIsOnline] = React.useState(navigator.onLine);
  React.useEffect(() => {
    const on = () => setIsOnline(true);
    const off = () => setIsOnline(false);
    window.addEventListener('online', on);
    window.addEventListener('offline', off);
    return () => { window.removeEventListener('online', on); window.removeEventListener('offline', off); };
  }, []);
  return (
    <div style={{ minHeight:'100dvh', width:'100%', position:'relative', fontFamily:T.font, color:T.ink, WebkitFontSmoothing:'antialiased', background:T.bg }} data-theme={appTheme}>
      {!isOnline && (
        <div style={{ position:'fixed', top:0, left:0, right:0, background:'#EF4444', color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:12, textAlign:'center', padding:'6px 16px', letterSpacing:'0.04em', zIndex:9999 }}>
          📡 Nincs internetkapcsolat — multiplayer nem elérhető
        </div>
      )}
      <BubbleBackground />
      <div key={screen} style={{ height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}>"""
assert old10 in html, "FAIL: BottleApp return"
html = html.replace(old10, new10, 1)

html = html.replace("const APP_VERSION = 'v9.291';", "const APP_VERSION = 'v9.292';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.292 — pontgrafikon EndScreen, profil badge, offline banner")
