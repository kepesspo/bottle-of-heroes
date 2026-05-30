import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Insert AnagrammaGame + RingFireGame before GameContent ─────────────────

NEW_GAMES = r"""function AnagrammaGame({ gameIdx }) {
  const WORDS = [
    'ALMA','BÉKA','KERT','BOLT','PARK','VERS','FILM','HOLD',
    'KARD','BORS','GOMB','TALP','RÉPA','AJTÓ','AUTÓ','ÉLET',
    'KÁVÉ','RÓKA','ÉNEK','PART','BIKA','HIBA','IKER','FOLT',
    'RÉGI','TELI','EPER','KEFE','VÉGE','KAPA',
  ];
  const TILE_COLORS = ['#4A90D9','#50C882','#F4A4A0','#F0C840'];

  const [phase, setPhase] = React.useState('ready');
  const [timeLeft, setTimeLeft] = React.useState(5);
  const ivRef = React.useRef(null);
  const startRef = React.useRef(null);

  React.useEffect(() => {
    setPhase('ready'); setTimeLeft(5);
    clearInterval(ivRef.current);
    return () => clearInterval(ivRef.current);
  }, [gameIdx]);

  const word = WORDS[gameIdx % WORDS.length];
  const letters = React.useMemo(() => {
    const arr = word.split('');
    let seed = gameIdx * 2654435761;
    const rng = () => { seed ^= seed << 13; seed ^= seed >> 17; seed ^= seed << 5; return Math.abs(seed); };
    for (let i = arr.length - 1; i > 0; i--) {
      const j = rng() % (i + 1);
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    // ensure shuffled (if same as word, swap first two)
    if (arr.join('') === word && arr.length > 1) [arr[0], arr[1]] = [arr[1], arr[0]];
    return arr;
  }, [gameIdx]);

  const start = () => {
    setPhase('running'); setTimeLeft(5);
    startRef.current = Date.now() + 5000;
    clearInterval(ivRef.current);
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (startRef.current - Date.now()) / 1000);
      setTimeLeft(parseFloat(rem.toFixed(1)));
      if (rem <= 0) { clearInterval(ivRef.current); setPhase('done'); }
    }, 80);
  };

  const R = 38, CX = 44, CY = 44;
  const circ = 2 * Math.PI * R;
  const progress = phase === 'running' ? timeLeft / 5 : phase === 'ready' ? 1 : 0;
  const dashOffset = circ * (1 - progress);
  const timerColor = timeLeft > 3 ? '#50C882' : timeLeft > 1.5 ? '#F0C840' : '#F4704A';

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:18 }}>

      {/* Circular countdown timer */}
      <div style={{ position:'relative', width:88, height:88 }}>
        <svg width={88} height={88} style={{ transform:'rotate(-90deg)' }}>
          <circle cx={CX} cy={CY} r={R} fill="none" stroke="rgba(0,0,0,0.09)" strokeWidth={7} />
          <circle cx={CX} cy={CY} r={R} fill="none" stroke={timerColor}
            strokeWidth={7} strokeLinecap="round"
            strokeDasharray={`${circ}`} strokeDashoffset={`${dashOffset}`}
            style={{ transition: phase==='running' ? 'stroke-dashoffset 0.1s linear, stroke 0.3s' : 'none' }} />
        </svg>
        <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
          {phase === 'ready' && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>KÉSZ?</span>}
          {phase === 'running' && <>
            <span style={{ fontFamily:'monospace', fontWeight:900, fontSize:26, color:timerColor, lineHeight:1 }}>{Math.ceil(timeLeft)}</span>
            <span style={{ fontFamily:T.font, fontSize:9, color:T.inkSoft }}>mp</span>
          </>}
          {phase === 'done' && <span style={{ fontSize:22 }}>⏱️</span>}
        </div>
      </div>

      {/* Letter tiles */}
      <div style={{ display:'flex', gap:10 }}>
        {letters.map((letter, i) => (
          <div key={i} style={{
            width:58, height:64, borderRadius:10,
            background: TILE_COLORS[i % TILE_COLORS.length],
            boxShadow:`0 4px 0 rgba(0,0,0,0.18), 0 6px 16px rgba(0,0,0,0.10)`,
            display:'flex', alignItems:'center', justifyContent:'center',
            fontFamily:'Georgia,serif', fontWeight:900, fontSize:30, color:'#fff',
            textShadow:'0 2px 4px rgba(0,0,0,0.2)', userSelect:'none',
          }}>
            {letter}
          </div>
        ))}
      </div>

      {/* Dot indicators */}
      <div style={{ display:'flex', gap:6 }}>
        {letters.map((_, i) => (
          <div key={i} style={{ width:8, height:8, borderRadius:'50%', background:TILE_COLORS[i % TILE_COLORS.length], opacity:0.65 }} />
        ))}
      </div>

      {phase === 'running' && (
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:timerColor, textTransform:'uppercase', letterSpacing:'0.08em' }}>
          {Math.ceil(timeLeft)} MÁSODPERC
        </div>
      )}

      {phase === 'done' && (
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.inkSoft, textAlign:'center' }}>
          Idő lejárt! · A szó: <span style={{ color:T.ink, fontWeight:900 }}>{word}</span>
        </div>
      )}

      {phase === 'ready' && (
        <button onClick={start} style={{ padding:'12px 32px', background:`${T.mint}22`, border:`2px solid ${T.mint}`, color:T.mint, fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:14, cursor:'pointer' }}>
          ▶ Start!
        </button>
      )}
    </div>
  );
}

function RingFireGame({ gameIdx }) {
  const TASKS = {
    '2':  { title:'Choose 🫵',   desc:'Válassz valakit, aki iszik.' },
    '3':  { title:'Me 🙋',       desc:'Te iszol.' },
    '4':  { title:'Whore 💃',    desc:'Összes lány iszik.' },
    '5':  { title:'Thumb Master 👍', desc:'Te leszel a Thumb Master — bármikor ráteheted a hüvelykujjad az asztalra, az utolsó aki követi, iszik.' },
    '6':  { title:'Dicks 🕺',    desc:'Összes fiú iszik.' },
    '7':  { title:'Heaven ☝️',   desc:'Fel kell mutatni az égre — az utolsó aki követi, iszik.' },
    '8':  { title:'Mate 🤝',     desc:'Válassz valakit, aki veled iszik.' },
    '9':  { title:'Rhyme 🎤',    desc:'Mondj egy szót — mindenki sorban rímelt rá. Aki megakad, iszik.' },
    '10': { title:'Categories 🗂️', desc:'Mondj egy kategóriát — mindenki mond egyet. Aki megakad, iszik.' },
    'J':  { title:'Make a Rule 📜', desc:'Hozz egy szabályt — aki megszegi, iszik.' },
    'Q':  { title:'Questions ❓', desc:'Csak kérdésekkel szabad kommunikálni — aki állítást mond, iszik.' },
    'K':  { title:'Pour 👑',     desc:'Önts a poharadból a középső pohárba. Aki az utolsó Királyt húzza, megissza az egészet.' },
    'A':  { title:'Waterfall 🌊', desc:'Mindenki elkezd inni — senki nem állhat meg amíg az Ász-húzó iszik.' },
  };

  const deck = React.useMemo(() => shuffleDeck(generateDeck(1)), []);
  const pos = gameIdx % deck.length;
  const card = deck[pos];
  const remaining = deck.length - pos - 1;
  const task = card ? TASKS[card.value] : null;
  const isRed = card && SUIT_RED.has(card.suit);
  const cardColor = isRed ? '#CC2020' : '#141424';

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14 }}>

      {/* Badge row */}
      <div style={{ display:'flex', gap:8, width:'100%', justifyContent:'space-between' }}>
        <div style={{ padding:'5px 12px', borderRadius:10, background:'rgba(255,255,255,0.7)', fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkSoft, letterSpacing:'0.05em' }}>
          TE HÚZTAD
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:4, padding:'5px 12px', borderRadius:10, background:'rgba(255,255,255,0.7)', fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkSoft }}>
          <span style={{ fontSize:10 }}>⊞</span> {remaining} LAP MARADT
        </div>
      </div>

      {/* Large playing card */}
      {card && (
        <div style={{ width:140, height:196, borderRadius:16, background:'#fff', boxShadow:'0 8px 28px rgba(0,0,0,0.16)', border:'1px solid rgba(0,0,0,0.07)', display:'flex', flexDirection:'column', padding:'12px 14px', position:'relative', flexShrink:0 }}>
          <div style={{ fontFamily:'Georgia,serif', fontWeight:700, fontSize:36, color:cardColor, lineHeight:1 }}>{card.value}</div>
          <div style={{ fontFamily:'Georgia,serif', fontSize:26, color:cardColor, lineHeight:1.1 }}>{card.suit}</div>
          <div style={{ position:'absolute', bottom:14, left:'50%', transform:'translateX(-50%)', fontFamily:'Georgia,serif', fontSize:52, color:cardColor, lineHeight:1 }}>{card.suit}</div>
        </div>
      )}

      {/* Task card */}
      {task && (
        <div style={{ width:'100%', background:'#fff', borderRadius:18, padding:'16px 18px', boxShadow:'0 4px 16px rgba(0,0,0,0.10)' }}>
          <div style={{ display:'inline-flex', alignItems:'center', gap:4, padding:'4px 10px', background:'rgba(249,115,22,0.12)', borderRadius:20, marginBottom:10 }}>
            <span>🔥</span>
            <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:'#F97316', textTransform:'uppercase', letterSpacing:'0.08em' }}>FELADAT</span>
          </div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:18, color:T.ink, marginBottom:6 }}>{task.title}</div>
          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, lineHeight:1.55 }}>{task.desc}</div>
        </div>
      )}
    </div>
  );
}

"""

html = html.replace(
    'function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta }) {',
    NEW_GAMES + 'function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta }) {',
    1
)

# ── 2. Add anagramma + ringfire to GameContent router ─────────────────────────
html = html.replace(
    "  if (gameId === 'tapper') return <TapperGame key={gameIdx} gameIdx={gameIdx} />;",
    "  if (gameId === 'tapper') return <TapperGame key={gameIdx} gameIdx={gameIdx} />;\n  if (gameId === 'anagramma') return <AnagrammaGame key={gameIdx} gameIdx={gameIdx} />;\n  if (gameId === 'ringfire') return <RingFireGame key={gameIdx} gameIdx={gameIdx} />;",
    1
)

# ── 3. Version bump ────────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.18 · DNR · 2026.05.30 23:00',
    'Verzió 5.19 · DNR · 2026.05.31 00:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
