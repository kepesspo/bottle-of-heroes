import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Scenario cta: remove Nem sikerült/Megvan for anagramma + ringfire ──────
html = html.replace(
    "  anagramma: { prompt:'4 betű → rakj ki egy értelmes szót 5 mp alatt!', cta:['Nem sikerült','Megvan!'] },",
    "  anagramma: { prompt:'4 betű → rakj ki egy értelmes szót 5 mp alatt!', cta:[] },",
    1
)
html = html.replace(
    "  ringfire:  { prompt:'Húzz egy lapot — csináld meg a leírást!', cta:['Nem sikerült','Megúsztam!'] },",
    "  ringfire:  { prompt:'Húzz egy lapot — csináld meg a leírást!', cta:[] },",
    1
)

# ── 2. PlayScreen: only show Egyéni cta when cta array non-empty ───────────────
html = html.replace(
    "      {currentGame.category === 'Egyéni' && (",
    "      {currentGame.category === 'Egyéni' && scenario.cta.length > 0 && (",
    1
)

# ── 3. Replace AnagrammaGame ───────────────────────────────────────────────────
NEW_ANAGRAMMA = r"""function AnagrammaGame({ gameIdx, onAdvance }) {
  const WORDS = [
    'ALMA','BÉKA','KERT','BOLT','PARK','VERS','FILM','HOLD',
    'KARD','BORS','GOMB','TALP','RÉPA','AJTÓ','AUTÓ','ÉLET',
    'KÁVÉ','RÓKA','ÉNEK','PART','BIKA','HIBA','IKER','FOLT',
    'RÉGI','TELI','EPER','KEFE','VÉGE','KAPA',
  ];
  const TILE_COLORS = ['#4A90D9','#50C882','#F4A4A0','#F0C840'];

  const word = WORDS[gameIdx % WORDS.length];

  const shuffled = React.useMemo(() => {
    const arr = word.split('');
    let s = (gameIdx * 2654435761) >>> 0;
    const rng = () => { s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s >>> 0; };
    for (let i = arr.length - 1; i > 0; i--) {
      const j = rng() % (i + 1);
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    if (arr.join('') === word && arr.length > 1) [arr[0], arr[1]] = [arr[1], arr[0]];
    return arr;
  }, [gameIdx]);

  const [phase, setPhase] = React.useState('hidden'); // hidden | playing | won | lost
  const [pressed, setPressed] = React.useState([]); // tile indices tapped in order
  const [timeLeft, setTimeLeft] = React.useState(5);
  const [wrongFlash, setWrongFlash] = React.useState(false);
  const flashRef = React.useRef(false);
  const ivRef = React.useRef(null);

  React.useEffect(() => {
    setPhase('hidden'); setPressed([]); setTimeLeft(5); setWrongFlash(false);
    flashRef.current = false;
    clearInterval(ivRef.current);
    return () => clearInterval(ivRef.current);
  }, [gameIdx]);

  const startCountdown = () => {
    clearInterval(ivRef.current);
    const endTime = Date.now() + 5000;
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (endTime - Date.now()) / 1000);
      setTimeLeft(parseFloat(rem.toFixed(1)));
      if (rem <= 0) { clearInterval(ivRef.current); setPhase('lost'); }
    }, 80);
  };

  const startGame = () => {
    setPhase('playing'); setPressed([]); setTimeLeft(5); setWrongFlash(false);
    flashRef.current = false;
    startCountdown();
  };

  const retry = () => {
    setPressed([]); setTimeLeft(5); setWrongFlash(false);
    flashRef.current = false;
    setPhase('playing');
    startCountdown();
  };

  const handleTap = (idx) => {
    if (phase !== 'playing' || pressed.includes(idx) || flashRef.current) return;
    const expected = word[pressed.length];
    if (shuffled[idx] === expected) {
      const next = [...pressed, idx];
      setPressed(next);
      if (next.length === word.length) {
        clearInterval(ivRef.current);
        setPhase('won');
      }
    } else {
      flashRef.current = true;
      setWrongFlash(true);
      setTimeout(() => { setWrongFlash(false); setPressed([]); flashRef.current = false; }, 350);
    }
  };

  const timerColor = timeLeft > 3 ? '#50C882' : timeLeft > 1.5 ? '#F0C840' : '#F4704A';
  const R = 34, circ = 2 * Math.PI * R;

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14 }}>

      {/* Arc timer */}
      {phase === 'playing' && (
        <div style={{ position:'relative', width:76, height:76 }}>
          <svg width={76} height={76} style={{ transform:'rotate(-90deg)' }}>
            <circle cx={38} cy={38} r={R} fill="none" stroke="rgba(0,0,0,0.09)" strokeWidth={6} />
            <circle cx={38} cy={38} r={R} fill="none" stroke={timerColor}
              strokeWidth={6} strokeLinecap="round"
              strokeDasharray={`${circ}`} strokeDashoffset={`${circ*(1-timeLeft/5)}`}
              style={{ transition:'stroke-dashoffset 0.1s linear, stroke 0.3s' }} />
          </svg>
          <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
            <span style={{ fontFamily:'monospace', fontWeight:900, fontSize:22, color:timerColor, lineHeight:1 }}>{Math.ceil(timeLeft)}</span>
            <span style={{ fontFamily:T.font, fontSize:9, color:T.inkSoft }}>mp</span>
          </div>
        </div>
      )}

      {/* Word-building slots */}
      {phase !== 'hidden' && (
        <div style={{ display:'flex', gap:8 }}>
          {word.split('').map((_, i) => (
            <div key={i} style={{
              width:38, height:44, borderRadius:8,
              background: i < pressed.length ? 'rgba(80,200,130,0.18)' : 'rgba(0,0,0,0.07)',
              border: `2px solid ${i < pressed.length ? '#50C882' : 'rgba(0,0,0,0.12)'}`,
              display:'flex', alignItems:'center', justifyContent:'center',
              fontFamily:'Georgia,serif', fontWeight:800, fontSize:20, color:'#1B2340',
              transition:'all .12s',
            }}>
              {i < pressed.length ? shuffled[pressed[i]] : ''}
            </div>
          ))}
        </div>
      )}

      {/* Tiles */}
      {phase === 'hidden' ? (
        <div style={{ display:'flex', gap:10 }}>
          {word.split('').map((_, i) => (
            <div key={i} style={{ width:58, height:64, borderRadius:10, background:'#1B2340', boxShadow:'0 4px 0 rgba(0,0,0,0.22)', display:'flex', alignItems:'center', justifyContent:'center' }}>
              <span style={{ fontSize:26, color:'rgba(255,255,255,0.25)' }}>?</span>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ display:'flex', gap:10 }}>
          {shuffled.map((letter, i) => {
            const used = pressed.includes(i);
            return (
              <div key={i} onClick={() => handleTap(i)} style={{
                width:58, height:64, borderRadius:10,
                background: used ? '#C8CCD8' : wrongFlash ? '#F47060' : TILE_COLORS[i % TILE_COLORS.length],
                boxShadow: used ? 'none' : `0 4px 0 rgba(0,0,0,0.18)`,
                display:'flex', alignItems:'center', justifyContent:'center',
                fontFamily:'Georgia,serif', fontWeight:900, fontSize:30, color:'#fff',
                opacity: used ? 0.45 : 1,
                transform: used ? 'translateY(4px)' : 'none',
                cursor: used || phase !== 'playing' ? 'default' : 'pointer',
                userSelect:'none', transition:'all .1s',
              }}>
                {letter}
              </div>
            );
          })}
        </div>
      )}

      {/* Dot indicators */}
      <div style={{ display:'flex', gap:6 }}>
        {shuffled.map((_, i) => (
          <div key={i} style={{ width:7, height:7, borderRadius:'50%', background:TILE_COLORS[i % TILE_COLORS.length], opacity:0.6 }} />
        ))}
      </div>

      {/* Hidden phase: Start button */}
      {phase === 'hidden' && (
        <button onClick={startGame} style={{ padding:'12px 32px', background:`${T.mint}22`, border:`2px solid ${T.mint}`, color:T.mint, fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:14, cursor:'pointer' }}>
          ▶ Start!
        </button>
      )}

      {/* Won */}
      {phase === 'won' && (
        <div style={{ textAlign:'center', animation:'popIn .3s' }}>
          <div style={{ fontSize:32 }}>🎉</div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:17, color:T.mint, marginTop:4 }}>Megvan! A szó: {word}</div>
        </div>
      )}

      {/* Lost */}
      {phase === 'lost' && (
        <div style={{ textAlign:'center', animation:'popIn .3s' }}>
          <div style={{ fontSize:32 }}>⏱️</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.coral, marginTop:4 }}>Idő lejárt! A szó: <strong>{word}</strong></div>
          <button onClick={retry} style={{ marginTop:10, padding:'9px 22px', background:`rgba(240,192,64,0.18)`, border:`2px solid #E0A030`, color:'#A06010', fontFamily:T.font, fontWeight:700, fontSize:14, borderRadius:12, cursor:'pointer' }}>
            🔄 Újra!
          </button>
        </div>
      )}

      {/* Tovább button (shown on won/lost) */}
      {(phase === 'won' || phase === 'lost') && (
        <button onClick={() => onAdvance && onAdvance({})} style={{ marginTop:4, padding:'12px 28px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, borderRadius:14, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
          Tovább →
        </button>
      )}
    </div>
  );
}"""

