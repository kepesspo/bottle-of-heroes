with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Pass onResult to CollectBoomGame from GameContent
OLD_COLLECT = "if (gameId === 'collect') return <CollectBoomGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;"
NEW_COLLECT = "if (gameId === 'collect') return <CollectBoomGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;"
assert OLD_COLLECT in content, 'CollectBoomGame GameContent call not found'
content = content.replace(OLD_COLLECT, NEW_COLLECT, 1)

# 2. Replace the full CollectBoomGame function
OLD_GAME = '''function CollectBoomGame({ gameIdx, players, onAdvance }) {
  const COLS = 4, TOTAL = 16, MAX_POT = 10;

  // 3×1 + 2×2 + 1×3 = 10 kortyok, 2 bombs, 8 safe
  const grid = React.useMemo(() => {
    const cells = [
      {type:'bomb'}, {type:'bomb'},
      {type:'drink',v:1},{type:'drink',v:1},{type:'drink',v:1},
      {type:'drink',v:2},{type:'drink',v:2},
      {type:'drink',v:3},
      ...Array(8).fill({type:'safe'}),
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
  const [pot, setPot] = React.useState(0);
  const [bombPid, setBombPid] = React.useState(null);
  const [bombDrinks, setBombDrinks] = React.useState(0);

  React.useEffect(() => {
    setRevealed(new Array(TOTAL).fill(false));
    setTurn(gameIdx % Math.max(players.length,1));
    setPot(0); setBombPid(null); setBombDrinks(0);
  }, [gameIdx]);

  const currentPlayer = players[turn % Math.max(players.length,1)];

  const tap = (i) => {
    if (revealed[i] || bombPid) return;
    const cell = grid[i];
    setRevealed(prev => { const n=[...prev]; n[i]=true; return n; });
    if (cell.type === 'bomb') {
      setBombPid(currentPlayer?.id);
      setBombDrinks(pot);
    } else if (cell.type === 'drink') {
      setPot(prev => Math.min(prev + cell.v, MAX_POT));
      setTurn(prev => (prev+1) % Math.max(players.length,1));
    } else {
      setTurn(prev => (prev+1) % Math.max(players.length,1));
    }
  };

  const proceed = () => {
    const dm = {};
    if (bombPid && bombDrinks > 0) dm[bombPid] = bombDrinks;
    else if (bombPid) dm[bombPid] = 1;
    onAdvance && onAdvance(dm);
  };

  const loser = bombPid ? players.find(p=>p.id===bombPid) : null;
  const allSafe = !bombPid && revealed.every(Boolean);

  return (
    <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:12,width:'100%'}}>

      {/* Drink counter + player indicator */}
      {!bombPid && (
        <div style={{ display:'flex', gap:10, width:'100%' }}>
          <div style={{ display:'flex', alignItems:'center', gap:10, background:'rgba(255,255,255,0.92)', borderRadius:14, padding:'10px 14px', boxShadow:T.shadow, flex:1 }}>
            <div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.ink, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
              {(currentPlayer?.name||'?').charAt(0).toUpperCase()}
            </div>
            <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink }}>
              {currentPlayer?.name} választ
            </div>
            <div style={{ display:'flex', alignItems:'center', gap:3 }}>
              {players.map((p) => <div key={p.id} style={{ width:7, height:7, borderRadius:'50%', background: p.id===currentPlayer?.id ? (currentPlayer.color) : T.inkMute+'40' }} />)}
            </div>
          </div>
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', background: pot>=7 ? '#FFF0EE' : pot>=4 ? '#FFFBE6' : 'rgba(255,255,255,0.92)', borderRadius:14, padding:'8px 14px', boxShadow:T.shadow, flexShrink:0, minWidth:64, border:`2px solid ${pot>=7?'#F87171':pot>=4?'#F0C840':'transparent'}` }}>
            <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>GYŰJTVE</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color: pot>=7 ? '#E55' : pot>=4 ? '#C08020' : T.mint, lineHeight:1 }}>{pot}</div>
            <div style={{ fontFamily:T.font, fontSize:9, color:T.inkSoft }}>/ {MAX_POT}</div>
          </div>
        </div>
      )}

      {/* 4×4 Grid */}
      <div style={{display:'grid',gridTemplateColumns:`repeat(${COLS},1fr)`,gap:8,width:'100%'}}>
        {grid.map((cell,i) => {
          const isRev = revealed[i];
          const isBombCell = isRev && cell.type==='bomb';
          const isDrink = isRev && cell.type==='drink';
          return (
            <div key={i} onClick={() => tap(i)} style={{
              aspectRatio:'1', borderRadius:12,
              background: isBombCell ? '#FFF0EE' : isDrink ? '#EDF7F2' : isRev ? '#fff' : '#F5ECD8',
              border: `2px solid ${isBombCell?'#F87171':isDrink?'#50C882':'transparent'}`,
              display:'flex', alignItems:'center', justifyContent:'center',
              cursor: isRev||bombPid ? 'default' : 'pointer',
              boxShadow: isRev ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
              transition:'all .18s',
              animation: isRev ? 'popIn .2s' : 'none',
            }}>
              {isRev ? (
                isBombCell ? <span style={{fontSize:22}}>💣</span>
                : isDrink ? <span style={{fontFamily:T.font,fontWeight:800,fontSize:17,color:'#50C882'}}>+{cell.v}</span>
                : <span style={{fontSize:20}}>⭐</span>
              ) : (
                <div style={{width:6,height:6,borderRadius:'50%',background:'rgba(0,0,0,0.16)'}}/>
              )}
            </div>
          );
        })}
      </div>

      {/* All safe */}
      {allSafe && (
        <div style={{width:'100%',padding:'12px 16px',borderRadius:14,background:'rgba(255,255,255,0.9)',boxShadow:T.shadow,textAlign:'center',animation:'popIn .3s'}}>
          <div style={{fontFamily:T.font,fontSize:14,fontWeight:700,color:T.mint,marginBottom:8}}>🎉 Senki nem találta a bombát!</div>
          <button onClick={proceed} style={{width:'100%',padding:'14px',background:T.mint,color:'#fff',fontFamily:T.font,fontWeight:700,fontSize:16,borderRadius:14,border:'none',cursor:'pointer',boxShadow:T.shadow}}>Új kör →</button>
        </div>
      )}

      {/* Bomb result */}
      {bombPid && loser && (
        <div style={{width:'100%',padding:'12px 16px',borderRadius:14,background:'#FFF0EE',boxShadow:T.shadow,display:'flex',flexDirection:'column',gap:10,animation:'popIn .3s',border:'2px solid #F87171'}}>
          <div style={{fontFamily:T.font,fontSize:15,color:T.ink,textAlign:'center',lineHeight:1.6}}>
            <span style={{fontSize:28}}>💣</span><br/>
            <span style={{fontWeight:800,color:'#E55555'}}>{loser.name}</span> csapta fel a bombát!<br/>
            {bombDrinks > 0 ? <span style={{fontWeight:800,color:'#E55555',fontSize:18}}>{bombDrinks} kortyt iszik!</span> : <span>Iszik egyet!</span>}
          </div>
          <button onClick={proceed} style={{width:'100%',padding:'14px',background:T.mint,color:'#fff',fontFamily:T.font,fontWeight:700,fontSize:16,borderRadius:14,border:'none',cursor:'pointer',boxShadow:T.shadow}}>
            Új kör →
          </button>
        </div>
      )}
    </div>
  );
}'''

