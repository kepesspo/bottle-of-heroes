#!/usr/bin/env python3
"""patch_9_157.py — ReakcióGame: Csapat → Páros párbaj, app dönti el ki veszít"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.156';" in content
content = content.replace("const APP_VERSION = 'v9.156';", "const APP_VERSION = 'v9.157';")

# ── 1. Game definition: Csapat → Páros, desc update ──
OLD_REAKCIO_DEF = "{ id:'reakcio',  roundTime:'fast', name:'Reakció Teszt',    difficulty:'könnyű',  category:'Csapat', emoji:'⚡', img:IMGS['reakcio_icon.png'], symbol:IMGS['reakcio_symbol.png'], color:'#FACC15', desc:'A képernyő piroson vár, majd véletlenszerűen zöldre vált. Mindenki megpróbál minél gyorsabban koppintani. A leglassabb játékos iszik.' },"
NEW_REAKCIO_DEF = "{ id:'reakcio',  roundTime:'fast', name:'Reakció Teszt',    difficulty:'könnyű',  category:'Páros',  emoji:'⚡', img:IMGS['reakcio_icon.png'], symbol:IMGS['reakcio_symbol.png'], color:'#FACC15', desc:'Párbaj! Mindkét játékos megnyomja a gombot amint a képernyő zöldre vált. A lassabb iszik.' },"
assert OLD_REAKCIO_DEF in content, "reakcio def not found"
content = content.replace(OLD_REAKCIO_DEF, NEW_REAKCIO_DEF, 1)

# ── 2. Render: pass challenger+opponent instead of players ──
OLD_REAKCIO_RENDER = "  if (gameId === 'reakcio')  return <ReakcioGame key={gameIdx} players={players||[]} gameIdx={gameIdx} onAdvance={onAdvance} onResult={onResult} />;"
NEW_REAKCIO_RENDER = "  if (gameId === 'reakcio')  return <ReakcioGame key={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;"
assert OLD_REAKCIO_RENDER in content, "reakcio render not found"
content = content.replace(OLD_REAKCIO_RENDER, NEW_REAKCIO_RENDER, 1)

# ── 3. Full ReakcioGame rewrite: 2-player duel ──
OLD_REAKCIO_FN = """// ── Reakció Teszt ──────────────────────────────────────────────────────────────
function ReakcioGame({ players, gameIdx, onAdvance, onResult }) {
  const [phase, setPhase] = useState('intro');
  const [currentIdx, setCurrentIdx] = useState(0);
  const [results, setResults] = useState([]);
  const [startTime, setStartTime] = useState(null);
  const [reactionMs, setReactionMs] = useState(null);
  const timerRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => () => clearTimeout(timerRef.current), []);

  const currentPlayer = players?.[currentIdx];

  const startWaiting = () => {
    setPhase('waiting');
    setReactionMs(null);
    const delay = 1500 + Math.random() * 3500;
    timerRef.current = setTimeout(() => {
      setStartTime(Date.now());
      setPhase('ready');
    }, delay);
  };

  const handleTap = () => {
    if (phase === 'waiting') {
      clearTimeout(timerRef.current);
      setPhase('intro');
      return;
    }
    if (phase !== 'ready') return;
    const ms = Date.now() - startTime;
    setReactionMs(ms);
    const newResults = [...results, { player: currentPlayer, ms }];
    setResults(newResults);
    setPhase('done');
    if (currentIdx >= (players?.length || 1) - 1) {
      const sorted = [...newResults].sort((a,b) => b.ms - a.ms);
      const loser = sorted[0];
      const dm = {};
      if (loser) dm[loser.player.id] = 2;
      if (!advancedRef.current) {
        advancedRef.current = true;
        onResult && onResult({ correct: false, playerName: loser?.player?.name||'', drinks:2, subtitle: `${loser?.player?.name} a leglassabb (${loser?.ms}ms) — iszik 2-t!` });
        onAdvance && onAdvance(dm, {});
      }
    }
  };

  const next = () => {
    setCurrentIdx(i => i+1);
    setPhase('intro');
    setReactionMs(null);
  };

  const allDone = currentIdx >= (players?.length || 1) - 1 && phase === 'done';

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      {phase === 'intro' && (
        <>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>{currentPlayer?.name} — Kész?</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>A képernyő piroson vár, majd zöldre vált. Koppints a lehető leggyorsabban!</div>
          <button onClick={startWaiting} style={{ width:'100%', padding:'16px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>
            Start!
          </button>
          {results.length > 0 && (
            <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:4 }}>
              {results.map((r, i) => <div key={i} style={{ display:'flex', justifyContent:'space-between', padding:'6px 12px', background:T.surface, borderRadius:10 }}><span style={{ fontFamily:T.font, fontSize:13, color:T.ink }}>{r.player.name}</span><span style={{ fontFamily:'monospace', fontWeight:700, fontSize:13, color:T.mint }}>{r.ms}ms</span></div>)}
            </div>
          )}
        </>
      )}
      {(phase === 'waiting' || phase === 'ready') && (
        <div onClick={handleTap}
          style={{ width:'100%', minHeight:220, borderRadius:24, background: phase==='ready' ? '#22C55E' : '#EF4444', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', cursor:'pointer', userSelect:'none', WebkitUserSelect:'none', gap:8, transition:'background .1s' }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:24, color:'#fff' }}>
            {phase === 'ready' ? '🟢 MOST! Koppints!' : '🔴 Várj...'}
          </div>
          <div style={{ fontFamily:T.font, fontSize:14, color:'rgba(255,255,255,0.8)' }}>{currentPlayer?.name}</div>
        </div>
      )}
      {phase === 'done' && (
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:12, width:'100%' }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:32, color:T.mint }}>{reactionMs}ms</div>
          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>{currentPlayer?.name} reakcióideje</div>
          {!allDone ? (
            <button onClick={next} style={{ width:'100%', padding:'14px 0', background:T.mint, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer' }}>
              Következő: {players?.[currentIdx+1]?.name} →
            </button>
          ) : (
            <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>Mindenki kész — eredmény...</div>
          )}
        </div>
      )}
    </div>
  );
}"""

NEW_REAKCIO_FN = """// ── Reakció Teszt (Párbaj) ────────────────────────────────────────────────────
function ReakcioGame({ challenger, opponent, onAdvance, onResult }) {
  // phase: 'intro1' | 'waiting1' | 'ready1' | 'done1' | 'intro2' | 'waiting2' | 'ready2' | 'result'
  const [phase, setPhase] = useState('intro1');
  const [p1Ms, setP1Ms] = useState(null);
  const [p2Ms, setP2Ms] = useState(null);
  const [startTime, setStartTime] = useState(null);
  const [earlyTap, setEarlyTap] = useState(false);
  const timerRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => () => clearTimeout(timerRef.current), []);

  const currentPlayer = phase.includes('1') ? challenger : opponent;

  const startWaiting = () => {
    setEarlyTap(false);
    const nextPhase = phase.startsWith('intro1') ? 'waiting1' : 'waiting2';
    setPhase(nextPhase);
    const delay = 1500 + Math.random() * 3500;
    timerRef.current = setTimeout(() => {
      setStartTime(Date.now());
      setPhase(nextPhase.replace('waiting', 'ready'));
    }, delay);
  };

  const handleTap = () => {
    if (phase === 'waiting1' || phase === 'waiting2') {
      clearTimeout(timerRef.current);
      setEarlyTap(true);
      setPhase(phase.startsWith('waiting1') ? 'intro1' : 'intro2');
      return;
    }
    if (phase !== 'ready1' && phase !== 'ready2') return;
    const ms = Date.now() - startTime;
    if (phase === 'ready1') {
      setP1Ms(ms);
      setPhase('done1');
    } else {
      setP2Ms(ms);
      setPhase('result');
    }
  };

  useEffect(() => {
    if (phase !== 'result' || advancedRef.current) return;
    if (p1Ms === null || p2Ms === null) return;
    advancedRef.current = true;
    const p1Name = challenger?.name || 'Kihívó';
    const p2Name = opponent?.name || 'Ellenfél';
    const p1Won = p1Ms <= p2Ms;
    const winner = p1Won ? challenger : opponent;
    const loser  = p1Won ? opponent  : challenger;
    const sub = `${p1Name}: ${p1Ms}ms — ${p2Name}: ${p2Ms}ms`;
    onResult && onResult({ correct: p1Won, playerName: loser?.name||'', drinks:1, subtitle: sub });
    onAdvance && onAdvance(
      loser  ? {[loser.id]:1}  : {},
      winner ? {[winner.id]:1} : {}
    );
  }, [phase, p1Ms, p2Ms]);

  if (phase === 'intro1' || phase === 'intro2') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:20, padding:'16px 0' }}>
      {earlyTap && <div style={{ fontFamily:T.font, fontSize:13, color:T.coral, fontWeight:700 }}>⚠️ Túl korán koppintottál! Próbáld újra.</div>}
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink, textAlign:'center' }}>
        {currentPlayer?.name || 'Játékos'} jön
      </div>
      <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center' }}>
        A képernyő piroson vár, majd zöldre vált.<br/>Koppints a lehető leggyorsabban!
      </div>
      {phase === 'done1' || p1Ms !== null ? null : null}
      <button onClick={startWaiting} style={{ padding:'16px 40px', background:T.mint, color:'#fff', border:'none', borderRadius:16, fontFamily:T.font, fontWeight:800, fontSize:18, cursor:'pointer', boxShadow:T.shadowLift }}>
        ▶ Start
      </button>
      {phase === 'intro2' && p1Ms !== null && (
        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft }}>
          {challenger?.name}: <span style={{ fontFamily:'monospace', fontWeight:700, color:T.mint }}>{p1Ms}ms</span>
        </div>
      )}
    </div>
  );

  if (phase === 'waiting1' || phase === 'waiting2' || phase === 'ready1' || phase === 'ready2') {
    const isReady = phase.startsWith('ready');
    return (
      <div onClick={handleTap}
        style={{ width:'100%', minHeight:240, borderRadius:24, background: isReady ? '#22C55E' : '#EF4444', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', cursor:'pointer', userSelect:'none', WebkitUserSelect:'none', gap:10, transition:'background .1s' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:26, color:'#fff' }}>
          {isReady ? '🟢 MOST! Koppints!' : '🔴 Várj...'}
        </div>
        <div style={{ fontFamily:T.font, fontSize:15, color:'rgba(255,255,255,0.85)' }}>{currentPlayer?.name}</div>
      </div>
    );
  }

  if (phase === 'done1') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:20, padding:'16px 0' }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:28, color:T.mint }}>
        {p1Ms}ms ✓
      </div>
      <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>{challenger?.name} reakcióideje</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, textAlign:'center', marginTop:8 }}>
        {opponent?.name || 'Ellenfél'} következik
      </div>
      <button onClick={() => setPhase('intro2')} style={{ padding:'16px 40px', background:T.mint, color:'#fff', border:'none', borderRadius:16, fontFamily:T.font, fontWeight:800, fontSize:18, cursor:'pointer', boxShadow:T.shadowLift }}>
        ▶ Tovább
      </button>
    </div>
  );

  // result
  const p1Won = p1Ms !== null && p2Ms !== null && p1Ms <= p2Ms;
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'16px 0' }}>
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'20px 16px', boxShadow:T.shadow }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.ink }}>{challenger?.name || 'Kihívó'}</div>
          <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:20, color: p1Won ? T.mint : T.coral }}>{p1Ms}ms</div>
        </div>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.ink }}>{opponent?.name || 'Ellenfél'}</div>
          <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:20, color: !p1Won ? T.mint : T.coral }}>{p2Ms}ms</div>
        </div>
      </div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.mint, textAlign:'center' }}>
        🏆 {p1Won ? (challenger?.name||'Kihívó') : (opponent?.name||'Ellenfél')} nyert!
      </div>
    </div>
  );
}"""

assert OLD_REAKCIO_FN in content, "ReakcioGame not found"
content = content.replace(OLD_REAKCIO_FN, NEW_REAKCIO_FN, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.157 ready")
