with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

import re

START = 'function RitmusGame({ gameIdx, players, challenger, opponent, onAdvance, onResult }) {'
END_MARKER = '\n// ── Mit Választanál'
assert START in src
si = src.index(START)
ei = src.index(END_MARKER, si)
OLD = src[si:ei]

NEW = '''function RitmusGame({ gameIdx, players, challenger, opponent, onAdvance, onResult }) {
  const GRID = 12;
  const DURATION = 30;
  const EMOJIS = ['🎯','⭐','🔥','💎','🎵','🍀','⚡','🎪','🦋','🎸','🎲','🚀'];
  const TRAP_EMOJI = '💀';
  const TRAP_CHANCE = 0.2;
  const [phase, setPhase] = useState('intro');
  const [timeLeft, setTimeLeft] = useState(DURATION);
  const [activeBtn, setActiveBtn] = useState(null);
  const [score1, setScore1] = useState(0);
  const [score2, setScore2] = useState(0);
  const [currentScore, setCurrentScore] = useState(0);
  const ivRef = useRef(null);
  const btnTimerRef = useRef(null);
  const spawnTimerRef = useRef(null);
  const advancedRef = useRef(false);
  const scoreRef = useRef(0);
  const endTimeRef = useRef(0);
  const startTimeRef = useRef(0);
  const isP2Ref = useRef(false);
  const score1Ref = useRef(0);
  const score2Ref = useRef(0);

  const p1 = challenger;
  const p2 = opponent || (players && players.find(p => p.id !== challenger?.id)) || null;

  useEffect(() => () => {
    clearInterval(ivRef.current);
    clearTimeout(btnTimerRef.current);
    clearTimeout(spawnTimerRef.current);
  }, []);

  const spawnNext = () => {
    if (Date.now() >= endTimeRef.current) return;
    const pos = Math.floor(Math.random() * GRID);
    const isTrap = Math.random() < TRAP_CHANCE;
    const emoji = isTrap ? TRAP_EMOJI : EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
    setActiveBtn({ pos, emoji, isTrap });
    const elapsed = Date.now() - startTimeRef.current;
    const progress = Math.min(1, elapsed / (DURATION * 1000));
    // FIX: min visible 380ms so it stays tappable at the end
    const visibleMs = Math.max(380, 900 - progress * 520) + Math.random() * 80;
    const gapMs = Math.max(60, 150 - progress * 90);
    btnTimerRef.current = setTimeout(() => {
      setActiveBtn(null);
      spawnTimerRef.current = setTimeout(spawnNext, gapMs);
    }, visibleMs);
  };

  const startRound = (isP2) => {
    scoreRef.current = 0;
    isP2Ref.current = isP2;
    setCurrentScore(0);
    setActiveBtn(null);
    setTimeLeft(DURATION);
    setPhase(isP2 ? 'p2playing' : 'p1playing');
    const endTime = Date.now() + DURATION * 1000;
    endTimeRef.current = endTime;
    startTimeRef.current = Date.now();
    clearInterval(ivRef.current);
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (endTime - Date.now()) / 1000);
      setTimeLeft(Math.ceil(rem));
      if (rem <= 0) {
        clearInterval(ivRef.current);
        clearTimeout(btnTimerRef.current);
        clearTimeout(spawnTimerRef.current);
        setActiveBtn(null);
        if (!isP2) {
          score1Ref.current = scoreRef.current;
          setScore1(scoreRef.current);
          setPhase('p1done');
        } else {
          score2Ref.current = scoreRef.current;
          setScore2(scoreRef.current);
          setPhase('done');
        }
      }
    }, 100);
    spawnTimerRef.current = setTimeout(spawnNext, 300);
  };

  useEffect(() => {
    if (phase === 'done') {
      const s1 = score1Ref.current, s2 = score2Ref.current;
      const diff = Math.abs(s1 - s2);
      const loser = s1 < s2 ? p1 : s2 < s1 ? p2 : null;
      const drinks = diff > 0 ? diff : 1;
      const dm = {};
      if (loser) dm[loser.id] = drinks;
      const subtitle = loser
        ? `${loser.name} iszik ${drinks} kortyt (${s1} vs ${s2})`
        : `Döntetlen! (${s1} vs ${s2}) — mindenki iszik 1-et`;
      if (!loser) { players?.forEach(p => { dm[p.id] = 1; }); }
      if (!advancedRef.current) {
        advancedRef.current = true;
        onResult && onResult({ correct: !loser, playerName: loser?.name || '', drinks, subtitle });
        onAdvance && onAdvance(dm, {});
      }
    }
  }, [phase]);

  const handleTap = (pos) => {
    if (!activeBtn || activeBtn.pos !== pos) return;
    clearTimeout(btnTimerRef.current);
    const wasTrap = activeBtn.isTrap;
    setActiveBtn(wasTrap ? { pos, emoji:'💥', isTrap:true, flash:true } : null);
    if (wasTrap) {
      scoreRef.current = Math.max(0, scoreRef.current - 1);
      setCurrentScore(scoreRef.current);
      spawnTimerRef.current = setTimeout(() => { setActiveBtn(null); setTimeout(spawnNext, 80); }, 300);
    } else {
      setActiveBtn(null);
      scoreRef.current += 1;
      setCurrentScore(scoreRef.current);
      spawnTimerRef.current = setTimeout(spawnNext, 100);
    }
  };

  const gridPositions = Array.from({ length: GRID });

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
    const PASTEL_COLORS = [
      '#F4B8A8','#F4CCA8','#A8D8C8','#C8B8E0',
      '#F4B8A8','#A8D8C8','#F4CCA8','#C8B8E0',
      '#C8D4F0','#C8B8E0','#C8D4F0','#A8D8C8',
    ];
    const rT = 20, circT = 2 * Math.PI * rT;
    const timerPctT = timeLeft / DURATION;
    return (
      <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
        <div style={{ display:'flex', justifyContent:'space-between', width:'100%', alignItems:'center' }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{currentPlayer?.name}</div>
          <svg width={48} height={48} viewBox="0 0 48 48">
            <circle cx={24} cy={24} r={rT} fill="none" stroke="rgba(20,30,50,0.1)" strokeWidth={3.5}/>
            <circle cx={24} cy={24} r={rT} fill="none" stroke={timeLeft <= 5 ? T.coral : T.mint} strokeWidth={3.5}
              strokeDasharray={circT} strokeDashoffset={circT * (1 - timerPctT)}
              strokeLinecap="round" transform="rotate(-90 24 24)" style={{transition:'stroke-dashoffset 0.1s, stroke 0.3s'}}/>
            <text x={24} y={29} textAnchor="middle" fontFamily={T.font} fontWeight={900} fontSize={14} fill={timeLeft <= 5 ? T.coral : T.ink}>{timeLeft}</text>
          </svg>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>✓ {currentScore}</div>
        </div>
        {/* FIX: entire cell is a <button> for full touch area */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:10, width:'100%' }}>
          {gridPositions.map((_, i) => {
            const isActive = activeBtn && activeBtn.pos === i;
            const isTrap = isActive && activeBtn.isTrap;
            const cellBg = isActive ? (isTrap ? '#EF4444' : '#34D399') : PASTEL_COLORS[i % PASTEL_COLORS.length];
            return (
              <button key={i} onClick={() => handleTap(i)}
                style={{
                  height:76, borderRadius:18, background: cellBg,
                  border:'none', padding:0,
                  display:'flex', alignItems:'center', justifyContent:'center',
                  cursor:'pointer', transition:'background .08s, transform .08s',
                  boxShadow: isActive ? `0 0 20px ${isTrap ? '#EF444488' : '#34D39988'}` : '0 2px 6px rgba(0,0,0,0.08)',
                  transform: isActive ? 'scale(0.96)' : 'scale(1)',
                  WebkitTapHighlightColor: 'transparent',
                  touchAction: 'manipulation',
                }}>
                {isActive && <span style={{ fontSize:32, pointerEvents:'none' }}>{activeBtn.emoji}</span>}
              </button>
            );
          })}
        </div>
        <div style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, textAlign:'center' }}>Az aktív pad lüktet — koppints rá a minta szerint</div>
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

  // FIX: 'done' phase — show result inline, no empty screen
  if (phase === 'done') {
    const s1 = score1Ref.current, s2 = score2Ref.current;
    const diff = Math.abs(s1 - s2);
    const loser = s1 < s2 ? p1 : s2 < s1 ? p2 : null;
    const drinks = diff > 0 ? diff : 1;
    const winner = loser ? (loser.id === p1?.id ? p2 : p1) : null;
    return (
      <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:18 }}>
        {/* Score comparison */}
        <div style={{ display:'flex', gap:14, width:'100%' }}>
          {[{p: p1, s: s1}, {p: p2, s: s2}].map(({p, s}, i) => {
            const isLoser = loser && loser.id === p?.id;
            return (
              <div key={i} style={{
                flex:1, borderRadius:18, padding:'16px 12px',
                background: isLoser ? `${T.coral}18` : `${T.mint}18`,
                border: `2.5px solid ${isLoser ? T.coral : T.mint}`,
                display:'flex', flexDirection:'column', alignItems:'center', gap:6,
                animation:'popIn .4s',
              }}>
                <div style={{ width:38, height:38, borderRadius:'50%', background: p?.color||T.mint,
                  display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff' }}>
                  {(p?.name||'?').charAt(0).toUpperCase()}
                </div>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink }}>{p?.name}</div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:28, color: isLoser ? T.coral : T.mint }}>{s}</div>
                <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>találat</div>
              </div>
            );
          })}
        </div>
        {/* Result banner */}
        <div style={{
          width:'100%', borderRadius:20, padding:'16px',
          background: loser ? `${T.coral}18` : `${T.yellow}22`,
          border: `2.5px solid ${loser ? T.coral : T.yellow}`,
          textAlign:'center', animation:'eremWin .5s cubic-bezier(0.34,1.56,0.64,1)',
        }}>
          {loser ? (
            <>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.coral }}>😬 {loser.name} veszített</div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink, marginTop:4 }}>
                Iszik <span style={{color:T.coral}}>{drinks} kortyt</span> ({s1} vs {s2})
              </div>
            </>
          ) : (
            <>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.yellow }}>🤝 Döntetlen!</div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink, marginTop:4 }}>
                Mindenki iszik <span style={{color:T.coral}}>1-et</span> ({s1} vs {s2})
              </div>
            </>
          )}
        </div>
      </div>
    );
  }

  return null;
}
'''

src = src[:si] + NEW + src[ei:]

m = re.search(r"APP_VERSION = 'v([\d.]+)'", src)
if m:
    parts = m.group(1).split('.')
    nv = f"{parts[0]}.{int(parts[1])+1}"
    src = src.replace(m.group(0), f"APP_VERSION = 'v{nv}'", 1)
    print(f"Version → v{nv}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('OK')