NEW_GAME = '''function CollectBoomGame({ gameIdx, players, onAdvance, onResult }) {
  const COLS = 4, TOTAL = 16, MAX_POT = 10;

  const grid = React.useMemo(() => {
    const cells = [
      {type:'bomb'}, {type:'bomb'},
      {type:'drink',v:1},{type:'drink',v:1},{type:'drink',v:1},
      {type:'drink',v:2},{type:'drink',v:2},
      {type:'drink',v:3},
      ...Array(8).fill({type:'safe'}),
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
  const [pot, setPot] = React.useState(0);
  const [bombPid, setBombPid] = React.useState(null);
  const [bombDrinks, setBombDrinks] = React.useState(0);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setRevealed(new Array(TOTAL).fill(false));
    setTurn(gameIdx % Math.max(players.length,1));
    setPot(0); setBombPid(null); setBombDrinks(0);
    advancedRef.current = false;
  }, [gameIdx]);

  const currentPlayer = players[turn % Math.max(players.length,1)];

  const tap = (i) => {
    if (revealed[i] || bombPid) return;
    const cell = grid[i];
    setRevealed(prev => { const n=[...prev]; n[i]=true; return n; });
    if (cell.type === 'bomb') {
      setBombPid(currentPlayer?.id);
      setBombDrinks(pot);
    } else if (cell.type === 'drink') {
      setPot(prev => Math.min(prev + cell.v, MAX_POT));
      setTurn(prev => (prev+1) % Math.max(players.length,1));
    } else {
      setTurn(prev => (prev+1) % Math.max(players.length,1));
    }
  };

  const loser = bombPid ? players.find(p=>p.id===bombPid) : null;
  const allRevealed = revealed.every(Boolean);
  const allSafe = !bombPid && allRevealed;

  // Auto-advance on bomb hit
  React.useEffect(() => {
    if (!bombPid || advancedRef.current) return;
    advancedRef.current = true;
    const drinks = bombDrinks > 0 ? bombDrinks : 1;
    const dm = { [bombPid]: drinks };
    onAdvance && onAdvance(dm);
    const loserPlayer = players.find(p=>p.id===bombPid);
    onResult && onResult({ correct: false, playerName: loserPlayer?.name, drinks });
  }, [bombPid]);

  // Auto-advance when all safe
  React.useEffect(() => {
    if (!allSafe || advancedRef.current) return;
    advancedRef.current = true;
    onAdvance && onAdvance({});
    onResult && onResult({ correct: true, playerName: null });
  }, [allSafe]);

  return (
    <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:12,width:'100%'}}>

      {/* Drink counter + player indicator */}
      {!bombPid && !allSafe && (
        <div style={{ display:'flex', gap:10, width:'100%' }}>
          <div style={{ display:'flex', alignItems:'center', gap:10, background:'rgba(255,255,255,0.92)', borderRadius:14, padding:'10px 14px', boxShadow:T.shadow, flex:1 }}>
            <div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.ink, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
              {(currentPlayer?.name||'?').charAt(0).toUpperCase()}
            </div>
            <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink }}>
              {currentPlayer?.name} választ
            </div>
            <div style={{ display:'flex', alignItems:'center', gap:3 }}>
              {players.map((p) => <div key={p.id} style={{ width:7, height:7, borderRadius:'50%', background: p.id===currentPlayer?.id ? (currentPlayer.color) : T.inkMute+'40' }} />)}
            </div>
          </div>
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', background: pot>=7 ? '#FFF0EE' : pot>=4 ? '#FFFBE6' : 'rgba(255,255,255,0.92)', borderRadius:14, padding:'8px 14px', boxShadow:T.shadow, flexShrink:0, minWidth:64, border:`2px solid ${pot>=7?'#F87171':pot>=4?'#F0C840':'transparent'}` }}>
            <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>GYŰJTVE</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color: pot>=7 ? '#E55' : pot>=4 ? '#C08020' : T.mint, lineHeight:1 }}>{pot}</div>
            <div style={{ fontFamily:T.font, fontSize:9, color:T.inkSoft }}>/ {MAX_POT}</div>
          </div>
        </div>
      )}

      {/* 4×4 Grid */}
      <div style={{display:'grid',gridTemplateColumns:`repeat(${COLS},1fr)`,gap:8,width:'100%'}}>
        {grid.map((cell,i) => {
          const isRev = revealed[i];
          const isBombCell = isRev && cell.type==='bomb';
          const isDrink = isRev && cell.type==='drink';
          return (
            <div key={i} onClick={() => tap(i)} style={{
              aspectRatio:'1', borderRadius:12,
              background: isBombCell ? '#FFF0EE' : isDrink ? '#EDF7F2' : isRev ? '#fff' : '#F5ECD8',
              border: `2px solid ${isBombCell?'#F87171':isDrink?'#50C882':'transparent'}`,
              display:'flex', alignItems:'center', justifyContent:'center',
              cursor: isRev||bombPid ? 'default' : 'pointer',
              boxShadow: isRev ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
              transition:'all .18s',
              animation: isRev ? 'popIn .2s' : 'none',
            }}>
              {isRev ? (
                isBombCell ? <span style={{fontSize:22}}>💣</span>
                : isDrink ? <span style={{fontFamily:T.font,fontWeight:800,fontSize:17,color:'#50C882'}}>+{cell.v}</span>
                : <span style={{fontSize:20}}>⭐</span>
              ) : (
                <div style={{width:6,height:6,borderRadius:'50%',background:'rgba(0,0,0,0.16)'}}/>
              )}
            </div>
          );
        })}
      </div>

      {/* Bomb result info (no button) */}
      {bombPid && loser && (
        <div style={{width:'100%',padding:'12px 16px',borderRadius:14,background:'#FFF0EE',boxShadow:T.shadow,textAlign:'center',animation:'popIn .3s',border:'2px solid #F87171'}}>
          <span style={{fontSize:28}}>💣</span>
          <div style={{fontFamily:T.font,fontSize:15,color:T.ink,lineHeight:1.6,marginTop:4}}>
            <span style={{fontWeight:800,color:'#E55555'}}>{loser.name}</span> csapta fel a bombát!<br/>
            {bombDrinks > 0
              ? <span style={{fontWeight:800,color:'#E55555',fontSize:18}}>{bombDrinks} kortyt iszik!</span>
              : <span>Iszik egyet!</span>}
          </div>
        </div>
      )}
    </div>
  );
}'''

assert OLD_GAME in content, 'CollectBoomGame old block not found'
content = content.replace(OLD_GAME, NEW_GAME, 1)

# Version bump
assert 'Verzió 5.72' in content
content = content.replace('Verzió 5.72', 'Verzió 5.73', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('OK — CollectBoom updated, v5.73')
