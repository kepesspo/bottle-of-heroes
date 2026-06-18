#!/usr/bin/env python3
"""patch_9_156.py — Matek: nincs Sikerült gomb; SzamSorrend: párbaj mód Start gombbal"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.155';" in content
content = content.replace("const APP_VERSION = 'v9.155';", "const APP_VERSION = 'v9.156';")

# ── 1. Matek: kizárás a Sikerült/Nem sikerült CTA gombok alól ──
OLD_CTA = "currentGameId !== 'otdolog' && currentGameId !== 'sohanem' && currentGameId !== 'zene' && currentGameId !== 'uveg'"
NEW_CTA = "currentGameId !== 'otdolog' && currentGameId !== 'sohanem' && currentGameId !== 'zene' && currentGameId !== 'uveg' && currentGameId !== 'matek'"
assert OLD_CTA in content, "CTA exclusion not found"
content = content.replace(OLD_CTA, NEW_CTA, 1)

# ── 2. Szám sorrend: category Egyéni → Páros, desc update ──
OLD_SZAMSOR_GAME = "{ id:'szamsor',  roundTime:'fast', name:'Szám Sorrend',     difficulty:'közepes', category:'Egyéni', emoji:'🔢', img:IMGS['szamsor_icon.png'], symbol:IMGS['szamsor_symbol.png'], color:'#3B82F6', desc:'Számok jelennek meg szétszórva a képernyőn. Koppints rájuk sorrendben 1-től 9-ig a lehető leggyorsabban. Az app méri az időt. Leglassabb a csoportban iszik.' },"
NEW_SZAMSOR_GAME = "{ id:'szamsor',  roundTime:'fast', name:'Szám Sorrend',     difficulty:'közepes', category:'Páros',  emoji:'🔢', img:IMGS['szamsor_icon.png'], symbol:IMGS['szamsor_symbol.png'], color:'#3B82F6', desc:'Párbaj! Mindkét játékos külön koppintja sorrendben 1-től 9-ig a számokat. Az app összehasonlítja az időt — a lassabb iszik.' },"
assert OLD_SZAMSOR_GAME in content, "szamsor game def not found"
content = content.replace(OLD_SZAMSOR_GAME, NEW_SZAMSOR_GAME, 1)

# ── 3. Szam sorrend megjelenítés: átváltás a PlayScreen-ben Páros-ra ──
OLD_SZAMSOR_RENDER = "  if (gameId === 'szamsor')  return <SzamsorGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;"
NEW_SZAMSOR_RENDER = "  if (gameId === 'szamsor')  return <SzamsorGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;"
assert OLD_SZAMSOR_RENDER in content, "szamsor render not found"
content = content.replace(OLD_SZAMSOR_RENDER, NEW_SZAMSOR_RENDER, 1)

# ── 4. SzamsorGame: teljes átírás párbaj módra ──
OLD_SZAMSOR_FN = """// ── Szám Sorrend ───────────────────────────────────────────────────────────────
function SzamsorGame({ gameIdx, challenger, onAdvance, onResult }) {
  const COUNT = 9;
  const genPositions = (idx) => {
    const s = (idx * 2654435761 + 1013904223) >>> 0;
    const rng = (seed, i) => { let x = (seed ^ (i * 2246822519 + 3266489917)) >>> 0; x ^= x<<13; x ^= x>>17; x ^= x<<5; return (x>>>0)/4294967296; };
    const positions = [];
    for (let i = 0; i < COUNT; i++) {
      let x, y, attempts = 0;
      do {
        x = 8 + rng(s, i*3+attempts)*78;
        y = 8 + rng(s, i*3+attempts+1)*70;
        attempts++;
      } while (positions.some(p => Math.abs(p.x-x)<14 && Math.abs(p.y-y)<12) && attempts < 20);
      positions.push({ num: i+1, x, y });
    }
    return positions;
  };

  const [positions] = useState(() => genPositions(gameIdx));
  const [next, setNext] = useState(1);
  const [startTime] = useState(() => Date.now());
  const [elapsed, setElapsed] = useState(0);
  const [done, setDone] = useState(false);
  const advancedRef = useRef(false);
  const ivRef = useRef(null);

  useEffect(() => {
    ivRef.current = setInterval(() => setElapsed(Date.now() - startTime), 80);
    return () => clearInterval(ivRef.current);
  }, []);

  const tap = (num) => {
    if (num !== next || done) return;
    if (next === COUNT) {
      clearInterval(ivRef.current);
      const ms = Date.now() - startTime;
      setElapsed(ms);
      setDone(true);
      if (!advancedRef.current) {
        advancedRef.current = true;
        const sec = (ms/1000).toFixed(2);
        onResult && onResult({ correct: true, playerName: challenger?.name||'', drinks:0, subtitle: `${challenger?.name||''} — ${sec} másodperc!` });
        onAdvance && onAdvance({}, {});
      }
    } else {
      setNext(n => n+1);
    }
  };

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Következő: <span style={{ color:T.mint, fontSize:18 }}>{done ? '✓' : next}</span></div>
        <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:18, color: done ? T.mint : T.ink }}>{(elapsed/1000).toFixed(done?2:1)}s</div>
      </div>
      <div style={{ position:'relative', width:'100%', paddingBottom:'85%', background:T.surfaceMuted, borderRadius:20, overflow:'hidden' }}>
        {positions.map(({ num, x, y }) => {
          const tapped = num < next;
          const isNext = num === next;
          return (
            <div key={num} onClick={() => tap(num)}
              style={{ position:'absolute', left:x+'%', top:y+'%', width:44, height:44, borderRadius:14, background: tapped ? T.mint : isNext ? '#1B2340' : T.surface, border: isNext ? `2.5px solid ${T.mint}` : tapped ? 'none' : `1.5px solid rgba(20,30,50,0.1)`, display:'grid', placeItems:'center', cursor: tapped||done ? 'default' : 'pointer', transform:'translate(-50%,-50%)', boxShadow: isNext ? `0 0 14px ${T.mint}88` : T.shadow, transition:'background .15s', userSelect:'none', WebkitUserSelect:'none' }}>
              <span style={{ fontFamily:'monospace', fontWeight:900, fontSize:16, color: tapped ? '#fff' : isNext ? '#fff' : T.ink }}>{tapped ? '✓' : num}</span>
            </div>
          );
        })}
      </div>
      {done && (
        <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:20, color:T.mint }}>
          🎉 {(elapsed/1000).toFixed(2)} másodperc!
        </div>
      )}
    </div>
  );
}"""

NEW_SZAMSOR_FN = """// ── Szám Sorrend (Párbaj) ─────────────────────────────────────────────────────
function SzamsorGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  const COUNT = 9;
  const genPositions = (seed) => {
    const s = (seed * 2654435761 + 1013904223) >>> 0;
    const rng = (i) => { let x = (s ^ (i * 2246822519 + 3266489917)) >>> 0; x ^= x<<13; x ^= x>>17; x ^= x<<5; return (x>>>0)/4294967296; };
    const positions = [];
    for (let i = 0; i < COUNT; i++) {
      let x, y, attempts = 0;
      do {
        x = 8 + rng(i*3+attempts)*78;
        y = 8 + rng(i*3+attempts+1)*70;
        attempts++;
      } while (positions.some(p => Math.abs(p.x-x)<14 && Math.abs(p.y-y)<12) && attempts < 20);
      positions.push({ num: i+1, x, y });
    }
    return positions;
  };

  // phase: 'intro1' | 'playing1' | 'done1' | 'intro2' | 'playing2' | 'result'
  const [phase, setPhase] = useState('intro1');
  const [p1Time, setP1Time] = useState(null);
  const [p2Time, setP2Time] = useState(null);
  const [positions1] = useState(() => genPositions(gameIdx));
  const [positions2] = useState(() => genPositions(gameIdx + 99991));
  const [next, setNext] = useState(1);
  const [startTime, setStartTime] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const ivRef = useRef(null);
  const advancedRef = useRef(false);

  const currentPlayer = phase.includes('1') ? challenger : opponent;
  const currentPositions = phase.includes('1') ? positions1 : positions2;

  useEffect(() => {
    if (phase === 'playing1' || phase === 'playing2') {
      const t0 = Date.now();
      setStartTime(t0);
      setElapsed(0);
      ivRef.current = setInterval(() => setElapsed(Date.now() - t0), 80);
      return () => clearInterval(ivRef.current);
    }
  }, [phase]);

  const tap = (num) => {
    if ((phase !== 'playing1' && phase !== 'playing2') || num !== next) return;
    if (next === COUNT) {
      clearInterval(ivRef.current);
      const ms = Date.now() - startTime;
      setElapsed(ms);
      if (phase === 'playing1') {
        setP1Time(ms);
        setPhase('done1');
      } else {
        setP2Time(ms);
        setPhase('result');
      }
      setNext(1);
    } else {
      setNext(n => n+1);
    }
  };

  // When result phase kicks in, call callbacks
  useEffect(() => {
    if (phase !== 'result' || advancedRef.current) return;
    if (p1Time === null || p2Time === null) return;
    advancedRef.current = true;
    const p1Name = challenger?.name || 'Kihívó';
    const p2Name = opponent?.name || 'Ellenfél';
    const p1sec = (p1Time/1000).toFixed(2);
    const p2sec = (p2Time/1000).toFixed(2);
    const p1Won = p1Time <= p2Time;
    const winner = p1Won ? challenger : opponent;
    const loser  = p1Won ? opponent  : challenger;
    const sub = `${p1Name}: ${p1sec}s — ${p2Name}: ${p2sec}s`;
    onResult && onResult({ correct: p1Won, playerName: loser?.name||'', drinks:1, subtitle: sub });
    onAdvance && onAdvance(
      loser  ? {[loser.id]:1}  : {},
      winner ? {[winner.id]:1} : {}
    );
  }, [phase, p1Time, p2Time]);

  const done = phase === 'playing1' || phase === 'playing2' ? false : (phase==='done1' || phase==='result');

  const renderBoard = () => (
    <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>
          Következő: <span style={{ color:T.mint, fontSize:18 }}>{next <= COUNT ? next : '✓'}</span>
        </div>
        <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:18, color: next > COUNT ? T.mint : T.ink }}>
          {(elapsed/1000).toFixed(next > COUNT ? 2 : 1)}s
        </div>
      </div>
      <div style={{ position:'relative', width:'100%', paddingBottom:'85%', background:T.surfaceMuted, borderRadius:20, overflow:'hidden' }}>
        {currentPositions.map(({ num, x, y }) => {
          const tapped = num < next;
          const isNext = num === next;
          return (
            <div key={num} onClick={() => tap(num)}
              style={{ position:'absolute', left:x+'%', top:y+'%', width:44, height:44, borderRadius:14, background: tapped ? T.mint : isNext ? '#1B2340' : T.surface, border: isNext ? `2.5px solid ${T.mint}` : tapped ? 'none' : `1.5px solid rgba(20,30,50,0.1)`, display:'grid', placeItems:'center', cursor: tapped ? 'default' : 'pointer', transform:'translate(-50%,-50%)', boxShadow: isNext ? `0 0 14px ${T.mint}88` : T.shadow, transition:'background .15s', userSelect:'none', WebkitUserSelect:'none' }}>
              <span style={{ fontFamily:'monospace', fontWeight:900, fontSize:16, color: tapped ? '#fff' : isNext ? '#fff' : T.ink }}>{tapped ? '✓' : num}</span>
            </div>
          );
        })}
      </div>
    </div>
  );

  if (phase === 'intro1') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:20, padding:'16px 0' }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink, textAlign:'center' }}>
        {challenger?.name || 'Kihívó'} jön
      </div>
      <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center' }}>
        Koppints 1-től 9-ig a lehető leggyorsabban!
      </div>
      <button onClick={() => setPhase('playing1')} style={{ padding:'16px 40px', background:T.mint, color:'#fff', border:'none', borderRadius:16, fontFamily:T.font, fontWeight:800, fontSize:18, cursor:'pointer', boxShadow:T.shadowLift }}>
        ▶ Start
      </button>
    </div>
  );

  if (phase === 'playing1') return renderBoard();

  if (phase === 'done1') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:20, padding:'16px 0' }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.mint, textAlign:'center' }}>
        {challenger?.name || 'Kihívó'}: {(p1Time/1000).toFixed(2)}s ✓
      </div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink, textAlign:'center' }}>
        {opponent?.name || 'Ellenfél'} következik
      </div>
      <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center' }}>
        Koppints 1-től 9-ig a lehető leggyorsabban!
      </div>
      <button onClick={() => setPhase('playing2')} style={{ padding:'16px 40px', background:T.mint, color:'#fff', border:'none', borderRadius:16, fontFamily:T.font, fontWeight:800, fontSize:18, cursor:'pointer', boxShadow:T.shadowLift }}>
        ▶ Start
      </button>
    </div>
  );

  if (phase === 'playing2') return renderBoard();

  // result phase — show summary while callbacks fire
  const p1Won = p1Time !== null && p2Time !== null && p1Time <= p2Time;
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'16px 0' }}>
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'20px 16px', boxShadow:T.shadow }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.ink }}>{challenger?.name || 'Kihívó'}</div>
          <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:20, color: p1Won ? T.mint : T.coral }}>{p1Time !== null ? (p1Time/1000).toFixed(2)+'s' : '—'}</div>
        </div>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.ink }}>{opponent?.name || 'Ellenfél'}</div>
          <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:20, color: !p1Won ? T.mint : T.coral }}>{p2Time !== null ? (p2Time/1000).toFixed(2)+'s' : '—'}</div>
        </div>
      </div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.mint, textAlign:'center' }}>
        🏆 {p1Won ? (challenger?.name||'Kihívó') : (opponent?.name||'Ellenfél')} nyert!
      </div>
    </div>
  );
}"""

assert OLD_SZAMSOR_FN in content, "SzamsorGame not found"
content = content.replace(OLD_SZAMSOR_FN, NEW_SZAMSOR_FN, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.156 ready")
