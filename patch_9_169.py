#!/usr/bin/env python3
"""patch_9_169.py — Tabu → Páros duel; Mutasd, Ne Mondd → Mutasd!"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.168';" in content
content = content.replace("const APP_VERSION = 'v9.168';", "const APP_VERSION = 'v9.169';")

# ── 1. Rename Mutasd, Ne Mondd → Mutasd! ──
OLD_MUTASD_NAME = "name:'Mutasd, Ne Mondd'"
NEW_MUTASD_NAME = "name:'Mutasd!'"
assert OLD_MUTASD_NAME in content, "Mutasd name not found"
content = content.replace(OLD_MUTASD_NAME, NEW_MUTASD_NAME, 1)

# ── 2. Change Tabu category Csapat → Páros and update desc ──
OLD_TABU_DEF = "{ id:'tabu',     roundTime:'fast', name:'Tabu Szó',         difficulty:'nehéz',   category:'Csapat', emoji:'🚫', img:IMGS['tabu_icon.png'], symbol:IMGS['tabu_symbol.png'], color:'#EF4444', desc:'Az app kisorsol egy játékost akinek le kell írnia egy szót 3 tiltott szó használata nélkül. A csapatnak 30 másodperce van kitalálni. Ha sikerül +1 pont, ha nem a leírás játékos iszik.' }"
NEW_TABU_DEF = "{ id:'tabu',     roundTime:'fast', name:'Tabu Szó',         difficulty:'nehéz',   category:'Páros',  emoji:'🚫', img:IMGS['tabu_icon.png'], symbol:IMGS['tabu_symbol.png'], color:'#EF4444', desc:'Páros párharc: mindkét játékos magyaráz egy szót, a másik talál. Aki sikeresen elmagyarázta +1 pont, aki nem — iszik.' }"
assert OLD_TABU_DEF in content, "Tabu game def not found"
content = content.replace(OLD_TABU_DEF, NEW_TABU_DEF, 1)

# ── 3. Pass opponent prop to TabuGame ──
OLD_TABU_RENDER = "if (gameId === 'tabu')     return <TabuGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;"
NEW_TABU_RENDER = "if (gameId === 'tabu')     return <TabuGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;"
assert OLD_TABU_RENDER in content, "TabuGame render not found"
content = content.replace(OLD_TABU_RENDER, NEW_TABU_RENDER, 1)

# ── 4. Remove tabu from Csapat "Ki rontott?" exclusion (it's Páros now) ──
OLD_CSAPAT_EXCL = "currentGameId !== 'tabu' && ("
NEW_CSAPAT_EXCL = "("
assert OLD_CSAPAT_EXCL in content, "Csapat tabu exclusion not found"
content = content.replace(OLD_CSAPAT_EXCL, NEW_CSAPAT_EXCL, 1)

# ── 5. Add tabu to Páros CTA exclusion (it handles results internally) ──
OLD_PAROS_EXCL = "currentGameId !== 'szamsor' && currentGameId !== 'reakcio' && currentGameId !== 'ritmus' && ("
NEW_PAROS_EXCL = "currentGameId !== 'szamsor' && currentGameId !== 'reakcio' && currentGameId !== 'ritmus' && currentGameId !== 'tabu' && ("
assert OLD_PAROS_EXCL in content, "Páros CTA exclusion not found"
content = content.replace(OLD_PAROS_EXCL, NEW_PAROS_EXCL, 1)

# ── 6. Replace TabuGame component with Páros duel version ──
OLD_TABU_COMPONENT = """// ── Tabu Szó ───────────────────────────────────────────────────────────────────
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
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>30 mp alatt el kell magyarázni a szót a 3 tiltott szó nélkül.</div>
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
        <button onClick={() => handleResult(true)} style={{ flex:1, padding:'14px 0', background:T.mint, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✓ Kitalálták</button>
        <button onClick={() => handleResult(false)} style={{ flex:1, padding:'14px 0', background:T.coral, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✗ Nem / Szabálysértés</button>
      </div>
    </div>
  );
}"""

NEW_TABU_COMPONENT = """// ── Tabu Szó (Páros duel) ──────────────────────────────────────────────────────
function TabuGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  // phase: 'intro1'|'playing1'|'done1'|'intro2'|'playing2'|'result'
  const [phase, setPhase] = useState('intro1');
  const [timeLeft, setTimeLeft] = useState(30);
  const [p1Won, setP1Won] = useState(null);
  const [p2Won, setP2Won] = useState(null);
  const ivRef = useRef(null);
  const advancedRef = useRef(false);

  const q1 = TABU_SHUFFLED[gameIdx * 2 % TABU_SHUFFLED.length];
  const q2 = TABU_SHUFFLED[(gameIdx * 2 + 1) % TABU_SHUFFLED.length];
  const currentQ = phase.includes('1') ? q1 : q2;
  const currentPlayer = phase.includes('1') ? challenger : opponent;

  useEffect(() => () => clearInterval(ivRef.current), []);

  const startTimer = (nextPhase) => {
    setTimeLeft(30);
    setPhase(nextPhase);
    const end = Date.now() + 30000;
    clearInterval(ivRef.current);
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      setTimeLeft(Math.ceil(rem));
      if (rem <= 0) { clearInterval(ivRef.current); setPhase(nextPhase === 'playing1' ? 'done1' : 'result_pending'); }
    }, 100);
  };

  const handleRoundResult = (won) => {
    clearInterval(ivRef.current);
    if (phase === 'playing1' || phase === 'done1') {
      setP1Won(won);
      setPhase('intro2');
    } else {
      setP2Won(won);
      finalize(p1Won, won);
    }
  };

  const finalize = (w1, w2) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    const p1Drinks = w1 ? 0 : 1;
    const p2Drinks = w2 ? 0 : 1;
    const drinks = {};
    const points = {};
    if (challenger) { if (w1) points[challenger.id] = 1; else drinks[challenger.id] = p1Drinks; }
    if (opponent)   { if (w2) points[opponent.id]   = 1; else drinks[opponent.id]   = p2Drinks; }
    let subtitle = '';
    if (w1 && !w2) subtitle = (challenger?.name||'') + ' nyert — +1 pont!';
    else if (!w1 && w2) subtitle = (opponent?.name||'') + ' nyert — +1 pont!';
    else if (w1 && w2) subtitle = 'Mindkettő sikerült — mindenki +1 pont!';
    else subtitle = 'Egyik sem sikerült — mindenki iszik!';
    onResult && onResult({ correct: w1 || w2, playerName: '', drinks: Math.max(p1Drinks, p2Drinks), subtitle });
    onAdvance && onAdvance(drinks, points);
  };

  // after timer runs out on round 2
  useEffect(() => {
    if (phase === 'result_pending') handleRoundResult(false);
  }, [phase]);

  if (phase === 'intro1') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.08em' }}>Forduló 1 / 2</div>
      <div style={{ fontSize:48 }}>🚫</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, textAlign:'center' }}>{challenger?.name} magyaráz!</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>{opponent?.name} talál. 30 mp, 3 tiltott szó nélkül.</div>
      <button onClick={() => startTimer('playing1')} style={{ width:'100%', padding:'16px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>Start!</button>
    </div>
  );

  if (phase === 'intro2') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.08em' }}>Forduló 2 / 2</div>
      <div style={{ fontSize:48 }}>🚫</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, textAlign:'center' }}>{opponent?.name} magyaráz!</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>{challenger?.name} talál. 30 mp, 3 tiltott szó nélkül.</div>
      <button onClick={() => startTimer('playing2')} style={{ width:'100%', padding:'16px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>Start!</button>
    </div>
  );

  const isPlaying = phase === 'playing1' || phase === 'playing2';
  const isDone = phase === 'done1';

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ textAlign:'center' }}>
        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:28, color: timeLeft <= 5 ? T.coral : T.mint }}>
          {isDone ? '⏰' : timeLeft + 's'}
        </span>
        <span style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, marginLeft:8 }}>{currentPlayer?.name} magyaráz</span>
      </div>
      <div style={{ background:'#1B2340', borderRadius:20, padding:'20px', textAlign:'center' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:30, color:'#fff', marginBottom:12 }}>{currentQ.word}</div>
        <div style={{ fontFamily:T.font, fontSize:11, color:'#94A3B8', textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:8 }}>🚫 Tiltott szavak</div>
        <div style={{ display:'flex', gap:8, justifyContent:'center', flexWrap:'wrap' }}>
          {currentQ.taboo.map((t, i) => <div key={i} style={{ padding:'5px 14px', background:T.coral+'33', borderRadius:999, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.coral, border:`1.5px solid ${T.coral}44` }}>{t}</div>)}
        </div>
      </div>
      <div style={{ display:'flex', gap:10 }}>
        <button onClick={() => handleRoundResult(false)} style={{ flex:1, padding:'14px 0', background:T.coral, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✗ Nem / Szabálysértés</button>
        <button onClick={() => handleRoundResult(true)} style={{ flex:1, padding:'14px 0', background:T.mint, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✓ Kitalálták</button>
      </div>
    </div>
  );
}"""

assert OLD_TABU_COMPONENT in content, "TabuGame component not found"
content = content.replace(OLD_TABU_COMPONENT, NEW_TABU_COMPONENT, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.169 ready")
