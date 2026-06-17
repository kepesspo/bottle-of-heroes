#!/usr/bin/env python3
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Version bump ───────────────────────────────────────────────────────────
assert "v9.95'" in content, "Version mismatch"
content = content.replace("const APP_VERSION = 'v9.95';", "const APP_VERSION = 'v9.96';", 1)

# ── 2. GameContent wiring ─────────────────────────────────────────────────────
ANCHOR = "  if (gameId === 'beerpong') return <BeerPongGame"
assert ANCHOR in content, f"Anchor not found: {ANCHOR}"

NEW_WIRING = """  if (gameId === 'ritmus')   return <RitmusGame key={gameIdx} gameIdx={gameIdx} players={players} challenger={challenger} opponent={selectedOpponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'mitval')   return <MitValasztanalGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'meduza')   return <MeduzaGame key={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'farkasos') return <FarkasosGame key={gameIdx} players={players||[]} gameIdx={gameIdx} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'mutasd')   return <MutasdGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'emojikv')  return <EmojiKvizGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'tabu')     return <TabuGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'matek')    return <MatekGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'reakcio')  return <ReakcioGame key={gameIdx} players={players||[]} gameIdx={gameIdx} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'szamsor')  return <SzamsorGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'beerpong') return <BeerPongGame"""

content = content.replace(ANCHOR, NEW_WIRING, 1)

# ── 3. Game components ────────────────────────────────────────────────────────
COMP_ANCHOR = "function BeerPongObserverView({ room, code, onLeave }) {"
assert COMP_ANCHOR in content, f"Component anchor not found"

