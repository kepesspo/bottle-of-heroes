with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════════════════════════
# 1. KISEBB / NAGYOBB FIXES
# ══════════════════════════════════════════════════════════════════════════════

# 1a. Fix Ace: current card Ace also wins; clear result banner after delay
OLD_HANDLE_GUESS = '''  const handleGuess = (guess) => {
    if (pendRef.current || !nextCard || gameOver) return;
    const cv = cardVal(currentCard.value);
    const nv = cardVal(nextCard.value);
    const same = cv === nv;
    const ok = same ? null : nextCard.value === 'A' ? true : (guess==='K' && nv<cv) || (guess==='N' && nv>cv);

    pendRef.current = true;
    setGuessRes({ correct:ok, same, pid:currentPid, card:nextCard, pot });

    setTimeout(()=>{
      const st = gsRef.current;
      const pid = st.activePids[st.turnPos % Math.max(st.activePids.length,1)];
      let nst = { ...st, deckPos:st.deckPos+1 };

      if (same) {
        // Same value: same player stays, pot grows
        const cfg2 = (gameMeta?.kisebbConfig)||{}; const sm = cfg2.stackMode??'plus1';
        nst = { ...nst, pot: sm==='times2' ? (st.pot||1)*2 : (st.pot||1)+1 };
      } else if (!ok) {
        // Wrong: player drinks pot, next player, pot resets
        const newLives = { ...st.playerLives, [pid]:(st.playerLives[pid]||1)-1 };
        const dm = { ...st.drinkMap, [pid]:(st.drinkMap[pid]||0)+(st.pot||1) };
        const loserPlayer = players.find(p=>p.id===pid);
        onResult && onResult({ correct: false, playerName: loserPlayer?.name, drinks: st.pot||1, subtitle: `${loserPlayer?.name||'Játékos'} iszik ${st.pot||1} kortyt` });
        nst = { ...nst, drinkMap:dm, playerLives:newLives, pot:1,
                turnPos:(st.turnPos+1)%st.activePids.length };
        if ((newLives[pid]||0)<=0) {
          const newActive = st.activePids.filter(p=>p!==pid);
          nst = { ...nst, activePids:newActive, turnPos:st.turnPos%Math.max(newActive.length,1) };
          if (newActive.length<=1) { setGameOver(true); onAdvance&&onAdvance(dm); }
        }
      } else {
        // Correct: next player, pot stays
        nst = { ...nst, turnPos:(st.turnPos+1)%st.activePids.length };
      }

      gsRef.current=nst; setGs({...nst}); setGuessRes(null); pendRef.current=false;
    }, 1800);
  };'''

NEW_HANDLE_GUESS = '''  const handleGuess = (guess) => {
    if (pendRef.current || !nextCard || gameOver) return;
    const cfg2 = (gameMeta?.kisebbConfig)||{};
    const noElim = cfg2.noElim === true;
    const cv = cardVal(currentCard.value);
    const nv = cardVal(nextCard.value);
    const same = cv === nv;
    // Ace: always wins regardless of direction (current or next card)
    const aceWin = currentCard.value === 'A' || nextCard.value === 'A';
    const ok = same ? null : aceWin ? true : (guess==='K' && nv<cv) || (guess==='N' && nv>cv);

    pendRef.current = true;
    setGuessRes({ correct:ok, same, pid:currentPid, card:nextCard, pot });

    setTimeout(()=>{
      const st = gsRef.current;
      const pid = st.activePids[st.turnPos % Math.max(st.activePids.length,1)];
      let nst = { ...st, deckPos:st.deckPos+1 };

      if (same) {
        const sm = cfg2.stackMode??'plus1';
        nst = { ...nst, pot: sm==='times2' ? (st.pot||1)*2 : (st.pot||1)+1 };
      } else if (!ok) {
        const newLives = { ...st.playerLives, [pid]:(st.playerLives[pid]||1)-1 };
        const dm = { ...st.drinkMap, [pid]:(st.drinkMap[pid]||0)+(st.pot||1) };
        const loserPlayer = players.find(p=>p.id===pid);
        onResult && onResult({ correct: false, playerName: loserPlayer?.name, drinks: st.pot||1, subtitle: `${loserPlayer?.name||'Játékos'} iszik ${st.pot||1} kortyt` });
        nst = { ...nst, drinkMap:dm, playerLives:newLives, pot:1,
                turnPos:(st.turnPos+1)%st.activePids.length };
        if (!noElim && (newLives[pid]||0)<=0) {
          const newActive = st.activePids.filter(p=>p!==pid);
          nst = { ...nst, activePids:newActive, turnPos:st.turnPos%Math.max(newActive.length,1) };
          if (newActive.length<=1) { setGameOver(true); onAdvance&&onAdvance(dm); }
        }
      } else {
        nst = { ...nst, turnPos:(st.turnPos+1)%st.activePids.length };
        onResult && onResult(null);
      }

      // No-elim mode: end game when deck runs out
      const atEnd = nst.deckPos >= nst.deck.length - 1;
      if (noElim && atEnd && !gameOver) { setGameOver(true); onAdvance&&onAdvance(nst.drinkMap); }

      gsRef.current=nst; setGs({...nst}); setGuessRes(null); pendRef.current=false;
    }, 1800);
  };'''

