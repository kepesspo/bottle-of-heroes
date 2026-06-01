import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. MemoriaGame ───────────────────────────────────────────────────────────
NEW_MEMORIA = r"""function MemoriaGame({ gameIdx, players, onAdvance }) {
  const SYMBOLS = ['★','♥','💧','◇','☾','✦','●','▲'];
  const cards = React.useMemo(() => {
    const deck = [...SYMBOLS, ...SYMBOLS];
    let s = (gameIdx * 1234567891 + 42) >>> 0;
    const rng = () => { s^=s<<13; s^=s>>17; s^=s<<5; return s>>>0; };
    for (let i = deck.length-1; i>0; i--) {
      const j = rng()%(i+1); [deck[i],deck[j]]=[deck[j],deck[i]];
    }
    return deck;
  }, [gameIdx]);

  const n = Math.max(players.length, 1);
  const [flipped, setFlipped] = React.useState([]);
  const [matched, setMatched] = React.useState(new Set());
  const [turn, setTurn] = React.useState(gameIdx % n);
  const [scores, setScores] = React.useState({});
  const [matchFlash, setMatchFlash] = React.useState(false);
  const [locked, setLocked] = React.useState(false);

  React.useEffect(() => {
    setFlipped([]); setMatched(new Set()); setTurn(gameIdx % n);
    setScores({}); setMatchFlash(false); setLocked(false);
  }, [gameIdx]);

  const currentPlayer = players[turn % n];
  const allMatched = matched.size === cards.length;

  const tap = (i) => {
    if (locked || matched.has(i) || flipped.includes(i) || flipped.length >= 2) return;
    const next = [...flipped, i];
    setFlipped(next);
    if (next.length === 2) {
      setLocked(true);
      const [a, b] = next;
      if (cards[a] === cards[b]) {
        setTimeout(() => {
          setMatched(prev => { const s = new Set(prev); s.add(a); s.add(b); return s; });
          setScores(prev => ({...prev, [currentPlayer.id]: (prev[currentPlayer.id]||0)+1}));
          setMatchFlash(true);
          setFlipped([]);
          setLocked(false);
          setTimeout(() => setMatchFlash(false), 1300);
        }, 500);
      } else {
        setTimeout(() => {
          setFlipped([]);
          setTurn(prev => (prev + 1) % n);
          setLocked(false);
        }, 1300);
      }
    }
  };

  const symColors = {'★':'#E8A020','♥':'#E55555','💧':'#5B9BD5','◇':'#9090B0','☾':'#C09040','✦':'#40A8A8','●':'#50B870','▲':'#E07040'};

  if (allMatched) {
    const entries = players.map(p => ({p, pairs: scores[p.id]||0})).sort((a,b)=>b.pairs-a.pairs);
    const minPairs = Math.min(...entries.map(e=>e.pairs));
    const loser = entries.find(e=>e.pairs===minPairs)?.p;
    return (
      <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14, width:'100%' }}>
        <div style={{ fontSize:42 }}>🎉</div>
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:20, color:T.ink }}>Minden pár megvolt!</div>
        <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:6 }}>
          {entries.map(({p, pairs}) => (
            <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, padding:'8px 14px', borderRadius:12, background:'rgba(255,255,255,0.85)', boxShadow:T.shadow }}>
              <div style={{ width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>
                {p.name.charAt(0).toUpperCase()}
              </div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink, flex:1 }}>{p.name}</div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.mint }}>{pairs} par</div>
            </div>
          ))}
        </div>
        <button onClick={() => onAdvance && onAdvance(loser ? {[loser.id]:1} : {})} style={{ width:'100%', padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
          {loser ? `${loser.name} iszik — uj kor →` : 'Uj kor →'}
        </button>
      </div>
    );
  }

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:10, width:'100%' }}>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft }}>
        <span style={{ fontWeight:700, color:currentPlayer?.color||T.ink }}>{currentPlayer?.name}</span> fordit lapot
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:7, width:'100%' }}>
        {cards.map((sym, i) => {
          const isMatched = matched.has(i);
          const isFaceUp = isMatched || flipped.includes(i);
          const isMiss = !isMatched && flipped.length===2 && flipped.includes(i) && cards[flipped[0]]!==cards[flipped[1]];
          return (
            <div key={i} onClick={() => tap(i)} style={{
              aspectRatio:'1', borderRadius:12,
              background: isMatched ? `${T.mint}28` : isMiss ? '#FFF0EE' : isFaceUp ? '#fff' : '#F5ECD8',
              border:`2px solid ${isMatched ? T.mint : isMiss ? '#F87171' : isFaceUp ? '#E0D8C8' : 'transparent'}`,
              display:'flex', alignItems:'center', justifyContent:'center',
              cursor:(isFaceUp||locked)?'default':'pointer',
              transition:'background .2s, border .2s',
              fontSize: isFaceUp ? 22 : 14,
              color: isFaceUp ? (symColors[sym]||T.ink) : '#C4B898',
              userSelect:'none',
            }}>
              {isFaceUp ? sym : '◇'}
            </div>
          );
        })}
      </div>

      {matchFlash && currentPlayer && (
        <div style={{ width:'100%', padding:'10px 16px', borderRadius:14, background:'rgba(255,255,255,0.92)', boxShadow:T.shadow, display:'flex', alignItems:'center', gap:10, animation:'popIn .2s' }}>
          <span style={{ fontSize:20 }}>🎉</span>
          <span style={{ fontFamily:T.font, fontSize:14, color:T.ink }}>
            <span style={{ fontWeight:800, color:T.mint }}>Par!</span>
            {' '}<span style={{ fontWeight:700, color:currentPlayer.color }}>{currentPlayer.name}</span>
            {' '}viszi — johet meg egy lap.
          </span>
        </div>
      )}
    </div>
  );
}

"""

