import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Replace TapperGame ─────────────────────────────────────────────────────

NEW_TAPPER = r"""function TapperGame({ gameIdx, challenger, opponent }) {
  const p1 = challenger;
  const p2 = opponent;

  const [phase, setPhase] = React.useState('idle');
  const [p1Hold, setP1Hold] = React.useState(false);
  const [p2Hold, setP2Hold] = React.useState(false);
  const [countdown, setCountdown] = React.useState(5.0);
  const [p1Time, setP1Time] = React.useState(null);
  const [p2Time, setP2Time] = React.useState(null);

  const phaseRef = React.useRef('idle');
  const p1HoldRef = React.useRef(false);
  const p2HoldRef = React.useRef(false);
  const p1TimeRef = React.useRef(null);
  const p2TimeRef = React.useRef(null);
  const startRef = React.useRef(null);
  const ivRef = React.useRef(null);

  React.useEffect(() => {
    setPhase('idle'); setP1Hold(false); setP2Hold(false);
    setCountdown(5.0); setP1Time(null); setP2Time(null);
    phaseRef.current = 'idle';
    p1HoldRef.current = false; p2HoldRef.current = false;
    p1TimeRef.current = null; p2TimeRef.current = null;
    clearInterval(ivRef.current);
    return () => clearInterval(ivRef.current);
  }, [gameIdx]);

  const tryStart = () => {
    if (!p1HoldRef.current || !p2HoldRef.current || phaseRef.current !== 'idle') return;
    phaseRef.current = 'counting'; setPhase('counting');
    p1TimeRef.current = null; p2TimeRef.current = null;
    setP1Time(null); setP2Time(null);
    startRef.current = Date.now() + 5000;
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (startRef.current - Date.now()) / 1000);
      setCountdown(parseFloat(rem.toFixed(2)));
      if (rem <= 0) {
        clearInterval(ivRef.current);
        if (p1TimeRef.current === null) { p1TimeRef.current = -1; setP1Time(-1); }
        if (p2TimeRef.current === null) { p2TimeRef.current = -1; setP2Time(-1); }
        phaseRef.current = 'done'; setPhase('done');
      }
    }, 40);
  };

  const pressDown = (pNum) => {
    if (phaseRef.current !== 'idle') return;
    if (pNum === 1) { p1HoldRef.current = true; setP1Hold(true); }
    else { p2HoldRef.current = true; setP2Hold(true); }
    tryStart();
  };

  const pressUp = (pNum) => {
    if (pNum === 1) { p1HoldRef.current = false; setP1Hold(false); }
    else { p2HoldRef.current = false; setP2Hold(false); }
    if (phaseRef.current === 'counting') {
      const rem = startRef.current - Date.now();
      if (pNum === 1 && p1TimeRef.current === null) {
        const t = rem <= 0 ? -1 : rem / 1000;
        p1TimeRef.current = t; setP1Time(t);
      }
      if (pNum === 2 && p2TimeRef.current === null) {
        const t = rem <= 0 ? -1 : rem / 1000;
        p2TimeRef.current = t; setP2Time(t);
      }
      if (p1TimeRef.current !== null && p2TimeRef.current !== null) {
        clearInterval(ivRef.current);
        phaseRef.current = 'done'; setPhase('done');
      }
    }
  };

  // -1 = past 0 (lose), positive = seconds remaining (smaller = better)
  const getResult = () => {
    if (p1Time === null || p2Time === null) return null;
    const p1Past = p1Time === -1, p2Past = p2Time === -1;
    if (p1Past && p2Past) return 'both-lose';
    if (p1Past) return 2;
    if (p2Past) return 1;
    if (p1Time < p2Time) return 1;
    if (p2Time < p1Time) return 2;
    return 'draw';
  };
  const result = phase === 'done' ? getResult() : null;
  const timerColor = countdown < 1 ? '#F4704A' : countdown < 2.5 ? '#F0C840' : '#50C882';

  if (!p2) return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:10, padding:'20px 0' }}>
      <div style={{ fontSize:36 }}>👇</div>
      <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center' }}>Válassz ellenfelet alább!</div>
    </div>
  );

  const Btn = ({ pNum, player, holding, timeVal }) => {
    const released = timeVal !== null;
    return (
      <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:6 }}>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:10, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>
          {pNum === 1 ? 'KIHÍVÓ' : 'ELLENFÉL'}
        </div>
        <div
          onPointerDown={e => { e.preventDefault(); e.currentTarget.setPointerCapture(e.pointerId); pressDown(pNum); }}
          onPointerUp={() => pressUp(pNum)}
          onPointerCancel={() => pressUp(pNum)}
          style={{
            width:104, height:104, borderRadius:'50%',
            background: released ? `${player.color}66` : player.color,
            boxShadow: holding && !released
              ? `0 0 0 10px ${player.color}44, 0 0 0 20px ${player.color}18`
              : `0 0 0 10px rgba(255,255,255,0.85)`,
            display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2,
            cursor:'pointer', userSelect:'none', WebkitUserSelect:'none', touchAction:'none',
            transition:'box-shadow 0.15s, background 0.15s',
            transform: holding && !released ? 'scale(0.96)' : 'scale(1)',
          }}
        >
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:32, color:'#fff', lineHeight:1 }}>
            {player.name.charAt(0).toUpperCase()}
          </div>
          {!released && (
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:10, color:'rgba(255,255,255,0.85)', letterSpacing:'0.04em' }}>
              {phase === 'idle' ? 'TARTSD' : 'TARTSD!'}
            </div>
          )}
          {released && (
            <div style={{ fontFamily:'monospace', fontWeight:700, fontSize:11, color:'rgba(255,255,255,0.9)' }}>
              {timeVal === -1 ? '✗ KÉSŐ' : `${(timeVal * 1000).toFixed(0)}ms`}
            </div>
          )}
        </div>
        <div style={{ fontFamily:T.font, fontWeight:600, fontSize:13, color:T.ink }}>{player.name}</div>
      </div>
    );
  };

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14 }}>

      <Btn pNum={2} player={p2} holding={p2Hold} timeVal={p2Time} />

      {/* VS / timer bubble */}
      <div style={{ width:56, height:56, borderRadius:'50%', background:T.surface, boxShadow:T.shadow, display:'flex', alignItems:'center', justifyContent:'center' }}>
        {phase === 'counting'
          ? <span style={{ fontFamily:'monospace', fontWeight:900, fontSize:22, color:timerColor, lineHeight:1 }}>{Math.ceil(countdown)}</span>
          : <span style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft }}>VS</span>
        }
      </div>

      <Btn pNum={1} player={p1} holding={p1Hold} timeVal={p1Time} />

      {phase === 'idle' && !p1Hold && !p2Hold && (
        <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, textAlign:'center', maxWidth:240, lineHeight:1.5 }}>
          Mindketten rakjátok az ujjatokat a gombra — automatikusan elindul!
        </div>
      )}
      {phase === 'idle' && (p1Hold !== p2Hold) && (
        <div style={{ fontFamily:T.font, fontSize:12, color:'#E0A030', textAlign:'center' }}>
          Várakozás a másik játékosra…
        </div>
      )}

      {phase === 'done' && result !== null && (
        <div style={{ padding:'12px 22px', borderRadius:14, animation:'popIn .3s', textAlign:'center',
          background: result==='both-lose' ? `${T.coral}18` : result==='draw' ? `${T.yellow}18` : result===1 ? `${p1.color}18` : `${p2.color}18`,
          border: `2px solid ${result==='both-lose' ? T.coral : result==='draw' ? T.yellow : result===1 ? p1.color : p2.color}` }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>
            {result === 'both-lose' ? '💀 Mindkettő túlment — mindkettő iszik!'
              : result === 'draw' ? '🤝 Döntetlen!'
              : result === 1 ? `🏆 ${p1.name} nyert! ${p2.name} iszik.`
              : `🏆 ${p2.name} nyert! ${p1.name} iszik.`}
          </div>
          {result !== 'both-lose' && p1Time !== null && p2Time !== null && p1Time !== -1 && p2Time !== -1 && (
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:4 }}>
              {p1.name}: {(p1Time*1000).toFixed(0)}ms · {p2.name}: {(p2Time*1000).toFixed(0)}ms
            </div>
          )}
        </div>
      )}
    </div>
  );
}"""

