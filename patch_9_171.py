#!/usr/bin/env python3
"""patch_9_171.py — Tabu → Páros: egy kör, challenger mond, opponent talál, mindkettő pont/korty"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.170';" in content
content = content.replace("const APP_VERSION = 'v9.170';", "const APP_VERSION = 'v9.171';")

# ── 1. Tabu: Csapat → Páros ──
OLD_DEF = "{ id:'tabu',     roundTime:'fast', name:'Tabu Szó',         difficulty:'nehéz',   category:'Csapat', emoji:'🚫', img:IMGS['tabu_icon.png'], symbol:IMGS['tabu_symbol.png'], color:'#EF4444', desc:'Az app kisorsol egy játékost akinek el kell magyaráznia egy szót 3 tiltott szó nélkül. Ha a csapat kitalálja mindenki +1 pont, ha nem — mindenki iszik.' }"
NEW_DEF = "{ id:'tabu',     roundTime:'fast', name:'Tabu Szó',         difficulty:'nehéz',   category:'Páros',  emoji:'🚫', img:IMGS['tabu_icon.png'], symbol:IMGS['tabu_symbol.png'], color:'#EF4444', desc:'Páros játék: az egyik játékos magyaráz, a másik talál. Ha sikerül — mindkettő +1 pont, ha nem — mindkettő iszik.' }"
assert OLD_DEF in content, "Tabu def not found"
content = content.replace(OLD_DEF, NEW_DEF, 1)

# ── 2. Pass opponent to TabuGame render ──
OLD_RENDER = "if (gameId === 'tabu')     return <TabuGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;"
NEW_RENDER = "if (gameId === 'tabu')     return <TabuGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;"
assert OLD_RENDER in content, "TabuGame render not found"
content = content.replace(OLD_RENDER, NEW_RENDER, 1)

# ── 3. Remove tabu from Csapat "Ki rontott?" exclusion ──
OLD_EXCL = "currentGameId !== 'powerhour' && currentGameId !== 'ovfj' && currentGameId !== 'tabu' && ("
NEW_EXCL = "currentGameId !== 'powerhour' && currentGameId !== 'ovfj' && ("
assert OLD_EXCL in content, "Csapat tabu exclusion not found"
content = content.replace(OLD_EXCL, NEW_EXCL, 1)

# ── 4. Add tabu to Páros CTA exclusion (handles results itself) ──
OLD_PAROS = "currentGameId !== 'szamsor' && currentGameId !== 'reakcio' && currentGameId !== 'ritmus' && ("
NEW_PAROS = "currentGameId !== 'szamsor' && currentGameId !== 'reakcio' && currentGameId !== 'ritmus' && currentGameId !== 'tabu' && ("
assert OLD_PAROS in content, "Páros CTA exclusion not found"
content = content.replace(OLD_PAROS, NEW_PAROS, 1)

# ── 5. Replace TabuGame component: Páros, one round, both get point or both drink ──
OLD_COMPONENT = """// ── Tabu Szó ───────────────────────────────────────────────────────────────────
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
      onResult && onResult({ correct: true, playerName: challenger?.name||'', drinks:0, subtitle: 'Mindenki kitalálta — mindenki +1 pont!' });
      onAdvance && onAdvance({}, {});  // everyone gets +1 via result banner
    } else {
      onResult && onResult({ correct: false, playerName: challenger?.name||'', drinks:1, subtitle: 'Nem sikerült — mindenki iszik 1-et!' });
      onAdvance && onAdvance({}, {});
    }
  };

  if (phase === 'ready') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontSize:52 }}>🚫</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>{challenger?.name} magyaráz!</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>30 mp alatt el kell magyarázni a szót a 3 tiltott szó nélkül. Ha kitalálják — mindenki kap pontot, ha nem — mindenki iszik.</div>
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

NEW_COMPONENT = """// ── Tabu Szó (Páros) ───────────────────────────────────────────────────────────
function TabuGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
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
    const both = [challenger, opponent].filter(Boolean);
    const points = {};
    const drinks = {};
    both.forEach(p => { if (won) points[p.id] = 1; else drinks[p.id] = 1; });
    if (won) {
      onResult && onResult({ correct: true, playerName: '', drinks: 0, subtitle: (challenger?.name||'') + ' & ' + (opponent?.name||'') + ' — mindkettő +1 pont!' });
    } else {
      onResult && onResult({ correct: false, playerName: '', drinks: 1, subtitle: (challenger?.name||'') + ' & ' + (opponent?.name||'') + ' — mindkettő iszik 1-et!' });
    }
    onAdvance && onAdvance(drinks, points);
  };

  if (phase === 'ready') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontSize:52 }}>🚫</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, textAlign:'center' }}>
        {challenger?.name} magyaráz — {opponent?.name} talál!
      </div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>30 mp, 3 tiltott szó nélkül. Ha sikerül — mindkettő +1 pont, ha nem — mindkettő iszik.</div>
      <button onClick={start} style={{ width:'100%', padding:'16px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>Start!</button>
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
        <button onClick={() => handleResult(true)} style={{ flex:1, padding:'14px 0', background:T.mint, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✓ Kitalálta!</button>
        <button onClick={() => handleResult(false)} style={{ flex:1, padding:'14px 0', background:T.coral, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✗ Nem / Szabálysértés</button>
      </div>
    </div>
  );
}"""

assert OLD_COMPONENT in content, "TabuGame component not found"
content = content.replace(OLD_COMPONENT, NEW_COMPONENT, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.171 ready")