# ── 2. KezCsereGame ─────────────────────────────────────────────────────────
NEW_KEZCSERE = r"""function KezCsereGame({ gameIdx, players, onAdvance }) {
  const [loserPid, setLoserPid] = React.useState(null);
  React.useEffect(() => { setLoserPid(null); }, [gameIdx]);
  const loser = loserPid ? players.find(p => p.id === loserPid) : null;
  const proceed = () => {
    const dm = {};
    if (loserPid) dm[loserPid] = 1;
    onAdvance && onAdvance(dm);
  };
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>
      <div style={{ width:130, height:130, borderRadius:'50%', background:'#fff', boxShadow:'0 4px 18px rgba(0,0,0,0.10)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:60 }}>
        ✋
      </div>
      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:18, color:T.ink }}>Ki rontott el?</div>
      <div style={{ display:'flex', gap:8, flexWrap:'wrap', justifyContent:'center' }}>
        {players.map(p => {
          const selected = loserPid === p.id;
          return (
            <div key={p.id} onClick={() => setLoserPid(selected ? null : p.id)} style={{
              display:'flex', flexDirection:'column', alignItems:'center', gap:6,
              padding:'10px 14px', borderRadius:14,
              background: selected ? '#FFF0EE' : '#fff',
              border:`2px solid ${selected ? '#F87171' : 'transparent'}`,
              boxShadow:'0 2px 8px rgba(0,0,0,0.08)', cursor:'pointer', minWidth:70,
            }}>
              <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>
                {p.name.charAt(0).toUpperCase()}
              </div>
              <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color:selected?'#E55':T.ink }}>
                {p.name}
              </div>
            </div>
          );
        })}
      </div>
      {loser ? (
        <button onClick={proceed} style={{ width:'100%', padding:'15px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, animation:'popIn .2s' }}>
          {loser.name} iszik — uj kor →
        </button>
      ) : (
        <button onClick={() => onAdvance && onAdvance({})} style={{ width:'100%', padding:'15px', background:'rgba(255,255,255,0.6)', color:T.inkSoft, fontFamily:T.font, fontWeight:600, fontSize:15, borderRadius:16, border:`2px solid rgba(0,0,0,0.1)`, cursor:'pointer' }}>
          Senki nem rontott — tovabb →
        </button>
      )}
    </div>
  );
}

"""

