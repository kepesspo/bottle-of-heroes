#!/usr/bin/env python3
"""patch_9_158.py — RitmusGame: gyors folyamatos spawn, tappelés után azonnal következő"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.157';" in content
content = content.replace("const APP_VERSION = 'v9.157';", "const APP_VERSION = 'v9.158';")

OLD_RITMUS = """function RitmusGame({ gameIdx, players, challenger, opponent, onAdvance, onResult }) {
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

  const p1 = challenger;
  const p2 = opponent || (players && players.find(p => p.id !== challenger?.id)) || null;

  useEffect(() => () => { clearInterval(ivRef.current); clearTimeout(btnTimerRef.current); }, []);

  const spawnButton = () => {
    const pos = Math.floor(Math.random() * GRID);
    setActiveBtn(pos);
    setTapped(false);
    clearTimeout(btnTimerRef.current);
    btnTimerRef.current = setTimeout(() => { setActiveBtn(null); }, 800 + Math.random() * 400);
  };

  const startRound = (isP2) => {
    scoreRef.current = 0;
    setCurrentScore(0);
    setActiveBtn(null);
    setTimeLeft(DURATION);
    setPhase(isP2 ? 'p2playing' : 'p1playing');
    const endTime = Date.now() + DURATION * 1000;
    clearInterval(ivRef.current);
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (endTime - Date.now()) / 1000);
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
      if (Date.now() >= endTime) return;
      spawnButton();
      btnTimerRef.current = setTimeout(spawnLoop, 900 + Math.random() * 700);
    };
    setTimeout(spawnLoop, 500);
  };

  useEffect(() => {
    if (phase === 'done') {
      const s1 = score1, s2 = score2;
      const diff = Math.abs(s1 - s2);
      const loser = s1 < s2 ? p1 : s2 < s1 ? p2 : null;
      const drinks = diff > 0 ? diff : 1;
      const dm = {};
      if (loser) dm[loser.id] = drinks;
      const subtitle = loser ? `${loser.name} iszik ${drinks} kortyt (${s1} vs ${s2})` : `Döntetlen! (${s1} vs ${s2}) — mindenki iszik 1-et`;
      if (!loser) { players?.forEach(p => { dm[p.id] = 1; }); }
      if (!advancedRef.current) {
        advancedRef.current = true;
        onResult && onResult({ correct: !loser, playerName: loser?.name || '', drinks, subtitle });
        onAdvance && onAdvance(dm, {});
      }
    }
  }, [phase]);

  const handleTap = (pos) => {
    if (activeBtn !== pos || tapped) return;
    setTapped(true);
    setActiveBtn(null);
    scoreRef.current += 1;
    setCurrentScore(scoreRef.current);
    clearTimeout(btnTimerRef.current);
  };"""

NEW_RITMUS = """function RitmusGame({ gameIdx, players, challenger, opponent, onAdvance, onResult }) {
  const GRID = 12;
  const DURATION = 30;
  const EMOJIS = ['🎯','⭐','🔥','💎','🎵','🍀','⚡','🎪','🦋','🎸','🎲','🚀'];
  const [phase, setPhase] = useState('intro');
  const [timeLeft, setTimeLeft] = useState(DURATION);
  const [activeBtn, setActiveBtn] = useState(null);  // {pos, emoji}
  const [score1, setScore1] = useState(0);
  const [score2, setScore2] = useState(0);
  const [currentScore, setCurrentScore] = useState(0);
  const ivRef = useRef(null);
  const btnTimerRef = useRef(null);
  const spawnTimerRef = useRef(null);
  const advancedRef = useRef(false);
  const scoreRef = useRef(0);
  const endTimeRef = useRef(0);
  const isP2Ref = useRef(false);

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
    const emoji = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
    setActiveBtn({ pos, emoji });
    // Button visible 380–580ms then disappears, next spawns immediately after
    const visibleMs = 380 + Math.random() * 200;
    btnTimerRef.current = setTimeout(() => {
      setActiveBtn(null);
      // 80ms gap between buttons
      spawnTimerRef.current = setTimeout(spawnNext, 80);
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
    clearInterval(ivRef.current);
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (endTime - Date.now()) / 1000);
      setTimeLeft(Math.ceil(rem));
      if (rem <= 0) {
        clearInterval(ivRef.current);
        clearTimeout(btnTimerRef.current);
        clearTimeout(spawnTimerRef.current);
        setActiveBtn(null);
        if (!isP2) { setScore1(scoreRef.current); setPhase('p1done'); }
        else { setScore2(scoreRef.current); setPhase('done'); }
      }
    }, 100);
    // Start spawning after 300ms
    spawnTimerRef.current = setTimeout(spawnNext, 300);
  };

  useEffect(() => {
    if (phase === 'done') {
      const s1 = score1, s2 = score2;
      const diff = Math.abs(s1 - s2);
      const loser = s1 < s2 ? p1 : s2 < s1 ? p2 : null;
      const drinks = diff > 0 ? diff : 1;
      const dm = {};
      if (loser) dm[loser.id] = drinks;
      const subtitle = loser ? `${loser.name} iszik ${drinks} kortyt (${s1} vs ${s2})` : `Döntetlen! (${s1} vs ${s2}) — mindenki iszik 1-et`;
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
    // Correct tap
    clearTimeout(btnTimerRef.current);
    setActiveBtn(null);
    scoreRef.current += 1;
    setCurrentScore(scoreRef.current);
    // Spawn next immediately after short gap
    spawnTimerRef.current = setTimeout(spawnNext, 100);
  };"""

assert OLD_RITMUS in content, "RitmusGame not found"
content = content.replace(OLD_RITMUS, NEW_RITMUS, 1)

# Also update the grid rendering to show the emoji from activeBtn object
OLD_GRID = """        <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:10, width:'100%' }}>
          {gridPositions.map((_, i) => {
            const isActive = activeBtn === i;
            return (
              <div key={i} onClick={() => handleTap(i)}
                style={{ height:72, borderRadius:16, background: isActive ? T.mint : T.surfaceMuted, border: isActive ? `3px solid ${T.mint}` : '3px solid transparent', display:'grid', placeItems:'center', cursor:'pointer', transition:'background .08s', boxShadow: isActive ? `0 0 18px ${T.mint}88` : 'none' }}>
                {isActive && <span style={{ fontSize:28 }}>🎯</span>}
              </div>
            );
          })}
        </div>"""

NEW_GRID = """        <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:10, width:'100%' }}>
          {gridPositions.map((_, i) => {
            const isActive = activeBtn && activeBtn.pos === i;
            return (
              <div key={i} onClick={() => handleTap(i)}
                style={{ height:72, borderRadius:16, background: isActive ? T.mint : T.surfaceMuted, border: isActive ? `3px solid ${T.mint}` : '3px solid transparent', display:'grid', placeItems:'center', cursor:'pointer', transition:'background .06s', boxShadow: isActive ? `0 0 18px ${T.mint}88` : 'none' }}>
                {isActive && <span style={{ fontSize:30, animation:'popIn .1s' }}>{activeBtn.emoji}</span>}
              </div>
            );
          })}
        </div>"""

assert OLD_GRID in content, "grid not found"
content = content.replace(OLD_GRID, NEW_GRID, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.158 ready")