assert OLD_HANDLE_GUESS in html, 'handleGuess not found'
html = html.replace(OLD_HANDLE_GUESS, NEW_HANDLE_GUESS, 1)

# 1b. Add "noElim" toggle to KisebbConfigSheet
OLD_KISEBB_CFG_CLOSE = '''        <Row label="Azonos érték (Stack)"'''
NEW_KISEBB_CFG_CLOSE = '''        <Row label="Nem esik ki senki" sub="Játék akkor ér véget ha elfogy a pakli"
          right={<Toggle on={config.noElim===true} onToggle={() => setConfig(c => ({...c, noElim: !c.noElim}))} />} />

        <Row label="Azonos érték (Stack)"'''
assert OLD_KISEBB_CFG_CLOSE in html, 'kisebb config close not found'
html = html.replace(OLD_KISEBB_CFG_CLOSE, NEW_KISEBB_CFG_CLOSE, 1)

# ══════════════════════════════════════════════════════════════════════════════
# 2. ADD 3 NEW GAMES TO GAMES ARRAY
# ══════════════════════════════════════════════════════════════════════════════

OLD_GAMES_END = '''  { id:'igazhamis', name:'Igaz Hamis','''
NEW_GAMES_END = '''  { id:'szolánc',   name:'Szólánc',              difficulty:'közepes', category:'Csapat', emoji:'🔗', symbol:null, img:null, banner:null, color:'#F59E0B', desc:'Ismételd el a sort, majd told hozzá egy új szót a kategóriából. Aki elront, iszik.' },
  { id:'idopárbaj', name:'Időpárbaj',            difficulty:'könnyű',  category:'Páros',  emoji:'⏱️', symbol:null, img:null, banner:null, color:'#6366F1', desc:'Az app elrejt egy véletlenszerű időt 1–30 mp között. Indítsd el a stoppert, majd állítsd le a lehető legközelebb a titkos célhoz. Aki messzebb jár, az iszik.' },
  { id:'csakegyszó', name:'Csak Egy Szó',         difficulty:'könnyű',  category:'Páros',  emoji:'💬', symbol:null, img:null, banner:null, color:'#10B981', desc:'Egy szót kell egyetlen szóval elmagyaráznod a párodnak 15 mp alatt. Ha kitalálja, mindketten pontot kapnak — ha nem, mindketten isznak.' },
  { id:'igazhamis', name:'Igaz Hamis','''
assert OLD_GAMES_END in html, 'games end not found'
html = html.replace(OLD_GAMES_END, NEW_GAMES_END, 1)

# ══════════════════════════════════════════════════════════════════════════════
# 3. ADD NEW GAME COMPONENTS (before GameContent router)
# ══════════════════════════════════════════════════════════════════════════════

OLD_GAME_CONTENT = '''function GameContent({ gameId, gameIdx, players, onAdvance, onUnready, onResult, roomCode, mode, gameMeta, challenger, opponent }) {'''