html = re.sub(
    r'function AnagrammaGame\(\{ gameIdx \}\) \{.*?\n\}(?=\n\nfunction RingFireGame)',
    NEW_ANAGRAMMA, html, flags=re.DOTALL
)

# ── 4. Replace RingFireGame ────────────────────────────────────────────────────
NEW_RINGFIRE = r"""function RingFireGame({ gameIdx, onAdvance }) {
  const TASKS = {
    '2':  { title:'Choose 🫵',       desc:'Válassz valakit, aki iszik.' },
    '3':  { title:'Me 🙋',           desc:'Te iszol.' },
    '4':  { title:'Whore 💃',        desc:'Összes lány iszik.' },
    '5':  { title:'Thumb Master 👍', desc:'Te leszel a Thumb Master — bármikor ráteheted a hüvelykujjad az asztalra, az utolsó aki követi, iszik.' },
    '6':  { title:'Dicks 🕺',        desc:'Összes fiú iszik.' },
    '7':  { title:'Heaven ☝️',       desc:'Fel kell mutatni az égre — az utolsó aki követi, iszik.' },
    '8':  { title:'Mate 🤝',         desc:'Válassz valakit, aki veled iszik.' },
    '9':  { title:'Rhyme 🎤',        desc:'Mondj egy szót — mindenki sorban rímelt rá. Aki megakad, iszik.' },
    '10': { title:'Categories 🗂️',  desc:'Mondj egy kategóriát — mindenki mond egyet. Aki megakad, iszik.' },
    'J':  { title:'Make a Rule 📜',  desc:'Hozz egy szabályt — aki megszegi, iszik.' },
    'Q':  { title:'Questions ❓',    desc:'Csak kérdésekkel szabad kommunikálni — aki állítást mond, iszik.' },
    'K':  { title:'Pour 👑',         desc:'Önts a poharadból a középső pohárba. Aki az utolsó Királyt húzza, megissza az egészet.' },
    'A':  { title:'Waterfall 🌊',    desc:'Mindenki elkezd inni — senki nem állhat meg amíg az Ász-húzó iszik.' },
  };

  const deck = React.useMemo(() => shuffleDeck(generateDeck(1)), []);

  const [phase, setPhase] = React.useState('choose'); // choose | reveal
  const [chosenIdx, setChosenIdx] = React.useState(null);

  React.useEffect(() => { setPhase('choose'); setChosenIdx(null); }, [gameIdx]);

  const pos1 = (gameIdx * 2) % deck.length;
  const pos2 = (gameIdx * 2 + 1) % deck.length;
  const cards = [deck[pos1], deck[pos2]];
  const remaining = Math.max(0, deck.length - pos1 - 2);

  const choose = (idx) => { setChosenIdx(idx); setPhase('reveal'); };

  const chosenCard = chosenIdx !== null ? cards[chosenIdx] : null;
  const task = chosenCard ? TASKS[chosenCard.value] : null;
  const isRed = chosenCard && SUIT_RED.has(chosenCard.suit);
  const cardColor = isRed ? '#CC2020' : '#141424';

  const CardBack = ({ onPick, label }) => (
    <div onClick={onPick} style={{
      width:118, height:164, borderRadius:14, background:'#1B2340',
      boxShadow:'0 6px 22px rgba(0,0,0,0.22)',
      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:8,
      cursor:'pointer', userSelect:'none', position:'relative',
      transition:'transform .12s', flexShrink:0,
    }}>
      <div style={{ position:'absolute', top:10, right:12, background:'rgba(255,255,255,0.12)', borderRadius:8, padding:'2px 8px' }}>
        <span style={{ fontFamily:'monospace', fontWeight:700, fontSize:11, color:'rgba(255,255,255,0.55)' }}>{label}</span>
      </div>
      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:44, color:'rgba(255,255,255,0.28)' }}>?</span>
      <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10, color:'rgba(255,255,255,0.35)', letterSpacing:'0.12em' }}>HÚZZ</span>
    </div>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14 }}>

      {/* Badges */}
      <div style={{ display:'flex', gap:8, width:'100%', justifyContent:'space-between' }}>
        <div style={{ padding:'5px 12px', borderRadius:10, background:'rgba(255,255,255,0.7)', fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkSoft, letterSpacing:'0.05em' }}>
          {phase === 'choose' ? 'VÁLASSZ LAPOT' : 'TE HÚZTAD'}
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:4, padding:'5px 12px', borderRadius:10, background:'rgba(255,255,255,0.7)', fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkSoft }}>
          <span style={{ fontSize:10 }}>⊞</span> {remaining} LAP MARADT
        </div>
      </div>

      {/* Choose: 2 face-down cards */}
      {phase === 'choose' && (
        <div style={{ display:'flex', gap:20, alignItems:'center' }}>
          <CardBack onPick={() => choose(0)} label="1" />
          <CardBack onPick={() => choose(1)} label="2" />
        </div>
      )}

      {/* Reveal: chosen card + task */}
      {phase === 'reveal' && chosenCard && (
        <>
          <div style={{ width:140, height:196, borderRadius:16, background:'#fff', boxShadow:'0 8px 28px rgba(0,0,0,0.16)', border:'1px solid rgba(0,0,0,0.07)', display:'flex', flexDirection:'column', padding:'12px 14px', position:'relative', flexShrink:0, animation:'popIn .35s' }}>
            <div style={{ fontFamily:'Georgia,serif', fontWeight:700, fontSize:36, color:cardColor, lineHeight:1 }}>{chosenCard.value}</div>
            <div style={{ fontFamily:'Georgia,serif', fontSize:26, color:cardColor, lineHeight:1.1 }}>{chosenCard.suit}</div>
            <div style={{ position:'absolute', bottom:14, left:'50%', transform:'translateX(-50%)', fontFamily:'Georgia,serif', fontSize:52, color:cardColor, lineHeight:1 }}>{chosenCard.suit}</div>
          </div>

          {task && (
            <div style={{ width:'100%', background:'#fff', borderRadius:18, padding:'16px 18px', boxShadow:'0 4px 16px rgba(0,0,0,0.10)', animation:'popIn .4s' }}>
              <div style={{ display:'inline-flex', alignItems:'center', gap:4, padding:'4px 10px', background:'rgba(249,115,22,0.12)', borderRadius:20, marginBottom:10 }}>
                <span>🔥</span>
                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:'#F97316', textTransform:'uppercase', letterSpacing:'0.08em' }}>FELADAT</span>
              </div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:18, color:T.ink, marginBottom:6 }}>{task.title}</div>
              <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, lineHeight:1.55 }}>{task.desc}</div>
            </div>
          )}

          <button onClick={() => onAdvance && onAdvance({})} style={{ padding:'12px 28px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, borderRadius:14, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
            Tovább →
          </button>
        </>
      )}
    </div>
  );
}"""

