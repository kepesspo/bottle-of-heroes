import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Redesign SzerencsekerékGame (slot-machine drum style) ───────────────────
NEW_SZERENCSE = r"""function SzerencsekerékGame({ gameIdx, players, onAdvance }) {
  const [phase, setPhase] = React.useState('ready'); // ready | spinning | result
  const [currentIdx, setCurrentIdx] = React.useState(0);
  const [winner, setWinner] = React.useState(null);

  React.useEffect(() => {
    setPhase('ready');
    setCurrentIdx(gameIdx % Math.max(players.length,1));
    setWinner(null);
  }, [gameIdx]);

  const spin = () => {
    if (phase !== 'ready' || players.length === 0) return;
    setPhase('spinning');
    const n = players.length;
    const winnerIdx = Math.floor(Math.random() * n);
    const stepsToWinner = ((winnerIdx - currentIdx + n) % n) || n;
    const totalSteps = n * 4 + stepsToWinner;
    let step = 0;
    let cur = currentIdx;

    const next = () => {
      step++;
      cur = (cur + 1) % n;
      setCurrentIdx(cur);
      if (step < totalSteps) {
        const progress = step / totalSteps;
        const delay = 55 + Math.pow(progress, 2.2) * 560;
        setTimeout(next, delay);
      } else {
        setWinner(players[winnerIdx]);
        setPhase('result');
      }
    };
    setTimeout(next, 55);
  };

  const proceed = () => {
    const dm = {};
    if (winner) dm[winner.id] = 1;
    onAdvance && onAdvance(dm);
  };

  const n = Math.max(players.length, 1);
  const VISIBLE = 5;
  const half = Math.floor(VISIBLE / 2);

  const visibleItems = [];
  for (let offset = -half; offset <= half; offset++) {
    const idx = ((currentIdx + offset) % n + n) % n;
    visibleItems.push({ player: players[idx], offset });
  }

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:12, width:'100%' }}>

      {/* Drum window */}
      <div style={{ background:'#fff', borderRadius:20, padding:'10px 14px', boxShadow:'0 4px 18px rgba(0,0,0,0.10)', width:'100%', position:'relative', overflow:'hidden' }}>

        {visibleItems.map(({ player, offset }) => {
          const isCenter = offset === 0;
          const dist = Math.abs(offset);
          const alpha = dist === 0 ? 1 : dist === 1 ? 0.55 : 0.3;
          return (
            <div key={`${offset}-${player.id}`} style={{
              display:'flex', alignItems:'center', gap:12,
              padding: isCenter ? '10px 14px' : '6px 14px',
              borderRadius:13,
              background: isCenter ? `${T.mint}18` : 'transparent',
              border: `2px solid ${isCenter ? T.mint : 'transparent'}`,
              marginBottom: 2,
              opacity: alpha,
              transition: 'opacity .1s',
            }}>
              {/* Left arrow indicators */}
              {offset === -1 && (
                <div style={{ position:'absolute', left:8, fontFamily:T.font, fontSize:11, color:T.inkSoft }}>◀</div>
              )}
              {offset === 1 && (
                <div style={{ position:'absolute', left:8, fontFamily:T.font, fontSize:11, color:T.inkSoft }}>▶</div>
              )}
              <div style={{ width:isCenter?44:32, height:isCenter?44:32, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:isCenter?18:13, color:'#fff', flexShrink:0, transition:'all .1s' }}>
                {player.name.charAt(0).toUpperCase()}
              </div>
              <div style={{ fontFamily:T.font, fontWeight:isCenter?800:500, fontSize:isCenter?21:14, color:isCenter?T.ink:T.inkSoft, transition:'all .1s' }}>
                {player.name}
              </div>
            </div>
          );
        })}
      </div>

      {/* Result banner */}
      {phase === 'result' && winner && (
        <div style={{ width:'100%', padding:'10px 18px', borderRadius:14, background:'rgba(255,255,255,0.9)', boxShadow:T.shadow, textAlign:'center', animation:'popIn .3s' }}>
          <span style={{ fontFamily:T.font, fontSize:14, color:T.ink }}>
            🎰 A sors <span style={{ fontWeight:800, color:winner.color }}>{winner.name}</span>-t húzta — iszik!
          </span>
        </div>
      )}

      {/* Buttons */}
      {phase !== 'result' ? (
        <button onClick={spin} disabled={phase==='spinning'} style={{
          width:'100%', padding:'14px', borderRadius:16,
          background: phase==='spinning' ? 'rgba(255,255,255,0.5)' : 'rgba(255,255,255,0.7)',
          border:`2px solid ${T.mint}`, color:T.mint,
          fontFamily:T.font, fontWeight:700, fontSize:16,
          cursor: phase==='spinning' ? 'default' : 'pointer',
          opacity: phase==='spinning' ? 0.65 : 1,
        }}>
          🎰 Sorsolás!
        </button>
      ) : (
        <button onClick={proceed} style={{ width:'100%', padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
          Tovább →
        </button>
      )}
    </div>
  );
}"""

