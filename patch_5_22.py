import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add CollectBoomGame before GameContent ──────────────────────────────────
NEW_COLLECT = r"""function CollectBoomGame({ gameIdx, players, onAdvance }) {
  const COLS = 4, ROWS = 4, TOTAL = 16;

  const grid = React.useMemo(() => {
    const cells = [
      {type:'bomb'}, {type:'bomb'},
      {type:'star'}, {type:'star'},
      ...[3,1,5,2,4,2,3,1,4,3,2,5].map(v => ({type:'pts',v})),
    ];
    let s = (gameIdx * 1234567891 + 99) >>> 0;
    const rng = () => { s^=s<<13; s^=s>>17; s^=s<<5; return s>>>0; };
    for (let i = cells.length-1; i>0; i--) {
      const j = rng()%(i+1); [cells[i],cells[j]]=[cells[j],cells[i]];
    }
    return cells;
  }, [gameIdx]);

  const initTurn = gameIdx % Math.max(players.length,1);
  const [revealed, setRevealed] = React.useState(() => new Array(TOTAL).fill(false));
  const [turn, setTurn] = React.useState(initTurn);
  const [scores, setScores] = React.useState({});
  const [bombPid, setBombPid] = React.useState(null);

  React.useEffect(() => {
    setRevealed(new Array(TOTAL).fill(false));
    setTurn(gameIdx % Math.max(players.length,1));
    setScores({}); setBombPid(null);
  }, [gameIdx]);

  const currentPlayer = players[turn % Math.max(players.length,1)];

  const tap = (i) => {
    if (revealed[i] || bombPid) return;
    const cell = grid[i];
    setRevealed(prev => { const n=[...prev]; n[i]=true; return n; });
    if (cell.type === 'bomb') {
      setBombPid(currentPlayer?.id);
    } else {
      const gain = cell.type==='pts' ? cell.v : 2;
      setScores(prev => ({...prev, [currentPlayer?.id]:(prev[currentPlayer?.id]||0)+gain}));
      setTurn(prev => (prev+1) % Math.max(players.length,1));
    }
  };

  const proceed = () => {
    const dm = {};
    if (bombPid) dm[bombPid] = 1;
    onAdvance && onAdvance(dm);
  };

  const loser = bombPid ? players.find(p=>p.id===bombPid) : null;
  const allSafe = !bombPid && revealed.every(Boolean);

  return (
    <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:12,width:'100%'}}>

      {/* Player score chips */}
      <div style={{display:'flex',gap:6,flexWrap:'wrap',justifyContent:'center',width:'100%'}}>
        {players.map(p => {
          const isActive = !bombPid && p.id===currentPlayer?.id;
          const isBombed = p.id===bombPid;
          const pts = scores[p.id]||0;
          return (
            <div key={p.id} style={{
              display:'flex', flexDirection:'column', alignItems:'center', gap:2,
              padding:'8px 10px', borderRadius:14, minWidth:58,
              background: isBombed?'#FFF0EE' : isActive?'rgba(255,255,255,0.92)':'rgba(255,255,255,0.5)',
              border:`2px solid ${isBombed?'#F87171':isActive?p.color:'transparent'}`,
              boxShadow: isActive ? '0 2px 8px rgba(0,0,0,0.10)' : 'none',
            }}>
              <div style={{width:34,height:34,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff'}}>
                {isBombed ? '💥' : p.name.charAt(0).toUpperCase()}
              </div>
              <div style={{fontFamily:'monospace',fontWeight:700,fontSize:14,color:isBombed?'#E55':T.ink,lineHeight:1}}>
                {isBombed ? '💣' : pts>0 ? pts : <span style={{color:T.inkSoft,fontWeight:400,fontSize:11}}>—</span>}
              </div>
            </div>
          );
        })}
      </div>

      {/* 4×4 Grid */}
      <div style={{display:'grid',gridTemplateColumns:`repeat(${COLS},1fr)`,gap:8,width:'100%'}}>
        {grid.map((cell,i) => {
          const isRev = revealed[i];
          const isBombCell = isRev && cell.type==='bomb';
          return (
            <div key={i} onClick={() => tap(i)} style={{
              aspectRatio:'1', borderRadius:12,
              background: isBombCell ? '#FFF0EE' : isRev ? '#fff' : '#F5ECD8',
              border: `2px solid ${isBombCell?'#F87171':'transparent'}`,
              display:'flex', alignItems:'center', justifyContent:'center',
              cursor: isRev||bombPid ? 'default' : 'pointer',
              boxShadow: isRev ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
              transition:'all .18s',
              animation: isRev ? 'popIn .2s' : 'none',
            }}>
              {isRev ? (
                cell.type==='pts'  ? <span style={{fontFamily:T.font,fontWeight:800,fontSize:17,color:'#50C882'}}>+{cell.v}</span>
                : cell.type==='star' ? <span style={{fontSize:20}}>⭐</span>
                : <span style={{fontSize:22}}>💣</span>
              ) : (
                <div style={{width:6,height:6,borderRadius:'50%',background:'rgba(0,0,0,0.16)'}}/>
              )}
            </div>
          );
        })}
      </div>

      {/* Turn indicator */}
      {!bombPid && !allSafe && (
        <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,textAlign:'center'}}>
          <span style={{fontWeight:700,color:currentPlayer?.color||T.ink}}>{currentPlayer?.name}</span>
          {' '}választ lapot
        </div>
      )}

      {/* All safe (no bombs left) */}
      {allSafe && (
        <div style={{width:'100%',padding:'12px 16px',borderRadius:14,background:'rgba(255,255,255,0.9)',boxShadow:T.shadow,textAlign:'center',animation:'popIn .3s'}}>
          <div style={{fontFamily:T.font,fontSize:14,fontWeight:700,color:T.mint,marginBottom:8}}>🎉 Senki nem találta a bombát!</div>
          <button onClick={proceed} style={{width:'100%',padding:'14px',background:T.mint,color:'#fff',fontFamily:T.font,fontWeight:700,fontSize:16,borderRadius:14,border:'none',cursor:'pointer',boxShadow:T.shadow}}>Új kör →</button>
        </div>
      )}

      {/* Bomb result */}
      {bombPid && loser && (
        <div style={{width:'100%',padding:'12px 16px',borderRadius:14,background:'rgba(255,255,255,0.9)',boxShadow:T.shadow,display:'flex',flexDirection:'column',gap:10,animation:'popIn .3s'}}>
          <div style={{fontFamily:T.font,fontSize:14,color:T.ink,textAlign:'center',lineHeight:1.5}}>
            <span style={{fontWeight:800,color:'#E55555'}}>{loser.name}</span> csapta fel a bombát — iszik egyet! 🙈
          </div>
          <button onClick={proceed} style={{width:'100%',padding:'14px',background:T.mint,color:'#fff',fontFamily:T.font,fontWeight:700,fontSize:16,borderRadius:14,border:'none',cursor:'pointer',boxShadow:T.shadow}}>
            Új kör →
          </button>
        </div>
      )}
    </div>
  );
}

"""

html = html.replace(
    'function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta, challenger, opponent }) {',
    NEW_COLLECT + 'function GameContent({ gameId, gameIdx, players, onAdvance, roomCode, mode, gameMeta, challenger, opponent }) {',
    1
)

# ── 2. Add collect to GameContent router ───────────────────────────────────────
html = html.replace(
    "  if (gameId === 'kopapir') return <KoPapirGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  return null;",
    "  if (gameId === 'kopapir') return <KoPapirGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  if (gameId === 'collect') return <CollectBoomGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  return null;",
    1
)

# ── 3. Version bump ────────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.21 · DNR · 2026.05.31 02:00',
    'Verzió 5.22 · DNR · 2026.05.31 03:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