NEW_GAME_CONTENT = '''// ─── SZÓLÁNC ────────────────────────────────────────────────────────────────
function SzolancGame({ gameIdx, players, onAdvance, onResult }) {
  const CATS = [
    'Gyümölcsök 🍎','Állatok 🐾','Fővárosok 🌍','Autómárkák 🚗','Ételek 🍕',
    'Sportágak ⚽','Filmek 🎬','Zenekarok 🎸','Foglalkozások 👷','Országok 🌐',
    'Zöldségek 🥦','Italok 🍹','Ruhamárkák 👗','Magyar városok 🏙️','Hangszerek 🎺',
    'Sütemények 🍰','TV-sorozatok 📺','Olimpiai sportok 🏅','Állatfajok 🦁',
  ];
  const [catIdx] = React.useState(() => Math.floor(Math.random() * CATS.length));
  const cat = CATS[catIdx];
  const [words, setWords] = React.useState([]); // [{word, pid, name}]
  const [turnIdx, setTurnIdx] = React.useState(0);
  const [phase, setPhase] = React.useState('playing'); // 'playing' | 'done'
  const [timeLeft, setTimeLeft] = React.useState(null);
  const timerRef = React.useRef(null);
  const [committed, setCommitted] = React.useState(false);

  React.useEffect(() => { setWords([]); setTurnIdx(0); setPhase('playing'); setTimeLeft(null); setCommitted(false); }, [gameIdx]);

  const currentPid = players[turnIdx % players.length]?.id;
  const currentPlayer = players[turnIdx % players.length];

  const startTimer = () => {
    setTimeLeft(5 + Math.min(words.length, 10));
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          clearInterval(timerRef.current);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
  };

  React.useEffect(() => () => clearInterval(timerRef.current), []);

  const markFailed = (pid) => {
    if (committed) return;
    setCommitted(true);
    clearInterval(timerRef.current);
    const p = players.find(x => x.id === pid);
    onResult && onResult({ correct: false, playerName: p?.name, drinks: 1, subtitle: `${p?.name} elrontotta — iszik egyet` });
    onAdvance && onAdvance({ [pid]: 1 });
    setPhase('done');
  };

  const addWord = (word) => {
    if (!word.trim()) return;
    const newWords = [...words, { word: word.trim(), pid: currentPid, name: currentPlayer?.name }];
    setWords(newWords);
    setTurnIdx(t => t + 1);
    clearInterval(timerRef.current);
    setTimeLeft(null);
  };

  const [inputWord, setInputWord] = React.useState('');
  React.useEffect(() => { setInputWord(''); }, [turnIdx]);

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:12, width:'100%' }}>
      {/* Category */}
      <div style={{ background:T.surface, borderRadius:16, padding:'12px 16px', display:'flex', alignItems:'center', gap:10, boxShadow:T.shadow }}>
        <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', flexShrink:0 }}>KATEGÓRIA</div>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>{cat}</div>
      </div>

      {/* Word chain list */}
      <div style={{ display:'flex', flexDirection:'column', gap:6, maxHeight:260, overflowY:'auto', WebkitOverflowScrolling:'touch' }}>
        {words.map((w, i) => {
          const p = players.find(x => x.id === w.pid);
          return (
            <div key={i} style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:12, padding:'10px 14px', boxShadow:T.shadow }}>
              <div style={{ width:28, height:28, borderRadius:'50%', background:'rgba(26,42,74,0.10)', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, flexShrink:0 }}>{i+1}</div>
              <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:16, color:T.ink }}>{w.word}</div>
              <div style={{ width:28, height:28, borderRadius:'50%', background:p?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', flexShrink:0 }}>{(p?.name||'?').charAt(0).toUpperCase()}</div>
            </div>
          );
        })}

        {/* Next player row */}
        {phase === 'playing' && (
          <div style={{ display:'flex', alignItems:'flex-start', gap:10, borderRadius:12, padding:'10px 14px', border:`2px dashed ${T.mint}`, background:`${T.mint}08` }}>
            <div style={{ width:28, height:28, borderRadius:'50%', background:T.mint, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:13, color:'#fff', flexShrink:0 }}>{words.length + 1}</div>
            <div style={{ flex:1 }}>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.mint }}>{currentPlayer?.name} jössz…</div>
              <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>ismételd el a {words.length} szót, majd egy újat{timeLeft !== null ? ` · ${timeLeft} mp` : ''}</div>
            </div>
            <div style={{ width:28, height:28, borderRadius:'50%', background:currentPlayer?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', flexShrink:0 }}>{(currentPlayer?.name||'?').charAt(0).toUpperCase()}</div>
          </div>
        )}
      </div>

      {/* Controls */}
      {phase === 'playing' && (
        <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
          {timeLeft === null ? (
            <button onClick={startTimer} style={{ width:'100%', padding:'14px', background:T.mint, color:'#fff', border:'none', borderRadius:16, fontFamily:T.font, fontWeight:800, fontSize:16, cursor:'pointer', boxShadow:T.shadowLift }}>
              ▶ {currentPlayer?.name} indul
            </button>
          ) : (
            <>
              <div style={{ display:'flex', gap:8 }}>
                <div style={{ flex:1, textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:32, color: timeLeft<=3 ? T.coral : T.mint }}>{timeLeft}</div>
              </div>
              <input
                value={inputWord} onChange={e => setInputWord(e.target.value)}
                onKeyDown={e => e.key==='Enter' && inputWord.trim() && addWord(inputWord)}
                placeholder="Új szó a kategóriából…"
                style={{ width:'100%', padding:'12px 14px', borderRadius:12, border:`2px solid ${T.mint}`, fontFamily:T.font, fontSize:16, boxSizing:'border-box', outline:'none', background:T.surface }}
                autoFocus
              />
              <div style={{ display:'flex', gap:8 }}>
                <button onClick={() => inputWord.trim() && addWord(inputWord)} disabled={!inputWord.trim()}
                  style={{ flex:2, padding:'13px', background:T.mint, color:'#fff', border:'none', borderRadius:14, fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer', opacity: inputWord.trim()?1:0.45 }}>
                  ✓ Helyes
                </button>
                <button onClick={() => markFailed(currentPid)}
                  style={{ flex:1, padding:'13px', background:T.coral, color:'#fff', border:'none', borderRadius:14, fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer' }}>
                  ✗ Rontott
                </button>
              </div>
            </>
          )}
          {words.length > 0 && timeLeft === null && (
            <button onClick={() => markFailed(currentPid)} style={{ width:'100%', padding:'12px', background:`${T.coral}18`, color:T.coral, border:`1.5px solid ${T.coral}40`, borderRadius:14, fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>
              {currentPlayer?.name} rontott — iszik →
            </button>
          )}
        </div>
      )}
    </div>
  );
}

// ─── IDŐPÁRBAJ ───────────────────────────────────────────────────────────────
function IdoparbajGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  const target = React.useRef(+(1 + Math.random() * 29).toFixed(1));
  const [phase, setPhase] = React.useState('idle'); // 'idle'|'p1running'|'p1done'|'p2running'|'p2done'|'result'
  const [t1, setT1] = React.useState(null);
  const [t2, setT2] = React.useState(null);
  const startRef = React.useRef(null);
  const advRef = React.useRef(false);

  React.useEffect(() => { target.current = +(1 + Math.random() * 29).toFixed(1); setPhase('idle'); setT1(null); setT2(null); advRef.current = false; }, [gameIdx]);

  const startP1 = () => { startRef.current = Date.now(); setPhase('p1running'); };
  const stopP1 = () => { const elapsed = (Date.now() - startRef.current) / 1000; setT1(+elapsed.toFixed(1)); setPhase('p1done'); };
  const startP2 = () => { startRef.current = Date.now(); setPhase('p2running'); };
  const stopP2 = () => {
    const elapsed = (Date.now() - startRef.current) / 1000; const tv = +elapsed.toFixed(1); setT2(tv); setPhase('result');
    const tgt = target.current;
    if (!advRef.current) {
      advRef.current = true;
      const d1 = Math.abs(t1 - tgt), d2 = Math.abs(tv - tgt);
      const p1wins = d1 <= d2;
      const loser = p1wins ? opponent : challenger;
      const winner = p1wins ? challenger : opponent;
      setTimeout(() => {
        onResult && onResult({ correct: false, playerName: loser?.name, drinks: 1, subtitle: `${loser?.name} iszik — ${winner?.name} nyert` });
        onAdvance && onAdvance({ [loser?.id]: 1 });
      }, 400);
    }
  };

  const tgt = target.current;
  const BigBtn = ({ label, sub, onClick, color }) => (
    <button onClick={onClick} style={{ width:'100%', padding:'22px 0', background:color||T.mint, color:'#fff', border:'none', borderRadius:20, fontFamily:T.font, fontWeight:900, fontSize:22, cursor:'pointer', boxShadow:T.shadowLift, display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
      <span>{label}</span>
      {sub && <span style={{ fontSize:13, fontWeight:600, opacity:0.85 }}>{sub}</span>}
    </button>
  );

  const PlayerChip = ({ p, time, active, winner }) => (
    <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:6, padding:'14px 10px', borderRadius:16, background: winner===true ? `${T.mint}18` : winner===false ? `${T.coral}18` : active ? `${p?.color}18` : T.surface, border:`2px solid ${winner===true?T.mint:winner===false?T.coral:active?p?.color:'transparent'}`, boxShadow:T.shadow }}>
      <div style={{ width:44, height:44, borderRadius:'50%', background:p?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:18, color:'#fff' }}>{(p?.name||'?').charAt(0).toUpperCase()}</div>
      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{p?.name}</div>
      {time !== null && <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:26, color: winner===true?T.mint:winner===false?T.coral:T.ink }}>{time.toFixed(1)}<span style={{ fontFamily:T.font, fontSize:13, fontWeight:700 }}>mp</span></div>}
      {time !== null && phase==='result' && <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft }}>{time===tgt?'🎯 Pontos!': (time>tgt?`+${(time-tgt).toFixed(1)} mp eltérés`:`${(time-tgt).toFixed(1)} mp eltérés`)}</div>}
      {winner===true && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.mint, background:`${T.mint}22`, borderRadius:999, padding:'2px 10px' }}>NYERT</div>}
      {winner===false && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.coral, background:`${T.coral}22`, borderRadius:999, padding:'2px 10px' }}>ISZIK 🍺</div>}
    </div>
  );

  const d1 = t1 !== null ? Math.abs(t1 - tgt) : null;
  const d2 = t2 !== null ? Math.abs(t2 - tgt) : null;
  const p1wins = phase === 'result' ? (d1 <= d2) : null;

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:16, alignItems:'center', width:'100%' }}>
      {/* Target time — revealed only in result */}
      <div style={{ background:'#1B2340', borderRadius:16, padding:'16px 24px', width:'100%', textAlign:'center', boxSizing:'border-box' }}>
        <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:'rgba(255,255,255,0.5)', textTransform:'uppercase', letterSpacing:'0.12em', marginBottom:6 }}>A TITKOS CÉL ENNYI VOLT</div>
        {phase === 'result' ? (
          <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:42, color:'#fff', lineHeight:1 }}>{tgt.toFixed(1)}<span style={{ fontFamily:T.font, fontSize:20, fontWeight:700, marginLeft:4 }}>mp</span></div>
        ) : (
          <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:42, color:'rgba(255,255,255,0.15)', lineHeight:1 }}>?</div>
        )}
      </div>

      {/* Player chips */}
      <div style={{ display:'flex', gap:10, width:'100%' }}>
        <PlayerChip p={challenger} time={t1} active={phase==='p1running'||phase==='p1done'} winner={phase==='result'?p1wins:null} />
        <PlayerChip p={opponent}   time={t2} active={phase==='p2running'||phase==='p2done'} winner={phase==='result'?(p2wins=>p2wins)(d2<=d1):null} />
      </div>

      {/* Action area */}
      {phase==='idle'    && <BigBtn label={`▶ ${challenger?.name} indul`} sub="Nyomd meg az időzítő indításához" onClick={startP1} color={challenger?.color} />}
      {phase==='p1running' && <BigBtn label="⏹ Stop!" sub={`${challenger?.name} — nyomd meg a megállításhoz`} onClick={stopP1} color={T.coral} />}
      {phase==='p1done'  && <BigBtn label={`▶ ${opponent?.name} indul`} sub="Nyomd meg az időzítő indításához" onClick={startP2} color={opponent?.color} />}
      {phase==='p2running' && <BigBtn label="⏹ Stop!" sub={`${opponent?.name} — nyomd meg a megállításhoz`} onClick={stopP2} color={T.coral} />}
    </div>
  );
}

// ─── CSAK EGY SZÓ ────────────────────────────────────────────────────────────
function CsakEgySzoGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  const WORDS = [
    'Napsütés','Kaland','Barátság','Csend','Öröm','Otthon','Álom','Tenger','Erdő','Boldogság',
    'Zene','Szerelem','Szabadság','Gőzmozdony','Kísértet','Könyvtár','Homokóra','Csillag','Hullám','Tűz',
    'Jégkrém','Futball','Hegymászás','Mágnes','Vulkán','Kristály','Vitorla','Kalapács','Pókháló','Robot',
    'Méz','Villámlás','Hóvihar','Bálna','Sakk','Piramis','Kaktusz','Karate','Asztronauta','Delfin',
    'Pizza','Lány','Fiú','Cipő','Ital','Étel','Szék','Ablakok','Ajtó','Telefon',
  ];
  const [wordIdx] = React.useState(() => Math.floor(Math.random() * WORDS.length));
  const word = WORDS[(gameIdx * 7 + wordIdx) % WORDS.length];
  const [phase, setPhase] = React.useState('reveal'); // 'reveal'|'guessing'|'done'
  const [timeLeft, setTimeLeft] = React.useState(15);
  const timerRef = React.useRef(null);
  const advRef = React.useRef(false);

  React.useEffect(() => { setPhase('reveal'); setTimeLeft(15); clearInterval(timerRef.current); advRef.current = false; }, [gameIdx]);
  React.useEffect(() => () => clearInterval(timerRef.current), []);

  const startGuessing = () => {
    setPhase('guessing');
    timerRef.current = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) { clearInterval(timerRef.current); commitResult(false); return 0; }
        return t - 1;
      });
    }, 1000);
  };

  const commitResult = (success) => {
    if (advRef.current) return;
    advRef.current = true;
    clearInterval(timerRef.current);
    setPhase('done');
    if (success) {
      onResult && onResult({ correct: true, playerName: challenger?.name, drinks: 0, subtitle: `${challenger?.name} & ${opponent?.name} — mindketten +1 pont!` });
    } else {
      onResult && onResult({ correct: false, playerName: null, drinks: 1, subtitle: `Nem sikerült — mindketten isznak 🍺` });
    }
    onAdvance && onAdvance(success ? { [challenger?.id]:0,[opponent?.id]:0 } : { [challenger?.id]:1,[opponent?.id]:1 });
  };

  const pct = (timeLeft / 15) * 100;
  const circumference = 2 * Math.PI * 44;

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:16, alignItems:'center', width:'100%' }}>
      {/* Players */}
      <div style={{ display:'flex', alignItems:'center', gap:8, width:'100%' }}>
        <div style={{ flex:1, display:'flex', alignItems:'center', gap:8, background:T.surface, borderRadius:12, padding:'8px 12px', boxShadow:T.shadow }}>
          <div style={{ width:32, height:32, borderRadius:'50%', background:challenger?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:14, color:'#fff' }}>{(challenger?.name||'?').charAt(0).toUpperCase()}</div>
          <div style={{ flex:1 }}>
            <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>MAGYARÁZ</div>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>{challenger?.name}</div>
          </div>
        </div>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, color:T.inkSoft }}>→</div>
        <div style={{ flex:1, display:'flex', alignItems:'center', gap:8, background:T.surface, borderRadius:12, padding:'8px 12px', boxShadow:T.shadow }}>
          <div style={{ width:32, height:32, borderRadius:'50%', background:opponent?.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:14, color:'#fff' }}>{(opponent?.name||'?').charAt(0).toUpperCase()}</div>
          <div style={{ flex:1 }}>
            <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>TIPPEL</div>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>{opponent?.name}</div>
          </div>
        </div>
      </div>

      {/* Word card */}
      <div style={{ background:'#1B2340', borderRadius:18, padding:'24px 20px', width:'100%', textAlign:'center', boxSizing:'border-box' }}>
        <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:'rgba(255,255,255,0.45)', textTransform:'uppercase', letterSpacing:'0.12em', marginBottom:10 }}>👁 CSAK {(challenger?.name||'?').toUpperCase()} LÁTJA</div>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:36, color:'#fff', textTransform:'uppercase', letterSpacing:'-0.01em', lineHeight:1.1 }}>{word}</div>
        <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.5)', marginTop:8 }}>Ezt magyarázd el — egyetlen szóval</div>
      </div>

      {/* Timer circle */}
      {phase === 'guessing' && (
        <svg width={100} height={100} style={{ flexShrink:0 }}>
          <circle cx={50} cy={50} r={44} fill="none" stroke="rgba(0,0,0,0.08)" strokeWidth={8} />
          <circle cx={50} cy={50} r={44} fill="none" stroke={timeLeft<=5?T.coral:T.mint} strokeWidth={8}
            strokeDasharray={circumference} strokeDashoffset={circumference*(1-pct/100)}
            strokeLinecap="round" transform="rotate(-90 50 50)" style={{ transition:'stroke-dashoffset .9s linear' }}/>
          <text x={50} y={55} textAnchor="middle" fontFamily={T.font} fontWeight={900} fontSize={28} fill={timeLeft<=5?T.coral:T.ink}>{timeLeft}</text>
        </svg>
      )}

      {/* Rule reminder */}
      {phase !== 'done' && (
        <div style={{ background:T.surfaceMuted, borderRadius:14, padding:'12px 16px', width:'100%', display:'flex', alignItems:'center', gap:10, boxSizing:'border-box' }}>
          <span style={{ fontSize:18 }}>💬</span>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.ink, fontWeight:600, lineHeight:1.4 }}>Mondj <b>egyetlen szót</b> — tilos mutogatni!</div>
        </div>
      )}

      {/* Action buttons */}
      {phase === 'reveal' && (
        <button onClick={startGuessing} style={{ width:'100%', padding:'16px', background:T.mint, color:'#fff', border:'none', borderRadius:16, fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:T.shadowLift }}>
          ▶ Kezdés — 15 mp
        </button>
      )}
      {phase === 'guessing' && (
        <div style={{ display:'flex', gap:10, width:'100%' }}>
          <button onClick={() => commitResult(true)} style={{ flex:1, padding:'16px 8px', background:T.mint, color:'#fff', border:'none', borderRadius:16, fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer', boxShadow:T.shadowLift, display:'flex', flexDirection:'column', alignItems:'center', gap:2 }}>
            <span>Kitalálta! ✓</span><span style={{ fontSize:12, fontWeight:600, opacity:0.85 }}>+1 pont mindkettőnek</span>
          </button>
          <button onClick={() => commitResult(false)} style={{ flex:1, padding:'16px 8px', background:T.coral, color:'#fff', border:'none', borderRadius:16, fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer', boxShadow:T.shadowLift, display:'flex', flexDirection:'column', alignItems:'center', gap:2 }}>
            <span>Nem sikerült</span><span style={{ fontSize:12, fontWeight:600, opacity:0.85 }}>mindketten isznak 🍺</span>
          </button>
        </div>
      )}
    </div>
  );
}

function GameContent({ gameId, gameIdx, players, onAdvance, onUnready, onResult, roomCode, mode, gameMeta, challenger, opponent }) {'''

assert OLD_GAME_CONTENT in html, 'GameContent not found'
html = html.replace(OLD_GAME_CONTENT, NEW_GAME_CONTENT, 1)

# ══════════════════════════════════════════════════════════════════════════════
# 4. WIRE NEW GAMES IN GameContent ROUTER
# ══════════════════════════════════════════════════════════════════════════════

OLD_ROUTER_END = '''  if (gameId === 'kisebb') return <KisebbGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />;'''
NEW_ROUTER_END = '''  if (gameId === 'kisebb') return <KisebbGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />;
  if (gameId === 'szolánc') return <SzolancGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'idopárbaj') return <IdoparbajGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'csakegyszó') return <CsakEgySzoGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;'''

assert OLD_ROUTER_END in html, 'router end not found'
html = html.replace(OLD_ROUTER_END, NEW_ROUTER_END, 1)

# ══════════════════════════════════════════════════════════════════════════════
# 5. VERSION BUMP
# ══════════════════════════════════════════════════════════════════════════════
OLD_VER = "const APP_VERSION = 'v7.55'"
NEW_VER = "const APP_VERSION = 'v7.56'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