html = re.sub(
    r'function SzerencsekerékGame\(\{ gameIdx, players \}\) \{.*?\n\}(?=\n\nfunction LóversenyGame)',
    NEW_SZERENCSE, html, flags=re.DOTALL
)

# ── 2. Add KategoriaGame before GameContent ────────────────────────────────────
NEW_KATEGORIA = r"""function KategoriaGame({ gameIdx, players, onAdvance }) {
  const CATS = [
    'Fővárosok','Gyümölcsök','Sportágak','Filmek','Állatok',
    'Autómárkák','Zenekarok','Ételek','Országok','TV-sorozatok',
    'Focicsapatok','Koktélok','Énekes előadók','Játékok','Foglalkozások',
    'Hangszerek','Tánctípusok','Borok','Folyók','Magyar városok',
    'Filmhősök','Ruhamárkák','Könyvek','Olimpiai sportok','Helyek Budapesten',
    'Zöldségek','Sütemények','Filmrendezők','Állatfajok','Csapatjátékok',
  ];
  const BG_COLORS = ['#F4D06A','#A8CFF7','#F4A4A0'];

  const cat = CATS[gameIdx % CATS.length];
  const [loserPid, setLoserPid] = React.useState(null);

  React.useEffect(() => { setLoserPid(null); }, [gameIdx]);

  const loser = loserPid ? players.find(p=>p.id===loserPid) : null;

  const proceed = () => {
    const dm = {};
    if (loserPid) dm[loserPid] = 1;
    onAdvance && onAdvance(dm);
  };

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>

      {/* Stacked card deck */}
      <div style={{ position:'relative', width:'100%', height:160 }}>
        {BG_COLORS.map((bg, i) => (
          <div key={i} style={{
            position:'absolute', inset:0,
            background:bg, borderRadius:20,
            transform:`rotate(${[-4,3,0][i]}deg) translateY(${[4,2,0][i]}px)`,
            boxShadow:'0 4px 18px rgba(0,0,0,0.12)',
          }} />
        ))}
        <div style={{ position:'relative', background:'#fff', borderRadius:20, padding:'20px 24px', boxShadow:'0 4px 18px rgba(0,0,0,0.12)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', height:'100%', boxSizing:'border-box' }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.12em', marginBottom:10 }}>KATEGÓRIA</div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:26, color:T.ink, textAlign:'center', lineHeight:1.2 }}>{cat}</div>
        </div>
      </div>

      {/* Player selection */}
      <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.12em' }}>
        Ki nem tudott szót mondani?
      </div>
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
              <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color: selected ? '#E55' : T.ink }}>
                {p.name}
              </div>
            </div>
          );
        })}
      </div>

      {/* Action button */}
      {loser ? (
        <button onClick={proceed} style={{ width:'100%', padding:'15px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, animation:'popIn .2s' }}>
          {loser.name} iszik — új kategória →
        </button>
      ) : (
        <button onClick={() => onAdvance && onAdvance({})} style={{ width:'100%', padding:'15px', background:'rgba(255,255,255,0.6)', color:T.inkSoft, fontFamily:T.font, fontWeight:600, fontSize:15, borderRadius:16, border:`2px solid rgba(0,0,0,0.1)`, cursor:'pointer' }}>
          Senki nem rontott — tovább →
        </button>
      )}
    </div>
  );
}

"""

html = html.replace(
    'function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta, challenger, opponent }) {',
    NEW_KATEGORIA + 'function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta, challenger, opponent }) {',
    1
)

# ── 3. Update GameContent router ───────────────────────────────────────────────
html = html.replace(
    "  if (gameId === 'szerencse') return <SzerencsekerékGame key={gameIdx} gameIdx={gameIdx} players={players||[]} />;",
    "  if (gameId === 'szerencse') return <SzerencsekerékGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;",
    1
)
html = html.replace(
    "  if (gameId === 'collect') return <CollectBoomGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  return null;",
    "  if (gameId === 'collect') return <CollectBoomGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  if (gameId === 'kategoria') return <KategoriaGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  return null;",
    1
)

# ── 4. Exclude self-advancing Csapat games from "Ki nyert?" block ──────────────
html = html.replace(
    "currentGameId !== 'ticktak' && (",
    "currentGameId !== 'ticktak' && currentGameId !== 'szerencse' && currentGameId !== 'kategoria' && currentGameId !== 'collect' && currentGameId !== 'kopapir' && (",
    1
)

# ── 5. Version bump ────────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.22 · DNR · 2026.05.31 03:00',
    'Verzió 5.23 · DNR · 2026.05.31 04:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