html = re.sub(
    r'function TapperGame\(\{ gameIdx \}\) \{.*?\n\}(?=\n\nfunction AnagrammaGame)',
    NEW_TAPPER, html, flags=re.DOTALL
)

# ── 2. Update GameContent to pass challenger + opponent to TapperGame ──────────
html = html.replace(
    "  if (gameId === 'tapper') return <TapperGame key={gameIdx} gameIdx={gameIdx} />;",
    "  if (gameId === 'tapper') return <TapperGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} />;",
    1
)

html = html.replace(
    "function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta }) {",
    "function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta, challenger, opponent }) {",
    1
)

# ── 3. Pass challenger + opponent from PlayScreen into GameContent ─────────────
html = html.replace(
    "<GameContent key={currentGameId + gameIdx} gameId={currentGameId} gameIdx={gameIdx} players={players} onAdvance={advanceLoverseny} roomCode={roomCode} mode={mode} gameMeta={gameMeta} />",
    "<GameContent key={currentGameId + gameIdx} gameId={currentGameId} gameIdx={gameIdx} players={players} onAdvance={advanceLoverseny} roomCode={roomCode} mode={mode} gameMeta={gameMeta} challenger={currentPlayer} opponent={selectedOpponent} />",
    1
)

# ── 4. Version bump ────────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.19 · DNR · 2026.05.31 00:00',
    'Verzió 5.20 · DNR · 2026.05.31 01:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