# ── 3. TicktakGame redesign ──────────────────────────────────────────────────
NEW_TICKTAK = r"""function TicktakGame({ gameIdx, players, onAdvance }) {
  const [phase, setPhase] = React.useState('ready');
  const [loserPid, setLoserPid] = React.useState(null);
  const timerRef = React.useRef(null);

  React.useEffect(() => {
    setPhase('ready'); setLoserPid(null);
    return () => clearTimeout(timerRef.current);
  }, [gameIdx]);

  const start = () => {
    setPhase('running');
    const delay = 15000 + Math.floor(Math.random() * 30000);
    timerRef.current = setTimeout(() => setPhase('buzz'), delay);
  };

  const loser = loserPid ? players.find(p => p.id === loserPid) : null;

  const proceed = () => {
    const dm = {};
    if (loserPid) dm[loserPid] = 1;
    onAdvance && onAdvance(dm);
  };

  if (phase === 'ready') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ width:120, height:120, borderRadius:'50%', background:'rgba(255,255,255,0.85)', boxShadow:'0 4px 18px rgba(0,0,0,0.10)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:56 }}>
        ⏰
      </div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5, maxWidth:260 }}>
        Korbeadjatok a targyat! Az idozito titokban indul — mikor cseng, annal a jatekosnal aki epp tartja.
      </div>
      <button onClick={start} style={{ width:'100%', padding:'15px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
        ⏰ Idozito inditasa!
      </button>
    </div>
  );

  if (phase === 'running') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ width:120, height:120, borderRadius:'50%', background:'rgba(255,255,255,0.85)', boxShadow:'0 4px 18px rgba(0,0,0,0.10)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:60, animation:'pulse 0.7s infinite' }}>
        ⏰
      </div>
      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:24, color:T.mint, textTransform:'uppercase', letterSpacing:'0.1em' }}>Megy!</div>
      <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>Adjatok korbe a targyat!</div>
    </div>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14, width:'100%' }}>
      <div style={{ width:130, height:130, borderRadius:'50%', background:'#fff', boxShadow:'0 4px 18px rgba(0,0,0,0.12)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:64, animation:!loserPid?'pulse 0.4s infinite':'none' }}>
        ⏰
      </div>
      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:26, color:T.coral, textTransform:'uppercase', letterSpacing:'0.08em' }}>
        CSOROG! 🔔
      </div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginBottom:4 }}>Kinel volt a targy a kezeben?</div>
      <div style={{ display:'flex', gap:8, flexWrap:'wrap', justifyContent:'center' }}>
        {players.map(p => {
          const selected = loserPid === p.id;
          return (
            <div key={p.id} onClick={() => !loserPid && setLoserPid(p.id)} style={{
              display:'flex', flexDirection:'column', alignItems:'center', gap:6,
              padding:'10px 14px', borderRadius:14,
              background: selected ? '#FFF0EE' : '#fff',
              border:`2px solid ${selected ? '#F87171' : 'transparent'}`,
              boxShadow:'0 2px 8px rgba(0,0,0,0.08)', cursor:loserPid?'default':'pointer', minWidth:70,
            }}>
              <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>
                {p.name.charAt(0).toUpperCase()}
              </div>
              <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color:selected?'#E55':T.ink }}>
                {p.name}
              </div>
            </div>
          );
        })}
      </div>
      {loser && (
        <button onClick={proceed} style={{ width:'100%', padding:'15px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, animation:'popIn .2s' }}>
          {loser.name} iszik — uj kor →
        </button>
      )}
    </div>
  );
}"""

# ── 4. Insert MemoriaGame + KezCsereGame before GameContent ─────────────────
html = html.replace(
    'function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta, challenger, opponent }) {',
    NEW_MEMORIA + NEW_KEZCSERE + 'function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta, challenger, opponent }) {',
    1
)

# ── 5. Replace TicktakGame ───────────────────────────────────────────────────
html = re.sub(
    r'function TicktakGame\(\{ gameIdx, players, onAdvance \}\) \{.*?\n\}(?=\n\nfunction EremGame)',
    NEW_TICKTAK, html, flags=re.DOTALL
)

# ── 6. GameContent router entries ────────────────────────────────────────────
html = html.replace(
    "  if (gameId === 'kategoria') return <KategoriaGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  return null;",
    "  if (gameId === 'kategoria') return <KategoriaGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  if (gameId === 'memoria') return <MemoriaGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  if (gameId === 'kezcsere') return <KezCsereGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  return null;",
    1
)

# ── 7. Add to Csapat self-advancing exceptions ───────────────────────────────
html = html.replace(
    "currentGameId !== 'ticktak' && currentGameId !== 'szerencse' && currentGameId !== 'kategoria' && currentGameId !== 'collect' && currentGameId !== 'kopapir' && (",
    "currentGameId !== 'ticktak' && currentGameId !== 'szerencse' && currentGameId !== 'kategoria' && currentGameId !== 'collect' && currentGameId !== 'kopapir' && currentGameId !== 'memoria' && currentGameId !== 'kezcsere' && (",
    1
)

# ── 8. Version bump ──────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.24 · DNR · 2026.05.31 05:00',
    'Verzió 5.25 · DNR · 2026.06.01 01:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