html = re.sub(
    r'function RingFireGame\(\{ gameIdx \}\) \{.*?\n\}(?=\n\nfunction GameContent)',
    NEW_RINGFIRE, html, flags=re.DOTALL
)

# ── 5. Add KoPapirGame before GameContent ──────────────────────────────────────
NEW_KOPAPIR = r"""function KoPapirGame({ gameIdx, players, onAdvance }) {
  const CHOICES = [
    { id:'kő',    label:'KŐ',    icon:'🗿', beats:'olló' },
    { id:'papír', label:'PAPÍR', icon:'📄', beats:'kő' },
    { id:'olló',  label:'OLLÓ',  icon:'✂️', beats:'papír' },
  ];

  const p1idx = gameIdx % Math.max(players.length, 1);
  const p2idx = (gameIdx + 1) % Math.max(players.length, 1);
  const p1 = players[p1idx];
  const p2 = players[p2idx];

  const [phase, setPhase] = React.useState('pick'); // pick | result
  const [myChoice, setMyChoice] = React.useState(null);
  const [oppChoice, setOppChoice] = React.useState(null);

  React.useEffect(() => { setPhase('pick'); setMyChoice(null); setOppChoice(null); }, [gameIdx]);

  const pick = (choice) => {
    if (phase !== 'pick') return;
    const opp = CHOICES[Math.floor(Math.random() * 3)];
    setMyChoice(choice); setOppChoice(opp); setPhase('result');
  };

  const result = React.useMemo(() => {
    if (!myChoice || !oppChoice) return null;
    if (myChoice.id === oppChoice.id) return 'draw';
    return myChoice.beats === oppChoice.id ? 'p1wins' : 'p2wins';
  }, [myChoice, oppChoice]);

  const proceed = () => {
    const dm = {};
    if (result === 'draw') { if(p1) dm[p1.id]=1; if(p2) dm[p2.id]=1; }
    else if (result === 'p2wins' && p1) dm[p1.id] = 1;
    else if (result === 'p1wins' && p2) dm[p2.id] = 1;
    onAdvance && onAdvance(dm);
  };

  const PlayerChip = ({ player, label }) => (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
      <div style={{ width:42, height:42, borderRadius:'50%', background:player?.color||T.coral, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>
        {(player?.name||'?').charAt(0).toUpperCase()}
      </div>
      <div style={{ fontFamily:T.font, fontWeight:700, fontSize:10, color:T.inkSoft, letterSpacing:'0.08em', textTransform:'uppercase' }}>{label}</div>
      <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color:T.ink, maxWidth:72, textAlign:'center', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{player?.name||'?'}</div>
    </div>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>

      {/* Players */}
      <div style={{ display:'flex', alignItems:'center', gap:16 }}>
        <PlayerChip player={p1} label="KIHÍVÓ" />
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:18, color:T.inkSoft }}>VS</div>
        <PlayerChip player={p2} label="ELLENFÉL" />
      </div>

      {/* Pick phase */}
      {phase === 'pick' && (
        <>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, fontWeight:600 }}>
            {p1?.name}, válassz!
          </div>
          <div style={{ display:'flex', gap:10 }}>
            {CHOICES.map(c => (
              <button key={c.id} onClick={() => pick(c)} style={{
                width:90, padding:'14px 0', borderRadius:16, border:`2px solid rgba(0,0,0,0.10)`,
                background:T.surface, boxShadow:T.shadow, cursor:'pointer',
                display:'flex', flexDirection:'column', alignItems:'center', gap:6,
                fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink,
              }}>
                <span style={{ fontSize:32 }}>{c.icon}</span>
                <span>{c.label}</span>
              </button>
            ))}
          </div>
        </>
      )}

      {/* Result phase */}
      {phase === 'result' && myChoice && oppChoice && (
        <>
          <div style={{ display:'flex', gap:16, alignItems:'center' }}>
            <div style={{ textAlign:'center' }}>
              <div style={{ fontSize:40 }}>{myChoice.icon}</div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, marginTop:4 }}>{myChoice.label}</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>{p1?.name}</div>
            </div>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.inkSoft }}>VS</div>
            <div style={{ textAlign:'center' }}>
              <div style={{ fontSize:40 }}>{oppChoice.icon}</div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, marginTop:4 }}>{oppChoice.label}</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>{p2?.name}</div>
            </div>
          </div>

          <div style={{ padding:'10px 20px', borderRadius:14, textAlign:'center', animation:'popIn .3s',
            background: result==='draw' ? `${T.yellow}18` : result==='p1wins' ? `${T.mint}18` : `${T.coral}18`,
            border: `2px solid ${result==='draw' ? T.yellow : result==='p1wins' ? T.mint : T.coral}` }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>
              {result === 'draw'
                ? `🤝 Döntetlen! Mindkettő iszik.`
                : result === 'p1wins'
                  ? `🏆 ${p1?.name} nyert! ${p2?.name} iszik.`
                  : `🏆 ${p2?.name} nyert! ${p1?.name} iszik.`}
            </div>
          </div>

          <button onClick={proceed} style={{ padding:'12px 28px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, borderRadius:14, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
            Tovább →
          </button>
        </>
      )}
    </div>
  );
}

"""

html = html.replace(
    'function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta, challenger, opponent }) {',
    NEW_KOPAPIR + 'function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta, challenger, opponent }) {',
    1
)

# ── 6. Update GameContent: pass onAdvance to anagramma/ringfire, add kopapir ──
html = html.replace(
    "  if (gameId === 'anagramma') return <AnagrammaGame key={gameIdx} gameIdx={gameIdx} />;",
    "  if (gameId === 'anagramma') return <AnagrammaGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;",
    1
)
html = html.replace(
    "  if (gameId === 'ringfire') return <RingFireGame key={gameIdx} gameIdx={gameIdx} />;",
    "  if (gameId === 'ringfire') return <RingFireGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;",
    1
)
html = html.replace(
    "  if (gameId === 'ringfire') return <RingFireGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;\n  return null;",
    "  if (gameId === 'ringfire') return <RingFireGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;\n  if (gameId === 'kopapir') return <KoPapirGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  return null;",
    1
)

# ── 7. Version bump ────────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.20 · DNR · 2026.05.31 01:00',
    'Verzió 5.21 · DNR · 2026.05.31 02:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