COMPONENTS = r"""// ── Ritmus Játék ─────────────────────────────────────────────────────────────
function RitmusGame({ gameIdx, players, challenger, opponent, onAdvance, onResult }) {
  const GRID = 12;
  const DURATION = 30;
  const [phase, setPhase] = useState('intro');
  const [timeLeft, setTimeLeft] = useState(DURATION);
  const [activeBtn, setActiveBtn] = useState(null);
  const [score1, setScore1] = useState(0);
  const [score2, setScore2] = useState(0);
  const [currentScore, setCurrentScore] = useState(0);
  const [tapped, setTapped] = useState(false);
  const ivRef = useRef(null);
  const btnTimerRef = useRef(null);
  const advancedRef = useRef(false);
  const scoreRef = useRef(0);
  const endTimeRef = useRef(0);

  const p1 = challenger;
  const p2 = opponent || (players && players.find(p => p && p.id !== challenger?.id)) || null;

  useEffect(() => () => { clearInterval(ivRef.current); clearTimeout(btnTimerRef.current); }, []);

  const startRound = (isP2) => {
    scoreRef.current = 0;
    setCurrentScore(0);
    setActiveBtn(null);
    setTapped(false);
    setTimeLeft(DURATION);
    setPhase(isP2 ? 'p2playing' : 'p1playing');
    endTimeRef.current = Date.now() + DURATION * 1000;
    clearInterval(ivRef.current);
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (endTimeRef.current - Date.now()) / 1000);
      setTimeLeft(Math.ceil(rem));
      if (rem <= 0) {
        clearInterval(ivRef.current);
        clearTimeout(btnTimerRef.current);
        setActiveBtn(null);
        if (!isP2) { setScore1(scoreRef.current); setPhase('p1done'); }
        else { setScore2(scoreRef.current); setPhase('done'); }
      }
    }, 100);
    const spawnLoop = () => {
      if (Date.now() >= endTimeRef.current) return;
      const pos = Math.floor(Math.random() * GRID);
      setActiveBtn(pos);
      setTapped(false);
      clearTimeout(btnTimerRef.current);
      btnTimerRef.current = setTimeout(() => {
        setActiveBtn(null);
        btnTimerRef.current = setTimeout(spawnLoop, 300 + Math.random() * 400);
      }, 700 + Math.random() * 400);
    };
    setTimeout(spawnLoop, 600);
  };

  useEffect(() => {
    if (phase === 'done' && !advancedRef.current) {
      advancedRef.current = true;
      const s1 = score1, s2 = score2;
      const diff = Math.abs(s1 - s2);
      const loser = s1 < s2 ? p1 : s2 < s1 ? p2 : null;
      const drinks = Math.max(1, diff);
      const dm = {};
      if (loser) dm[loser.id] = drinks;
      else { players?.forEach(p => { if (p) dm[p.id] = 1; }); }
      const subtitle = loser ? `${loser.name} iszik ${drinks} kortyt (${s1} vs ${s2})` : `Döntetlen! (${s1} vs ${s2}) — mindenki iszik 1-et`;
      onResult && onResult({ correct: !loser, playerName: loser?.name || '', drinks, subtitle });
      onAdvance && onAdvance(dm, {});
    }
  }, [phase]);

  const handleTap = (pos) => {
    if (activeBtn !== pos || tapped) return;
    setTapped(true);
    setActiveBtn(null);
    scoreRef.current += 1;
    setCurrentScore(scoreRef.current);
  };

  if (phase === 'intro') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'8px 0' }}>
      <div style={{ fontSize:52 }}>🥁</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, textAlign:'center' }}>Ritmus Játék</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.6 }}>
        Gombok villannak fel — koppints rájuk mielőtt eltűnnek!<br/>
        <strong style={{color:T.ink}}>{p1?.name}</strong> játszik először (30mp), majd <strong style={{color:T.ink}}>{p2?.name || '?'}</strong>.<br/>
        A kevesebb találatú játékos annyit iszik amennyi a különbség.
      </div>
      <button onClick={() => startRound(false)} style={{ width:'100%', padding:'16px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>
        {p1?.name} — Start!
      </button>
    </div>
  );

  if (phase === 'p1playing' || phase === 'p2playing') {
    const isP2 = phase === 'p2playing';
    const currentPlayer = isP2 ? p2 : p1;
    return (
      <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:12 }}>
        <div style={{ display:'flex', justifyContent:'space-between', width:'100%', alignItems:'center' }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{currentPlayer?.name}</div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color: timeLeft <= 5 ? T.coral : T.mint }}>{timeLeft}s</div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>✅ {currentScore}</div>
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:10, width:'100%' }}>
          {Array.from({length:GRID}).map((_, i) => {
            const isActive = activeBtn === i;
            return (
              <div key={i} onClick={() => handleTap(i)}
                style={{ height:72, borderRadius:16, background: isActive ? T.mint : T.surfaceMuted, border: isActive ? `3px solid ${T.mint}` : '3px solid transparent', display:'grid', placeItems:'center', cursor:'pointer', transition:'background .08s', boxShadow: isActive ? `0 0 18px ${T.mint}88` : 'none', animation: isActive ? 'popIn .15s' : 'none', WebkitTapHighlightColor:'transparent', userSelect:'none' }}>
                {isActive && <span style={{ fontSize:28 }}>🎯</span>}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (phase === 'p1done') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontSize:48 }}>🎯</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink }}>{p1?.name}: {score1} találat</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>Most {p2?.name} jön!</div>
      <button onClick={() => startRound(true)} style={{ width:'100%', padding:'16px 0', background:T.coral, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>
        {p2?.name} — Start!
      </button>
    </div>
  );

  return null;
}

// ── Mit Választanál ───────────────────────────────────────────────────────────
function MitValasztanalGame({ gameIdx, challenger, onAdvance, onResult }) {
  const q = MIT_VALASZTANAL_SHUFFLED[gameIdx % MIT_VALASZTANAL_SHUFFLED.length];
  const [choice, setChoice] = useState(null);
  const [revealed, setRevealed] = useState(false);
  const [timeLeft, setTimeLeft] = useState(5);
  const [timedOut, setTimedOut] = useState(false);
  const [started, setStarted] = useState(false);
  const ivRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => () => clearInterval(ivRef.current), []);

  const startTimer = () => {
    if (started) return;
    setStarted(true);
    const end = Date.now() + 5000;
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      setTimeLeft(Math.ceil(rem));
      if (rem <= 0) { clearInterval(ivRef.current); setTimedOut(true); }
    }, 100);
  };

  const handleChoose = (side) => {
    if (timedOut || revealed) return;
    clearInterval(ivRef.current);
    setChoice(side);
    setRevealed(true);
  };

  const handleResult = (won) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    if (won) {
      onResult && onResult({ correct: true, playerName: challenger?.name||'', drinks:0, subtitle: (challenger?.name||'') + ' nyert — +1 pont!' });
      onAdvance && onAdvance({}, challenger ? {[challenger.id]:1} : {});
    } else {
      onResult && onResult({ correct: false, playerName: challenger?.name||'', drinks:1, subtitle: (challenger?.name||'') + ' iszik 1-et!' });
      onAdvance && onAdvance(challenger ? {[challenger.id]:1} : {}, {});
    }
  };

  const majorityA = q.statsA >= 50;
  const won = choice ? (choice === 'a' ? majorityA : !majorityA) : false;

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:12, width:'100%' }}>
      <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:13, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.08em' }}>Mit Választanál?</div>
      {started && !revealed && !timedOut && (
        <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:28, color: timeLeft <= 2 ? T.coral : T.mint }}>{timeLeft}s</div>
      )}
      {timedOut && !revealed && (
        <div style={{ background:`${T.coral}18`, borderRadius:16, padding:'14px 18px', textAlign:'center' }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.coral }}>⏰ Lejárt az idő!</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:4 }}>{challenger?.name} nem döntött — iszik!</div>
          <button onClick={() => handleResult(false)} style={{ marginTop:12, width:'100%', padding:'14px 0', background:T.coral, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer' }}>Tovább</button>
        </div>
      )}
      {!timedOut && (
        <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
          {['a','b'].map(side => {
            const text = side === 'a' ? q.a : q.b;
            const stat = side === 'a' ? q.statsA : 100 - q.statsA;
            const isChosen = choice === side;
            const isMajority = side === 'a' ? majorityA : !majorityA;
            let bg = T.surface, border = `1.5px solid rgba(20,30,50,0.08)`, textColor = T.ink;
            if (revealed) {
              if (isChosen && isMajority) { bg = `${T.mint}22`; border = `2px solid ${T.mint}`; textColor = T.mint; }
              else if (isChosen && !isMajority) { bg = `${T.coral}18`; border = `2px solid ${T.coral}`; textColor = T.coral; }
              else if (!isChosen && isMajority) { bg = `${T.mint}12`; border = `1.5px dashed ${T.mint}66`; }
            }
            return (
              <button key={side} onClick={!revealed && !timedOut ? () => { startTimer(); handleChoose(side); } : undefined}
                style={{ width:'100%', padding:'18px 16px', background:bg, border, borderRadius:18, cursor: !revealed && !timedOut ? 'pointer' : 'default', fontFamily:T.font, fontWeight:800, fontSize:15, color:textColor, textAlign:'left', transition:'all .2s', boxShadow:T.shadow, display:'flex', justifyContent:'space-between', alignItems:'center', gap:8 }}>
                <span style={{ flex:1, lineHeight:1.4 }}>{text}</span>
                {revealed && <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color: isMajority ? T.mint : T.inkMute, flexShrink:0 }}>{stat}%</span>}
              </button>
            );
          })}
        </div>
      )}
      {revealed && (
        <div style={{ textAlign:'center', marginTop:4 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color: won ? T.mint : T.coral }}>
            {won ? '✓ A többséggel értettél egyet!' : '✗ Kisebbségben voltál!'}
          </div>
          <button onClick={() => handleResult(won)} style={{ marginTop:10, width:'100%', padding:'14px 0', background: won ? T.mint : T.coral, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer' }}>
            {won ? '+1 pont!' : 'Iszik 1-et!'}
          </button>
        </div>
      )}
      {!started && !timedOut && !revealed && (
        <div style={{ textAlign:'center', fontFamily:T.font, fontSize:12, color:T.inkMute }}>Koppints egy opcióra — 5 mp visszaszámláló indul!</div>
      )}
    </div>
  );
}

// ── Medúza ────────────────────────────────────────────────────────────────────
function MeduzaGame({ players, onAdvance, onResult }) {
  const [phase, setPhase] = useState('intro');
  const [count, setCount] = useState(3);
  const [survivors, setSurvivors] = useState(() => players || []);
  const [round, setRound] = useState(1);
  const ivRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => () => clearInterval(ivRef.current), []);

  const startCountdown = () => {
    setCount(3);
    setPhase('countdown');
    const end = Date.now() + 3500;
    clearInterval(ivRef.current);
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      setCount(Math.max(1, Math.ceil(rem)));
      if (rem <= 0) { clearInterval(ivRef.current); setPhase('reveal'); }
    }, 80);
  };

  const handleEyeContact = (playerId) => {
    setSurvivors(prev => prev.filter(p => p.id !== playerId));
  };

  const handleNextRound = () => {
    if (survivors.length <= 2) {
      if (!advancedRef.current) {
        advancedRef.current = true;
        const dm = {};
        players?.forEach(p => { if (p && !survivors.find(s => s.id === p.id)) dm[p.id] = 1; });
        const winnerNames = survivors.map(s => s.name).join(' & ');
        onResult && onResult({ correct: true, playerName: winnerNames, drinks: 0, subtitle: `${winnerNames} nyert! A kiesők isznak.` });
        onAdvance && onAdvance(dm, {});
      }
      return;
    }
    setRound(r => r + 1);
    setPhase('intro');
  };

  if (phase === 'intro') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontSize:52 }}>🎯</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink }}>Medúza — {round}. kör</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.7 }}>
        Mindenki <strong>hajtsa le a fejét</strong> és nézzen valakire a körben.<br/>
        3-2-1-re <strong>emeljétek fel a fejet</strong>.<br/>
        Ha szemkontaktus van — mindkettő kiesik és iszik!
      </div>
      <div style={{ display:'flex', flexWrap:'wrap', gap:6, justifyContent:'center' }}>
        {survivors.map(p => <div key={p.id} style={{ display:'flex', alignItems:'center', gap:6, padding:'5px 12px', borderRadius:999, background:p.color+'22', border:`1.5px solid ${p.color}44` }}><div style={{ width:10, height:10, borderRadius:'50%', background:p.color }}/><span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink }}>{p.name}</span></div>)}
      </div>
      <button onClick={startCountdown} style={{ width:'100%', padding:'16px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>
        Mindenki kész — Start!
      </button>
    </div>
  );

  if (phase === 'countdown') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:16, minHeight:200 }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.1em' }}>Fejek le — nézz valakire!</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:96, color:T.ink, lineHeight:1, animation:'popIn .3s' }} key={count}>{count}</div>
    </div>
  );

  if (phase === 'reveal') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontSize:52 }}>👀</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink }}>Ki nézett a másikra?</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>Koppints azokra akikkel <strong>szemkontaktus</strong> volt — ők kiesnek és isznak.</div>
      <div style={{ display:'flex', flexDirection:'column', gap:8, width:'100%' }}>
        {survivors.map(p => (
          <button key={p.id} onClick={() => handleEyeContact(p.id)}
            style={{ padding:'14px 16px', borderRadius:14, border:`2px solid ${p.color}44`, background:p.color+'15', fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink, cursor:'pointer', display:'flex', alignItems:'center', gap:10, WebkitTapHighlightColor:'transparent' }}>
            <div style={{ width:14, height:14, borderRadius:'50%', background:p.color, flexShrink:0 }} />
            {p.name} — szemkontaktus volt 👁️
          </button>
        ))}
      </div>
      <button onClick={handleNextRound} style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>
        {survivors.length <= 2 ? '🏆 Vége — eredmény' : `Következő kör (${survivors.length} maradt)`}
      </button>
    </div>
  );

  return null;
}

// ── Farkasos ──────────────────────────────────────────────────────────────────
function FarkasosGame({ players, gameIdx, onAdvance, onResult }) {
  const assignRoles = (ps) => {
    const n = ps.length;
    const roles = [];
    const wolvesCount = n <= 5 ? 1 : n <= 8 ? 2 : 3;
    for (let i = 0; i < wolvesCount; i++) roles.push('🐺 Farkas');
    if (n >= 5) roles.push('💊 Orvos');
    if (n >= 6) roles.push('🔍 Nyomozó');
    while (roles.length < n) roles.push('👤 Faluslakó');
    const shuffled = [...roles].sort(() => Math.random() - 0.5);
    return ps.map((p, i) => ({ ...p, role: shuffled[i] }));
  };

  const [phase, setPhase] = useState('deal');
  const [roleRevealIdx, setRoleRevealIdx] = useState(0);
  const [rolesAssigned] = useState(() => assignRoles(players || []));
  const [showRole, setShowRole] = useState(false);
  const [eliminated, setEliminated] = useState([]);
  const [nightKill, setNightKill] = useState(null);
  const [nightHeal, setNightHeal] = useState(null);
  const [nightInvestigate, setNightInvestigate] = useState(null);
  const [nightPhase, setNightPhase] = useState('wolves');
  const [investigateResult, setInvestigateResult] = useState(null);
  const [dayVotes, setDayVotes] = useState({});
  const [round, setRound] = useState(1);
  const [gameOver, setGameOver] = useState(null);
  const advancedRef = useRef(false);

  const alive = rolesAssigned.filter(p => !eliminated.includes(p.id));
  const doctor = alive.find(p => p.role === '💊 Orvos');
  const detective = alive.find(p => p.role === '🔍 Nyomozó');

  const checkWin = (elim) => {
    const al = rolesAssigned.filter(p => !elim.includes(p.id));
    const w = al.filter(p => p.role === '🐺 Farkas').length;
    const v = al.filter(p => p.role !== '🐺 Farkas').length;
    if (w === 0) return 'village';
    if (w >= v) return 'wolves';
    return null;
  };

  const handleNightEnd = () => {
    const newElim = [...eliminated];
    if (nightKill && nightKill !== nightHeal) newElim.push(nightKill);
    setEliminated(newElim);
    setNightKill(null); setNightHeal(null); setNightInvestigate(null); setInvestigateResult(null);
    const result = checkWin(newElim);
    if (result) { setGameOver(result); setPhase('gameover'); return; }
    setPhase('day');
  };

  const handleDayVote = () => {
    const counts = {};
    Object.values(dayVotes).forEach(id => { counts[id] = (counts[id]||0)+1; });
    let maxV = 0, elimId = null;
    Object.entries(counts).forEach(([id, v]) => { if (v > maxV) { maxV = v; elimId = id; } });
    const newElim = elimId ? [...eliminated, elimId] : [...eliminated];
    setEliminated(newElim);
    setDayVotes({});
    const result = checkWin(newElim);
    if (result) { setGameOver(result); setPhase('gameover'); return; }
    setRound(r => r+1);
    setNightPhase('wolves');
    setPhase('night');
  };

  const btnS = (tone) => ({ width:'100%', padding:'11px 14px', border:'none', borderRadius:12, cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:14, background: tone==='mint'?T.mint:tone==='coral'?T.coral+'33':tone==='blue'?'#60A5FA33':'rgba(255,255,255,0.06)', color: tone==='mint'?'#fff':tone==='coral'?T.coral:tone==='blue'?'#60A5FA':'#CBD5E1', textAlign:'left', display:'flex', alignItems:'center', gap:10, marginBottom:6 });

  if (phase === 'deal') {
    const current = rolesAssigned[roleRevealIdx];
    return (
      <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>Szereposztás — {roleRevealIdx+1}/{rolesAssigned.length}</div>
        <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'24px', boxShadow:T.shadow, textAlign:'center' }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, color:T.inkSoft, marginBottom:12 }}>📱 Add át: <strong style={{color:T.ink}}>{current?.name}</strong></div>
          {!showRole ? (
            <button onClick={() => setShowRole(true)} style={{ padding:'16px 32px', background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer' }}>
              Megmutat 👁
            </button>
          ) : (
            <div>
              <div style={{ fontSize:52, marginBottom:8 }}>{current?.role?.split(' ')[0]}</div>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink }}>{current?.role?.split(' ').slice(1).join(' ')}</div>
              {current?.role === '🐺 Farkas' && <div style={{ fontFamily:T.font, fontSize:12, color:T.coral, marginTop:6 }}>Ne áruld el! Éjszaka ölhetsz.</div>}
              {current?.role === '💊 Orvos' && <div style={{ fontFamily:T.font, fontSize:12, color:T.mint, marginTop:6 }}>Éjszaka megmenthetsz valakit.</div>}
              {current?.role === '🔍 Nyomozó' && <div style={{ fontFamily:T.font, fontSize:12, color:'#60A5FA', marginTop:6 }}>Éjszaka megkérdezheted: farkas-e valaki.</div>}
              <button onClick={() => { setShowRole(false); if (roleRevealIdx < rolesAssigned.length - 1) setRoleRevealIdx(i => i+1); else setPhase('night'); }}
                style={{ marginTop:16, padding:'12px 28px', background:T.mint, border:'none', borderRadius:12, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>
                {roleRevealIdx < rolesAssigned.length - 1 ? 'Következő →' : 'Játék kezd! 🌙'}
              </button>
            </div>
          )}
        </div>
        <div style={{ display:'flex', gap:6, flexWrap:'wrap', justifyContent:'center' }}>
          {rolesAssigned.map((p, i) => <div key={p.id} style={{ padding:'4px 10px', borderRadius:999, background: i < roleRevealIdx ? T.mint+'22' : i === roleRevealIdx ? '#E2E8F022' : T.surfaceMuted, fontFamily:T.font, fontSize:11, fontWeight:700, color: i < roleRevealIdx ? T.mint : T.inkSoft }}>{i < roleRevealIdx ? '✓' : i === roleRevealIdx ? '●' : '○'} {p.name}</div>)}
        </div>
      </div>
    );
  }

  if (phase === 'night') return (
    <div style={{ background:'#0F1729', borderRadius:20, padding:'20px 16px', display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:18, color:'#E2E8F0' }}>🌙 {round}. éjszaka</div>
      <div style={{ fontFamily:T.font, fontSize:12, color:'#94A3B8', textAlign:'center', marginBottom:4 }}>Mindenki csukja le a szemét!</div>
      {nightPhase === 'wolves' && (
        <div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.coral, marginBottom:8 }}>🐺 Farkasok — kit öltök?</div>
          {alive.filter(p => p.role !== '🐺 Farkas').map(p => (
            <button key={p.id} onClick={() => setNightKill(p.id)} style={{ ...btnS(nightKill===p.id?'coral':''), border: nightKill===p.id ? `1.5px solid ${T.coral}` : '1.5px solid transparent' }}>
              <div style={{ width:10, height:10, borderRadius:'50%', background:p.color }} />{p.name}
            </button>
          ))}
          <button disabled={!nightKill} onClick={() => setNightPhase(doctor ? 'doctor' : detective ? 'detective' : 'reveal')}
            style={{ ...btnS('mint'), opacity: nightKill ? 1 : 0.4, justifyContent:'center', marginTop:4 }}>Döntés kész →</button>
        </div>
      )}
      {nightPhase === 'doctor' && doctor && (
        <div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.mint, marginBottom:8 }}>💊 Orvos ({doctor.name}) — kit mentesz?</div>
          {alive.map(p => (
            <button key={p.id} onClick={() => setNightHeal(p.id)} style={{ ...btnS(nightHeal===p.id?'mint':''), border: nightHeal===p.id ? `1.5px solid ${T.mint}` : '1.5px solid transparent' }}>
              <div style={{ width:10, height:10, borderRadius:'50%', background:p.color }} />{p.name}
            </button>
          ))}
          <button onClick={() => setNightPhase(detective ? 'detective' : 'reveal')} style={{ ...btnS('mint'), justifyContent:'center', marginTop:4 }}>Döntés kész →</button>
        </div>
      )}
      {nightPhase === 'detective' && detective && (
        <div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'#60A5FA', marginBottom:8 }}>🔍 Nyomozó ({detective.name}) — kit vizsgálsz?</div>
          {alive.filter(p => p.id !== detective.id).map(p => (
            <button key={p.id} onClick={() => { setNightInvestigate(p.id); setInvestigateResult(p.role === '🐺 Farkas' ? `${p.name} FARKAS! 🐺` : `${p.name} ártatlan 👤`); }}
              style={{ ...btnS(nightInvestigate===p.id?'blue':''), border: nightInvestigate===p.id ? `1.5px solid #60A5FA` : '1.5px solid transparent' }}>
              <div style={{ width:10, height:10, borderRadius:'50%', background:p.color }} />{p.name}
            </button>
          ))}
          {investigateResult && <div style={{ background:'rgba(96,165,250,0.15)', borderRadius:12, padding:'10px 14px', fontFamily:T.font, fontWeight:700, fontSize:14, color:'#60A5FA', marginTop:4 }}>{investigateResult}</div>}
          <button disabled={!nightInvestigate} onClick={() => setNightPhase('reveal')} style={{ ...btnS('blue'), opacity: nightInvestigate?1:0.4, justifyContent:'center', marginTop:4 }}>Kész →</button>
        </div>
      )}
      {nightPhase === 'reveal' && (
        <div style={{ textAlign:'center' }}>
          <div style={{ fontFamily:T.font, fontSize:13, color:'#94A3B8', marginBottom:12 }}>Mindenki kinyithatja a szemét!</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color: nightKill && nightKill !== nightHeal ? T.coral : T.mint, marginBottom:16 }}>
            {nightKill && nightKill !== nightHeal
              ? `😵 ${rolesAssigned.find(p=>p.id===nightKill)?.name} meghalt éjjel!`
              : nightKill === nightHeal
              ? `💊 Az orvos megmentette ${rolesAssigned.find(p=>p.id===nightKill)?.name}-t!`
              : '😴 Csendes éjszaka.'}
          </div>
          <button onClick={handleNightEnd} style={{ padding:'14px 28px', background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>Nappal ☀️</button>
        </div>
      )}
    </div>
  );

  if (phase === 'day') return (
    <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>☀️ {round}. nappal — szavazás</div>
      <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, textAlign:'center' }}>Vitatkozzatok, majd szavazzon mindenki: ki a farkas?</div>
      <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
        {alive.map(p => {
          const voteCount = Object.values(dayVotes).filter(id=>id===p.id).length;
          return (
            <div key={p.id} style={{ background:T.surface, borderRadius:14, padding:'10px 14px', display:'flex', alignItems:'center', gap:10, boxShadow:T.shadow }}>
              <div style={{ width:12, height:12, borderRadius:'50%', background:p.color, flexShrink:0 }}/>
              <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>{p.name}</div>
              <div style={{ display:'flex', gap:5 }}>
                {alive.filter(v => v.id !== p.id).map(voter => (
                  <button key={voter.id} onClick={() => setDayVotes(v => ({ ...v, [voter.id]: p.id }))}
                    style={{ width:26, height:26, borderRadius:'50%', border: dayVotes[voter.id]===p.id ? `2px solid ${T.coral}` : `2px solid ${voter.color}55`, background: dayVotes[voter.id]===p.id ? T.coral : voter.color+'22', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:9, color: dayVotes[voter.id]===p.id ? '#fff' : T.inkSoft, flexShrink:0 }}>
                    {voter.name.charAt(0)}
                  </button>
                ))}
              </div>
              {voteCount > 0 && <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.coral, flexShrink:0, minWidth:20, textAlign:'center' }}>{voteCount}🗳️</div>}
            </div>
          );
        })}
      </div>
      <button onClick={handleDayVote} style={{ padding:'14px 0', background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer', width:'100%' }}>
        Kivégzés & Éjszaka 🌙
      </button>
    </div>
  );

  if (phase === 'gameover') {
    const endGame = () => {
      if (advancedRef.current) return;
      advancedRef.current = true;
      onAdvance && onAdvance({}, {});
    };
    return (
      <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
        <div style={{ fontSize:52 }}>{gameOver === 'village' ? '🎉' : '🐺'}</div>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink, textAlign:'center' }}>
          {gameOver === 'village' ? 'A Falu Győzött!' : 'A Farkasok Győztek!'}
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:6, width:'100%' }}>
          {rolesAssigned.map(p => (
            <div key={p.id} style={{ padding:'10px 14px', borderRadius:12, background: eliminated.includes(p.id) ? T.coral+'18' : T.mint+'18', display:'flex', alignItems:'center', gap:10, opacity: eliminated.includes(p.id) ? 0.6 : 1 }}>
              <div style={{ width:10, height:10, borderRadius:'50%', background:p.color }}/>
              <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>{p.name}</div>
              <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft }}>{p.role}</div>
              {eliminated.includes(p.id) && <span>☠️</span>}
            </div>
          ))}
        </div>
        <button onClick={endGame} style={{ width:'100%', padding:'14px 0', background:T.mint, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer' }}>
          Tovább
        </button>
      </div>
    );
  }

  return null;
}

// ── Mutasd Ne Mondd ───────────────────────────────────────────────────────────
function MutasdGame({ gameIdx, challenger, onAdvance, onResult }) {
  const word = MUTASD_SZAVAK[gameIdx % MUTASD_SZAVAK.length];
  const [phase, setPhase] = useState('ready');
  const [timeLeft, setTimeLeft] = useState(15);
  const ivRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => () => clearInterval(ivRef.current), []);

  const start = () => {
    setPhase('playing');
    const end = Date.now() + 15000;
    clearInterval(ivRef.current);
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      setTimeLeft(Math.ceil(rem));
      if (rem <= 0) { clearInterval(ivRef.current); setPhase('done'); }
    }, 100);
  };

  const handleResult = (won) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    clearInterval(ivRef.current);
    if (won) {
      onResult && onResult({ correct: true, playerName: challenger?.name||'', drinks:0, subtitle: (challenger?.name||'') + ' sikeresen mutogatta — +1 pont!' });
      onAdvance && onAdvance({}, challenger ? {[challenger.id]:1} : {});
    } else {
      onResult && onResult({ correct: false, playerName: challenger?.name||'', drinks:1, subtitle: (challenger?.name||'') + ' iszik 1-et!' });
      onAdvance && onAdvance(challenger ? {[challenger.id]:1} : {}, {});
    }
  };

  if (phase === 'ready') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontSize:52 }}>🎭</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>{challenger?.name} mutogat!</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>A szó megjelenik — 15 mp alatt el kell mutogatni szavak nélkül.<br/>A többiek kitalálják?</div>
      <button onClick={start} style={{ width:'100%', padding:'16px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>
        Megmutat!
      </button>
    </div>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:32, color: timeLeft <= 5 ? T.coral : T.mint }}>
        {phase === 'done' ? '⏰ Lejárt!' : timeLeft + 's'}
      </div>
      <div style={{ background:'#1B2340', borderRadius:20, padding:'24px 32px', textAlign:'center', width:'100%', boxSizing:'border-box' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:30, color:'#fff' }}>{word}</div>
        <div style={{ fontFamily:T.font, fontSize:11, color:'#94A3B8', marginTop:4 }}>NE MONDD KI!</div>
      </div>
      <div style={{ display:'flex', gap:10, width:'100%' }}>
        <button onClick={() => { clearInterval(ivRef.current); handleResult(true); }} style={{ flex:1, padding:'14px 0', background:T.mint, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>✓ Kitalálták!</button>
        <button onClick={() => handleResult(false)} style={{ flex:1, padding:'14px 0', background:T.coral, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>✗ Nem sikerült</button>
      </div>
    </div>
  );
}

// ── Emoji Kvíz ────────────────────────────────────────────────────────────────
function EmojiKvizGame({ gameIdx, challenger, onAdvance, onResult }) {
  const q = EMOJI_REJTVENY_SHUFFLED[gameIdx % EMOJI_REJTVENY_SHUFFLED.length];
  const [revealed, setRevealed] = useState(false);
  const advancedRef = useRef(false);

  useEffect(() => { setRevealed(false); advancedRef.current = false; }, [gameIdx]);

  const handleResult = (won) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    if (won) {
      onResult && onResult({ correct: true, playerName: challenger?.name||'', drinks:0, subtitle: (challenger?.name||'') + ' eltalálta — +1 pont!' });
      onAdvance && onAdvance({}, challenger ? {[challenger.id]:1} : {});
    } else {
      onResult && onResult({ correct: false, playerName: challenger?.name||'', drinks:1, subtitle: (challenger?.name||'') + ' iszik 1-et!' });
      onAdvance && onAdvance(challenger ? {[challenger.id]:1} : {}, {});
    }
  };

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:20 }}>
      <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.08em' }}>{q.category}</div>
      <div style={{ background:T.surface, borderRadius:24, padding:'28px 20px', textAlign:'center', width:'100%', boxShadow:T.shadow }}>
        <div style={{ fontSize:56, letterSpacing:'0.1em', lineHeight:1.3 }}>{q.emojis}</div>
        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkMute, marginTop:10 }}>Mi lehet ez?</div>
      </div>
      {!revealed ? (
        <button onClick={() => setRevealed(true)} style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>
          🔍 Felfed
        </button>
      ) : (
        <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:10 }}>
          <div style={{ background:`${T.mint}18`, borderRadius:16, padding:'16px', textAlign:'center', border:`1.5px solid ${T.mint}44` }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink }}>{q.answer}</div>
          </div>
          <div style={{ display:'flex', gap:10 }}>
            <button onClick={() => handleResult(true)} style={{ flex:1, padding:'13px 0', background:T.mint, border:'none', borderRadius:12, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✓ Eltalálta</button>
            <button onClick={() => handleResult(false)} style={{ flex:1, padding:'13px 0', background:T.coral, border:'none', borderRadius:12, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✗ Nem találta</button>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Tabu Szó ──────────────────────────────────────────────────────────────────
function TabuGame({ gameIdx, challenger, onAdvance, onResult }) {
  const q = TABU_SHUFFLED[gameIdx % TABU_SHUFFLED.length];
  const [phase, setPhase] = useState('ready');
  const [timeLeft, setTimeLeft] = useState(30);
  const ivRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => () => clearInterval(ivRef.current), []);

  const start = () => {
    setPhase('playing');
    const end = Date.now() + 30000;
    clearInterval(ivRef.current);
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      setTimeLeft(Math.ceil(rem));
      if (rem <= 0) { clearInterval(ivRef.current); setPhase('done'); }
    }, 100);
  };

  const handleResult = (won) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    clearInterval(ivRef.current);
    if (won) {
      onResult && onResult({ correct: true, playerName: challenger?.name||'', drinks:0, subtitle: (challenger?.name||'') + ' sikeresen leírta — +1 pont!' });
      onAdvance && onAdvance({}, challenger ? {[challenger.id]:1} : {});
    } else {
      onResult && onResult({ correct: false, playerName: challenger?.name||'', drinks:1, subtitle: (challenger?.name||'') + ' iszik 1-et!' });
      onAdvance && onAdvance(challenger ? {[challenger.id]:1} : {}, {});
    }
  };

  if (phase === 'ready') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontSize:52 }}>🚫</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>{challenger?.name} magyaráz!</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>30 mp alatt el kell magyarázni a szót a 3 tiltott szó nélkül. A csapat kitalálja?</div>
      <button onClick={start} style={{ width:'100%', padding:'16px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>Megmutat!</button>
    </div>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:28, color: timeLeft <= 5 ? T.coral : T.mint }}>
        {phase === 'done' ? '⏰' : timeLeft + 's'}
      </div>
      <div style={{ background:'#1B2340', borderRadius:20, padding:'20px', textAlign:'center' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:30, color:'#fff', marginBottom:12 }}>{q.word}</div>
        <div style={{ fontFamily:T.font, fontSize:11, color:'#94A3B8', textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:8 }}>🚫 Tiltott szavak</div>
        <div style={{ display:'flex', gap:8, justifyContent:'center', flexWrap:'wrap' }}>
          {q.taboo.map((t, i) => <div key={i} style={{ padding:'5px 14px', background:T.coral+'33', borderRadius:999, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.coral, border:`1.5px solid ${T.coral}44` }}>{t}</div>)}
        </div>
      </div>
      <div style={{ display:'flex', gap:10 }}>
        <button onClick={() => { clearInterval(ivRef.current); handleResult(true); }} style={{ flex:1, padding:'14px 0', background:T.mint, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✓ Kitalálták</button>
        <button onClick={() => handleResult(false)} style={{ flex:1, padding:'14px 0', background:T.coral, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✗ Nem / Szabálysértés</button>
      </div>
    </div>
  );
}

// ── Gyors Matek ───────────────────────────────────────────────────────────────
function MatekGame({ gameIdx, challenger, onAdvance, onResult }) {
  const genQ = (idx) => {
    const s = ((idx * 1234567 + 7654321) >>> 0);
    const rng = (n, salt) => { let x = (s ^ (salt * 2246822519 + 3266489917)) >>> 0; x ^= x<<13; x ^= x>>17; x ^= x<<5; return (x>>>0) % n; };
    const ops = ['+','-','×'];
    const op = ops[rng(3, 1)];
    let a, b, ans;
    if (op==='+') { a = rng(30)+10; b = rng(30)+10; ans = a+b; }
    else if (op==='-') { a = rng(50)+30; b = rng(25)+5; ans = a-b; }
    else { a = rng(12)+3; b = rng(12)+3; ans = a*b; }
    const wrongs = new Set();
    let attempts = 0;
    while (wrongs.size < 2 && attempts < 30) {
      attempts++;
      const d = (rng(6, attempts*7+2)+1) * (rng(2, attempts*3+1)===0?1:-1);
      const w = ans + d;
      if (w > 0 && w !== ans) wrongs.add(w);
    }
    const options = [ans, ...[...wrongs].slice(0,2)].sort((x,y) => rng(3, x+y*7)-1);
    return { q:`${a} ${op} ${b} = ?`, ans, options };
  };

  const [qData] = useState(() => genQ(gameIdx));
  const [timeLeft, setTimeLeft] = useState(3);
  const [chosen, setChosen] = useState(null);
  const [timedOut, setTimedOut] = useState(false);
  const ivRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => {
    const end = Date.now() + 3000;
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      setTimeLeft(parseFloat(rem.toFixed(1)));
      if (rem <= 0) { clearInterval(ivRef.current); setTimedOut(true); }
    }, 80);
    return () => clearInterval(ivRef.current);
  }, []);

  useEffect(() => {
    if ((timedOut || chosen !== null) && !advancedRef.current) {
      advancedRef.current = true;
      clearInterval(ivRef.current);
      const won = chosen === qData.ans;
      setTimeout(() => {
        if (won) {
          onResult && onResult({ correct: true, playerName: challenger?.name||'', drinks:0, subtitle: (challenger?.name||'') + ' megoldotta — +1 pont!' });
          onAdvance && onAdvance({}, challenger ? {[challenger.id]:1} : {});
        } else {
          onResult && onResult({ correct: false, playerName: challenger?.name||'', drinks:1, subtitle: (challenger?.name||'') + (timedOut ? ' — lejárt az idő, iszik!' : ' — rossz válasz, iszik!') });
          onAdvance && onAdvance(challenger ? {[challenger.id]:1} : {}, {});
        }
      }, 600);
    }
  }, [timedOut, chosen]);

  const progress = Math.max(0, timeLeft / 3);

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ width:'100%', height:6, background:T.surfaceMuted, borderRadius:3, overflow:'hidden' }}>
        <div style={{ height:'100%', width:(progress*100)+'%', background: progress > 0.5 ? T.mint : progress > 0.2 ? T.yellow : T.coral, transition:'width .08s linear, background .3s' }} />
      </div>
      <div style={{ background:T.surface, borderRadius:24, padding:'28px 20px', textAlign:'center', width:'100%', boxShadow:T.shadow }}>
        <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:36, color:T.ink, letterSpacing:'-0.02em' }}>{qData.q}</div>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:10, width:'100%' }}>
        {qData.options.map((opt, i) => {
          const isChosen = chosen === opt;
          const isCorrect = opt === qData.ans;
          let bg = T.surface, color = T.ink, border = `1.5px solid rgba(20,30,50,0.08)`;
          if (timedOut || chosen !== null) {
            if (isCorrect) { bg = `${T.mint}22`; color = T.mint; border = `2px solid ${T.mint}`; }
            else if (isChosen) { bg = `${T.coral}22`; color = T.coral; border = `2px solid ${T.coral}`; }
          }
          return (
            <button key={i} onClick={() => !timedOut && chosen === null && setChosen(opt)}
              style={{ padding:'18px 0', background:bg, border, borderRadius:16, fontFamily:'monospace', fontWeight:900, fontSize:22, color, cursor: chosen===null && !timedOut ? 'pointer' : 'default', boxShadow:T.shadow }}>
              {opt}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── Reakció Teszt ─────────────────────────────────────────────────────────────
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
        <React.Fragment>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>{currentPlayer?.name} — Kész?</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>A képernyő piroson vár, majd zöldre vált.<br/>Koppints a lehető leggyorsabban!</div>
          {results.length > 0 && (
            <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:4 }}>
              {results.map((r, i) => <div key={i} style={{ display:'flex', justifyContent:'space-between', padding:'7px 14px', background:T.surface, borderRadius:10, boxShadow:T.shadow }}><span style={{ fontFamily:T.font, fontSize:13, color:T.ink, fontWeight:700 }}>{r.player.name}</span><span style={{ fontFamily:'monospace', fontWeight:700, fontSize:13, color:T.mint }}>{r.ms}ms</span></div>)}
            </div>
          )}
          <button onClick={startWaiting} style={{ width:'100%', padding:'16px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>
            Start!
          </button>
        </React.Fragment>
      )}
      {(phase === 'waiting' || phase === 'ready') && (
        <div onClick={handleTap}
          style={{ width:'100%', minHeight:240, borderRadius:24, background: phase==='ready' ? '#22C55E' : '#EF4444', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', cursor:'pointer', userSelect:'none', WebkitUserSelect:'none', gap:10, WebkitTapHighlightColor:'transparent' }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:26, color:'#fff' }}>
            {phase === 'ready' ? '🟢 MOST! Koppints!' : '🔴 Várj...'}
          </div>
          {phase === 'waiting' && <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.7)' }}>Ha korán koppintasz — újrakezdjük</div>}
          <div style={{ fontFamily:T.font, fontSize:16, color:'rgba(255,255,255,0.85)', fontWeight:700 }}>{currentPlayer?.name}</div>
        </div>
      )}
      {phase === 'done' && (
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:12, width:'100%' }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:38, color:T.mint }}>{reactionMs}ms</div>
          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>{currentPlayer?.name} reakcióideje</div>
          {!allDone ? (
            <button onClick={next} style={{ width:'100%', padding:'14px 0', background:T.mint, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer' }}>
              Következő: {players?.[currentIdx+1]?.name} →
            </button>
          ) : (
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft }}>Mindenki kész — eredmény hamarosan…</div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Szám Sorrend ──────────────────────────────────────────────────────────────
function SzamsorGame({ gameIdx, challenger, onAdvance, onResult }) {
  const COUNT = 9;
  const genPos = (idx) => {
    const s = (idx * 2654435761 + 1013904223) >>> 0;
    const rng = (salt) => { let x = (s ^ (salt * 2246822519 + 3266489917)) >>> 0; x ^= x<<13; x ^= x>>17; x ^= x<<5; return (x>>>0)/4294967296; };
    const positions = [];
    for (let i = 0; i < COUNT; i++) {
      let x, y, att = 0;
      do { x = 8 + rng(i*5+att)*80; y = 8 + rng(i*5+att+1)*76; att++; }
      while (positions.some(p => Math.abs(p.x-x)<16 && Math.abs(p.y-y)<14) && att < 30);
      positions.push({ num: i+1, x, y });
    }
    return positions;
  };

  const [positions] = useState(() => genPos(gameIdx));
  const [next, setNext] = useState(1);
  const [startMs] = useState(() => Date.now());
  const [elapsed, setElapsed] = useState(0);
  const [done, setDone] = useState(false);
  const advancedRef = useRef(false);
  const ivRef = useRef(null);

  useEffect(() => {
    ivRef.current = setInterval(() => { if (!done) setElapsed(Date.now() - startMs); }, 80);
    return () => clearInterval(ivRef.current);
  }, [done]);

  const tap = (num) => {
    if (num !== next || done) return;
    if (next === COUNT) {
      clearInterval(ivRef.current);
      const ms = Date.now() - startMs;
      setElapsed(ms);
      setDone(true);
      setNext(COUNT + 1);
      if (!advancedRef.current) {
        advancedRef.current = true;
        const sec = (ms/1000).toFixed(2);
        setTimeout(() => {
          onResult && onResult({ correct: true, playerName: challenger?.name||'', drinks:0, subtitle: `${challenger?.name||''} — ${sec}mp! Kövi játékos!` });
          onAdvance && onAdvance({}, {});
        }, 600);
      }
    } else {
      setNext(n => n+1);
    }
  };

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>
          {done ? '🎉 Kész!' : <>Következő: <span style={{ color:T.mint, fontWeight:900, fontSize:18 }}>{next}</span></>}
        </div>
        <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:20, color: done ? T.mint : T.ink }}>{(elapsed/1000).toFixed(done?2:1)}s</div>
      </div>
      <div style={{ position:'relative', width:'100%', paddingBottom:'90%', background:T.surfaceMuted, borderRadius:20, overflow:'hidden' }}>
        {positions.map(({ num, x, y }) => {
          const tapped = num < next;
          const isNext = num === next && !done;
          return (
            <div key={num} onClick={() => tap(num)}
              style={{ position:'absolute', left:x+'%', top:y+'%', width:46, height:46, borderRadius:14, background: tapped ? T.mint : isNext ? '#1B2340' : T.surface, border: isNext ? `2.5px solid ${T.mint}` : tapped ? 'none' : `1.5px solid rgba(20,30,50,0.10)`, display:'grid', placeItems:'center', cursor: tapped||done ? 'default' : 'pointer', transform:'translate(-50%,-50%)', boxShadow: isNext ? `0 0 14px ${T.mint}88` : T.shadow, transition:'background .15s', userSelect:'none', WebkitUserSelect:'none', WebkitTapHighlightColor:'transparent' }}>
              <span style={{ fontFamily:'monospace', fontWeight:900, fontSize:16, color: tapped||isNext ? '#fff' : T.ink }}>{tapped ? '✓' : num}</span>
            </div>
          );
        })}
      </div>
      {done && <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:22, color:T.mint }}>🎉 {(elapsed/1000).toFixed(2)} mp!</div>}
    </div>
  );
}

"""

content = content.replace(COMP_ANCHOR, COMPONENTS + COMP_ANCHOR, 1)

# ── 4. Verify and write ───────────────────────────────────────────────────────
assert "function RitmusGame" in content
assert "function MitValasztanalGame" in content
assert "function MeduzaGame" in content
assert "function FarkasosGame" in content
assert "function MutasdGame" in content
assert "function EmojiKvizGame" in content
assert "function TabuGame" in content
assert "function MatekGame" in content
assert "function ReakcioGame" in content
assert "function SzamsorGame" in content
assert "gameId === 'ritmus'" in content
assert "v9.96" in content

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ patch_9_96.py done!")
