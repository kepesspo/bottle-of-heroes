#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

PATH = '/home/user/bottle-of-heroes/index.html'

with open(PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# ── Change 1: Add utveszto to GAMES array ────────────────────────────────────
OLD1 = "  { id:'quiz', roundTime:'mid', name:'Kvíz', difficulty:'közepes', category:'Egyéni', emoji:'🧠', symbol:null, img:IMGS['quiz_icon.png'], banner:IMGS['quiz_banner.png'], color:'#6366F1', desc:'Válaszolj a kérdésekre! Helyes válasz után pontot vehetsz — vagy tovább mersz menni és kortyokat gyűjthetsz osztogatásra. Ha tovább mégy és hibázol, te iszol annyit ahány kördnél vesztetted.' },"
NEW1 = "  { id:'utveszto', roundTime:'slow', name:'Útvesztő', difficulty:'nehéz', category:'Páros', emoji:'🗺️', symbol:null, img:null, banner:null, color:'#7c3aed', desc:'Csapdákat rejtettél el — az ellenfél vakon navigál a pályádon. Aki előbb ér célba, nyer. A vesztes iszik!' },\n  { id:'quiz', roundTime:'mid', name:'Kvíz', difficulty:'közepes', category:'Egyéni', emoji:'🧠', symbol:null, img:IMGS['quiz_icon.png'], banner:IMGS['quiz_banner.png'], color:'#6366F1', desc:'Válaszolj a kérdésekre! Helyes válasz után pontot vehetsz — vagy tovább mersz menni és kortyokat gyűjthetsz osztogatásra. Ha tovább mégy és hibázol, te iszol annyit ahány kördnél vesztetted.' },"
assert OLD1 in html, 'Change 1: target string not found'
html = html.replace(OLD1, NEW1, 1)

# ── Change 2: Add dispatch in GameContent ────────────────────────────────────
OLD2 = "  if (gameId === 'quiz') return <QuizGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} gameMeta={gameMeta} />;\n  if (gameId === 'beerpong') return <BeerPongGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} roomCode={roomCode} initialBpState={null} onSetHideFooter={onSetHideFooter} />;"
NEW2 = "  if (gameId === 'quiz') return <QuizGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} gameMeta={gameMeta} />;\n  if (gameId === 'utveszto') return <UtvesztoGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;\n  if (gameId === 'beerpong') return <BeerPongGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} roomCode={roomCode} initialBpState={null} onSetHideFooter={onSetHideFooter} />;"
assert OLD2 in html, 'Change 2: target string not found'
html = html.replace(OLD2, NEW2, 1)

# ── Change 3: Add UtvesztoGame component before QuizGame ─────────────────────
OLD3 = "function QuizGame({ gameIdx, challenger, players, onAdvance, onResult, onSetHideFooter, gameMeta }) {\n  const QUIZ_DB = {"

UTVESZTO_COMPONENT = r"""function UtvesztoGame({ gameIdx, challenger, players, onAdvance, onResult, onSetHideFooter }) {
  const GRID = 7;
  const START_IDX = 0;
  const END_IDX = GRID * GRID - 1;

  const TRAP_TYPES = [
    { id:'sorc', emoji:'🍺', name:'Sörcsokor', desc:'+2 korty + lassít' },
    { id:'fal',  emoji:'🧱', name:'Fal',       desc:'Ha átmegy: +3 korty + nagy késés' },
    { id:'alom', emoji:'💤', name:'Álom',       desc:'Nagy késés, megáll' },
    { id:'orv',  emoji:'🌀', name:'Örvény',    desc:'2 mezővel visszadobja' },
    { id:'tel',  emoji:'🔀', name:'Teleport',  desc:'Random pozícióra ugrik' },
  ];

  const p1 = challenger;
  const p2 = (players||[]).find(p => p.id !== challenger?.id) || (players||[])[0];

  // phase: intro | setup1 | setup2 | path1 | path2 | reveal1 | reveal2 | done
  const [phase, setPhase] = React.useState('intro');
  const [board1, setBoard1] = React.useState(Array(GRID*GRID).fill(null));
  const [board2, setBoard2] = React.useState(Array(GRID*GRID).fill(null));
  const [path1, setPath1] = React.useState([]); // P1 draws on board2
  const [path2, setPath2] = React.useState([]); // P2 draws on board1
  const [selTrap, setSelTrap] = React.useState(null);
  const [animStep, setAnimStep] = React.useState(-1);
  const [revealMap, setRevealMap] = React.useState({});
  const [result1, setResult1] = React.useState(null); // {steps, korty}
  const [result2, setResult2] = React.useState(null);
  const animRef = React.useRef(null);

  React.useEffect(() => { return () => { if (animRef.current) clearInterval(animRef.current); }; }, []);

  const cellRC = idx => [Math.floor(idx/GRID), idx%GRID];
  const adjacent = (a, b) => { const [ar,ac]=cellRC(a), [br,bc]=cellRC(b); return Math.abs(ar-br)+Math.abs(ac-bc)===1; };

  // Count placed traps on a board
  const trapCount = (board) => TRAP_TYPES.map(t => board.filter(c => c===t.id).length);

  // Setup: place trap
  const placeOrRemove = (board, setBoard, idx) => {
    if (idx === START_IDX || idx === END_IDX) return;
    if (!selTrap) return;
    if (board[idx] === selTrap) {
      const nb = [...board]; nb[idx] = null; setBoard(nb); return;
    }
    const alreadyHas = board[idx] !== null;
    const total = board.filter(Boolean).length;
    if (!alreadyHas && total >= 5) return;
    // only 1 of each type
    if (board.includes(selTrap) && !alreadyHas) return;
    const nb = [...board]; nb[idx] = selTrap; setBoard(nb);
  };

  // Path drawing: tap to extend/undo
  const extendPath = (setPath, currentPath, idx) => {
    if (currentPath.length === 0) {
      if (idx === START_IDX) setPath([START_IDX]);
      return;
    }
    const last = currentPath[currentPath.length-1];
    if (idx === last) return;
    if (currentPath.length >= 2 && idx === currentPath[currentPath.length-2]) {
      setPath(p => p.slice(0,-1)); return;
    }
    if (adjacent(last, idx) && !currentPath.includes(idx)) {
      setPath(p => [...p, idx]);
    }
  };

  // Build expanded animation sequence for a path on a board
  const buildAnim = (path, board) => {
    const seq = [];
    let korty = 0;
    for (let i = 0; i < path.length; i++) {
      const idx = path[i];
      const trap = board[idx];
      seq.push({ idx, trap, i });
      if (trap === 'sorc') {
        korty += 2;
        seq.push({ idx, pause:'sorc' });
        seq.push({ idx, pause:'sorc' });
      } else if (trap === 'fal') {
        korty += 3;
        seq.push({ idx, pause:'fal' });
        seq.push({ idx, pause:'fal' });
        seq.push({ idx, pause:'fal' });
        if (i > 0) seq.push({ idx:path[i-1], bounce:true });
        seq.push({ idx, bounce:true });
      } else if (trap === 'alom') {
        for (let j=0;j<4;j++) seq.push({ idx, pause:'alom' });
      } else if (trap === 'orv') {
        if (i >= 2) { seq.push({ idx:path[i-1], reverse:true }); seq.push({ idx:path[i-2], reverse:true }); }
        else if (i >= 1) { seq.push({ idx:path[i-1], reverse:true }); }
        seq.push({ idx, recover:true });
      } else if (trap === 'tel') {
        const candidates = path.filter((_,j) => j!==i);
        if (candidates.length > 0) {
          const jumpIdx = candidates[Math.floor(Math.random()*candidates.length)];
          seq.push({ idx:jumpIdx, teleport:true });
        }
      }
    }
    return { seq, korty };
  };

  const startReveal = (whichReveal) => {
    const isRev1 = whichReveal === 1;
    const path = isRev1 ? path1 : path2;
    const board = isRev1 ? board2 : board1;
    const { seq, korty } = buildAnim(path, board);
    setAnimStep(0);
    setRevealMap({});
    const setRes = isRev1 ? setResult1 : setResult2;
    setRes({ steps: seq.length, korty, seq });
    let step = 0;
    animRef.current = setInterval(() => {
      step++;
      if (step >= seq.length) {
        clearInterval(animRef.current);
        setAnimStep(seq.length);
        return;
      }
      setAnimStep(step);
      const item = seq[step];
      if (item.trap) setRevealMap(r => ({...r, [item.idx]: item.trap}));
    }, 350);
  };

  // Grid cell size
  const cellSize = Math.floor((Math.min(340, window.innerWidth - 32)) / GRID);

  const renderGrid = ({ board, showTraps, path, currentPath, onCellTap, animSeq, animStepVal, revMap }) => {
    return (
      <div style={{display:'grid',gridTemplateColumns:`repeat(${GRID},${cellSize}px)`,gridTemplateRows:`repeat(${GRID},${cellSize}px)`,gap:2,margin:'0 auto'}}>
        {Array.from({length:GRID*GRID}).map((_,idx) => {
          const isStart = idx===START_IDX, isEnd = idx===END_IDX;
          const trap = board[idx];
          const inPath = (currentPath||path||[]).includes(idx);
          const isLast = currentPath && currentPath[currentPath.length-1]===idx;
          const isAnimCur = animSeq && animStepVal >= 0 && animSeq[Math.min(animStepVal, animSeq.length-1)]?.idx === idx;
          const revealed = revMap && revMap[idx];
          const trapToShow = showTraps ? trap : (revealed || null);
          const t = trapToShow ? TRAP_TYPES.find(t=>t.id===trapToShow) : null;

          let bg = 'rgba(255,255,255,0.08)';
          let border = '1px solid rgba(255,255,255,0.1)';
          if (isStart) { bg='#22c55e33'; border='2px solid #22c55e'; }
          if (isEnd) { bg='#f59e0b33'; border='2px solid #f59e0b'; }
          if (inPath && !isStart && !isEnd) { bg='rgba(124,58,237,0.35)'; border='1px solid rgba(124,58,237,0.7)'; }
          if (isLast) { bg='rgba(124,58,237,0.6)'; border='2px solid #7c3aed'; }
          if (isAnimCur) { bg='rgba(251,191,36,0.7)'; border='2px solid #fbbf24'; }

          return (
            <div key={idx} onClick={()=>onCellTap && onCellTap(idx)} style={{
              width:cellSize,height:cellSize,borderRadius:4,
              background:bg,border,
              display:'flex',alignItems:'center',justifyContent:'center',
              fontSize:cellSize>40?18:14,cursor:onCellTap?'pointer':'default',
              boxSizing:'border-box',position:'relative',transition:'background .1s',
            }}>
              {isAnimCur ? '🏃' : t ? t.emoji : isStart ? '🚩' : isEnd ? '🏁' : ''}
            </div>
          );
        })}
      </div>
    );
  };

  const BG = '#1e0a4e';
  const YELLOW = '#F5C518';
  const wrapStyle = {margin:'-16px',background:BG,minHeight:'100%',display:'flex',flexDirection:'column',padding:'12px 12px 16px',boxSizing:'border-box',color:'#fff'};

  // ── INTRO ──
  if (phase === 'intro') {
    return (
      <div style={wrapStyle}>
        <div style={{textAlign:'center',fontSize:36,marginBottom:8}}>🗺️</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:YELLOW,textAlign:'center',marginBottom:4}}>ÚTVESZTŐ</div>
        <div style={{fontFamily:T.font,fontSize:13,color:'rgba(255,255,255,0.65)',textAlign:'center',marginBottom:16}}>2 fős csapda-pálya verseny</div>
        <div style={{background:'rgba(255,255,255,0.08)',borderRadius:14,padding:'14px 16px',marginBottom:12}}>
          <div style={{fontFamily:T.font,fontWeight:700,fontSize:13,color:'rgba(255,255,255,0.9)',lineHeight:1.6}}>
            {'1️⃣ Mindkét játékos elhelyez 5 csapdát a saját 7×7-es pályáján\n2️⃣ Az ellenfél vakon megrajzolja az útvonalát\n3️⃣ Animáció — csapdák feltárulnak\n4️⃣ Aki kevesebb késéssel ér célba, nyer! 🏆'}
          </div>
        </div>
        <div style={{display:'flex',gap:8,marginBottom:16,flexWrap:'wrap'}}>
          {TRAP_TYPES.map(t => (
            <div key={t.id} style={{background:'rgba(255,255,255,0.1)',borderRadius:10,padding:'6px 10px',fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.8)'}}>
              {t.emoji} {t.name}
            </div>
          ))}
        </div>
        <div style={{display:'flex',alignItems:'center',gap:10,background:'rgba(124,58,237,0.2)',borderRadius:12,padding:'10px 14px',marginBottom:16,border:'1px solid rgba(124,58,237,0.4)'}}>
          <div style={{width:36,height:36,borderRadius:'50%',background:p1?.color||'#7c3aed',display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>{(p1?.name||'P1').charAt(0).toUpperCase()}</div>
          <div style={{fontFamily:T.font,fontWeight:700,fontSize:14,color:'#fff'}}>{p1?.name||'Játékos 1'}</div>
          <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.5)',marginLeft:'auto'}}>vs</div>
          <div style={{fontFamily:T.font,fontWeight:700,fontSize:14,color:'#fff'}}>{p2?.name||'Játékos 2'}</div>
          <div style={{width:36,height:36,borderRadius:'50%',background:p2?.color||'#0ea5e9',display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>{(p2?.name||'P2').charAt(0).toUpperCase()}</div>
        </div>
        <button onClick={()=>setPhase('setup1')} style={{padding:'15px',borderRadius:14,border:'none',background:YELLOW,color:'#1a0a3e',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer',marginTop:'auto'}}>
          Kezdés → {p1?.name||'Játékos 1'} elhelyezi a csapdákat
        </button>
      </div>
    );
  }

  // ── SETUP 1 (P1 places traps) ──
  if (phase === 'setup1') {
    const placed = board1.filter(Boolean).length;
    const canPlace = (id) => !board1.includes(id) && placed < 5;
    return (
      <div style={wrapStyle}>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:16,color:YELLOW,marginBottom:2}}>{p1?.name||'Játékos 1'} csapdái</div>
        <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.5)',marginBottom:10}}>Helyezz el {5-placed} csapdát! Start mezőre nem tehetsz.</div>
        {renderGrid({ board:board1, showTraps:true, onCellTap:(idx)=>placeOrRemove(board1,setBoard1,idx) })}
        <div style={{display:'flex',gap:6,marginTop:10,flexWrap:'wrap',justifyContent:'center'}}>
          {TRAP_TYPES.map(t => {
            const used = board1.includes(t.id);
            const isSel = selTrap===t.id;
            return (
              <button key={t.id} onClick={()=>setSelTrap(isSel?null:t.id)} disabled={used && !isSel} style={{
                padding:'8px 10px',borderRadius:10,border:'2px solid '+(isSel?YELLOW:'rgba(255,255,255,0.2)'),
                background:isSel?YELLOW+'22':used?'rgba(255,255,255,0.03)':'rgba(255,255,255,0.1)',
                color:used&&!isSel?'rgba(255,255,255,0.25)':isSel?YELLOW:'rgba(255,255,255,0.85)',
                fontFamily:T.font,fontWeight:700,fontSize:12,cursor:used&&!isSel?'default':'pointer',
              }}>
                {t.emoji} {t.name}{used?' ✓':''}
              </button>
            );
          })}
        </div>
        <button onClick={()=>{setSelTrap(null);setPhase('setup2');}} disabled={placed===0} style={{
          marginTop:10,padding:'13px',borderRadius:14,border:'none',
          background:placed>0?YELLOW:'rgba(255,255,255,0.1)',color:placed>0?'#1a0a3e':'rgba(255,255,255,0.3)',
          fontFamily:T.font,fontWeight:900,fontSize:14,cursor:placed>0?'pointer':'default',
        }}>Kész ({placed}/5) → Add át {p2?.name||'Játékos 2'}-nek</button>
      </div>
    );
  }

  // ── SETUP 2 (P2 places traps) ──
  if (phase === 'setup2') {
    const placed = board2.filter(Boolean).length;
    return (
      <div style={wrapStyle}>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:16,color:YELLOW,marginBottom:2}}>{p2?.name||'Játékos 2'} csapdái</div>
        <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.5)',marginBottom:10}}>Helyezz el {5-placed} csapdát! Az ellenfél nem látja.</div>
        {renderGrid({ board:board2, showTraps:true, onCellTap:(idx)=>placeOrRemove(board2,setBoard2,idx) })}
        <div style={{display:'flex',gap:6,marginTop:10,flexWrap:'wrap',justifyContent:'center'}}>
          {TRAP_TYPES.map(t => {
            const used = board2.includes(t.id);
            const isSel = selTrap===t.id;
            return (
              <button key={t.id} onClick={()=>setSelTrap(isSel?null:t.id)} disabled={used && !isSel} style={{
                padding:'8px 10px',borderRadius:10,border:'2px solid '+(isSel?YELLOW:'rgba(255,255,255,0.2)'),
                background:isSel?YELLOW+'22':used?'rgba(255,255,255,0.03)':'rgba(255,255,255,0.1)',
                color:used&&!isSel?'rgba(255,255,255,0.25)':isSel?YELLOW:'rgba(255,255,255,0.85)',
                fontFamily:T.font,fontWeight:700,fontSize:12,cursor:used&&!isSel?'default':'pointer',
              }}>
                {t.emoji} {t.name}{used?' ✓':''}
              </button>
            );
          })}
        </div>
        <button onClick={()=>{setSelTrap(null);setPhase('path1');}} disabled={placed===0} style={{
          marginTop:10,padding:'13px',borderRadius:14,border:'none',
          background:placed>0?YELLOW:'rgba(255,255,255,0.1)',color:placed>0?'#1a0a3e':'rgba(255,255,255,0.3)',
          fontFamily:T.font,fontWeight:900,fontSize:14,cursor:placed>0?'pointer':'default',
        }}>Kész ({placed}/5) → Útvonal rajzolás</button>
      </div>
    );
  }

  // ── PATH 1 (P1 draws on P2's board — traps hidden) ──
  if (phase === 'path1') {
    const pathDone = path1.length > 0 && path1[path1.length-1] === END_IDX;
    return (
      <div style={wrapStyle}>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:16,color:YELLOW,marginBottom:2}}>{p1?.name||'P1'} — rajzold az utadat!</div>
        <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.5)',marginBottom:10}}>
          Ez {p2?.name||'P2'} pályája. Csapdák rejtve! 🚩 → 🏁
        </div>
        {renderGrid({ board:board2, showTraps:false, currentPath:path1, onCellTap:(idx)=>extendPath(setPath1, path1, idx) })}
        <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.45)',textAlign:'center',marginTop:8}}>
          {path1.length===0 ? 'Koppints a 🚩 start mezőre!' : pathDone ? '✅ Célba értél!' : `${path1.length} lépés — érd el a 🏁 célt!`}
        </div>
        <div style={{display:'flex',gap:8,marginTop:10}}>
          <button onClick={()=>setPath1([])} style={{flex:1,padding:'11px',borderRadius:12,border:'1px solid rgba(255,255,255,0.2)',background:'rgba(255,255,255,0.05)',color:'rgba(255,255,255,0.6)',fontFamily:T.font,fontWeight:700,fontSize:13,cursor:'pointer'}}>
            ↺ Újra
          </button>
          <button onClick={()=>setPhase('path2')} disabled={!pathDone} style={{
            flex:2,padding:'13px',borderRadius:14,border:'none',
            background:pathDone?YELLOW:'rgba(255,255,255,0.1)',color:pathDone?'#1a0a3e':'rgba(255,255,255,0.3)',
            fontFamily:T.font,fontWeight:900,fontSize:14,cursor:pathDone?'pointer':'default',
          }}>Kész → Add át {p2?.name||'P2'}-nek</button>
        </div>
      </div>
    );
  }

  // ── PATH 2 (P2 draws on P1's board — traps hidden) ──
  if (phase === 'path2') {
    const pathDone = path2.length > 0 && path2[path2.length-1] === END_IDX;
    return (
      <div style={wrapStyle}>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:16,color:YELLOW,marginBottom:2}}>{p2?.name||'P2'} — rajzold az utadat!</div>
        <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.5)',marginBottom:10}}>
          Ez {p1?.name||'P1'} pályája. Csapdák rejtve! 🚩 → 🏁
        </div>
        {renderGrid({ board:board1, showTraps:false, currentPath:path2, onCellTap:(idx)=>extendPath(setPath2, path2, idx) })}
        <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.45)',textAlign:'center',marginTop:8}}>
          {path2.length===0 ? 'Koppints a 🚩 start mezőre!' : pathDone ? '✅ Célba értél!' : `${path2.length} lépés — érd el a 🏁 célt!`}
        </div>
        <div style={{display:'flex',gap:8,marginTop:10}}>
          <button onClick={()=>setPath2([])} style={{flex:1,padding:'11px',borderRadius:12,border:'1px solid rgba(255,255,255,0.2)',background:'rgba(255,255,255,0.05)',color:'rgba(255,255,255,0.6)',fontFamily:T.font,fontWeight:700,fontSize:13,cursor:'pointer'}}>
            ↺ Újra
          </button>
          <button onClick={()=>{setPhase('reveal1');startReveal(1);}} disabled={!pathDone} style={{
            flex:2,padding:'13px',borderRadius:14,border:'none',
            background:pathDone?'#7c3aed':'rgba(255,255,255,0.1)',color:pathDone?'#fff':'rgba(255,255,255,0.3)',
            fontFamily:T.font,fontWeight:900,fontSize:14,cursor:pathDone?'pointer':'default',
          }}>🎬 FELTÁRÁS!</button>
        </div>
      </div>
    );
  }

  // ── REVEAL 1 (P1's run on P2's board) ──
  if (phase === 'reveal1') {
    const seq = result1?.seq || [];
    const cur = animStep >= 0 && animStep < seq.length ? seq[animStep] : null;
    const animDoneHere = animStep >= seq.length;
    return (
      <div style={wrapStyle}>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:15,color:YELLOW,marginBottom:2,textAlign:'center'}}>{p1?.name||'P1'} fut — {p2?.name||'P2'} pályáján</div>
        <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.45)',textAlign:'center',marginBottom:8}}>
          {cur?.trap ? `${TRAP_TYPES.find(t=>t.id===cur.trap)?.emoji} ${TRAP_TYPES.find(t=>t.id===cur.trap)?.name}!` : animDoneHere ? '🏁 Megérkezett!' : '🏃 fut...'}
        </div>
        {renderGrid({ board:board2, showTraps:false, path:path1, animSeq:seq, animStepVal:animStep, revMap:revealMap })}
        {animDoneHere && (
          <div style={{background:'rgba(255,255,255,0.08)',borderRadius:12,padding:'12px 16px',marginTop:10,textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:700,fontSize:13,color:'rgba(255,255,255,0.9)'}}>
              {result1?.korty > 0 ? `☕ ${result1.korty} korty büntis` : '✅ Büntetés nélkül!'} · {seq.length} lépés összesen
            </div>
          </div>
        )}
        {animDoneHere && (
          <button onClick={()=>{setAnimStep(-1);setRevealMap({});startReveal(2);setPhase('reveal2');}} style={{
            marginTop:10,padding:'13px',borderRadius:14,border:'none',background:'#7c3aed',color:'#fff',
            fontFamily:T.font,fontWeight:900,fontSize:14,cursor:'pointer',
          }}>→ {p2?.name||'P2'} futása!</button>
        )}
      </div>
    );
  }

  // ── REVEAL 2 (P2's run on P1's board) ──
  if (phase === 'reveal2') {
    const seq = result2?.seq || [];
    const cur = animStep >= 0 && animStep < seq.length ? seq[animStep] : null;
    const animDoneHere = animStep >= seq.length;
    const goToResult = () => {
      const r1 = result1 || {steps:999, korty:0};
      const r2 = result2 || {steps:999, korty:0};
      const winnerIsP1 = r1.steps <= r2.steps;
      const loserKorty = winnerIsP1 ? (r2.korty + 2) : (r1.korty + 2);
      const loserId = winnerIsP1 ? p2?.id : p1?.id;
      if (onAdvance && loserId) onAdvance({[loserId]: loserKorty});
      const winner = winnerIsP1 ? (p1?.name||'P1') : (p2?.name||'P2');
      const loser = winnerIsP1 ? (p2?.name||'P2') : (p1?.name||'P1');
      if (onResult) onResult({ correct: winnerIsP1, playerName: winner, drinks: loserKorty, subtitle: `${loser} iszik ${loserKorty} kortyot!` });
      setPhase('done');
    };
    return (
      <div style={wrapStyle}>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:15,color:YELLOW,marginBottom:2,textAlign:'center'}}>{p2?.name||'P2'} fut — {p1?.name||'P1'} pályáján</div>
        <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.45)',textAlign:'center',marginBottom:8}}>
          {cur?.trap ? `${TRAP_TYPES.find(t=>t.id===cur.trap)?.emoji} ${TRAP_TYPES.find(t=>t.id===cur.trap)?.name}!` : animDoneHere ? '🏁 Megérkezett!' : '🏃 fut...'}
        </div>
        {renderGrid({ board:board1, showTraps:false, path:path2, animSeq:seq, animStepVal:animStep, revMap:revealMap })}
        {animDoneHere && (
          <div style={{background:'rgba(255,255,255,0.08)',borderRadius:12,padding:'12px 16px',marginTop:10,textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:700,fontSize:13,color:'rgba(255,255,255,0.9)'}}>
              {result2?.korty > 0 ? `☕ ${result2.korty} korty büntis` : '✅ Büntetés nélkül!'} · {seq.length} lépés összesen
            </div>
          </div>
        )}
        {animDoneHere && (
          <button onClick={goToResult} style={{
            marginTop:10,padding:'13px',borderRadius:14,border:'none',background:YELLOW,color:'#1a0a3e',
            fontFamily:T.font,fontWeight:900,fontSize:15,cursor:'pointer',
          }}>🏆 Eredmény!</button>
        )}
      </div>
    );
  }

  // ── DONE ──
  if (phase === 'done') {
    const r1 = result1 || {steps:999,korty:0};
    const r2 = result2 || {steps:999,korty:0};
    const p1wins = r1.steps <= r2.steps;
    const winner = p1wins ? p1 : p2;
    const loser = p1wins ? p2 : p1;
    const loserKorty = (p1wins ? r2.korty : r1.korty) + 2;
    return (
      <div style={{...wrapStyle,alignItems:'center',justifyContent:'center',textAlign:'center'}}>
        <div style={{fontSize:52,marginBottom:12}}>🏆</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:YELLOW,marginBottom:4}}>{winner?.name||'Győztes'} nyert!</div>
        <div style={{display:'flex',gap:10,marginBottom:16,width:'100%',maxWidth:280}}>
          <div style={{flex:1,background:'rgba(34,197,94,0.15)',borderRadius:12,padding:'12px',border:'1.5px solid rgba(34,197,94,0.4)'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:'#22c55e'}}>{p1?.name||'P1'}</div>
            <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.6)'}}>{r1.steps} lépés</div>
            <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.4)'}}>{r1.korty} korty</div>
          </div>
          <div style={{flex:1,background:'rgba(34,197,94,0.15)',borderRadius:12,padding:'12px',border:'1.5px solid rgba(34,197,94,0.4)'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:'#22c55e'}}>{p2?.name||'P2'}</div>
            <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.6)'}}>{r2.steps} lépés</div>
            <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.4)'}}>{r2.korty} korty</div>
          </div>
        </div>
        <div style={{background:'rgba(239,68,68,0.15)',borderRadius:16,padding:'16px 20px',border:'1.5px solid rgba(239,68,68,0.4)',marginBottom:8,width:'100%',maxWidth:280,boxSizing:'border-box'}}>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:16,color:'#ef4444'}}>{loser?.name||'Vesztes'} iszik!</div>
          <div style={{fontFamily:T.font,fontWeight:700,fontSize:20,color:'#ef4444',marginTop:4}}>{loserKorty} korty 🍺</div>
          <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.4)',marginTop:4}}>({loserKorty-2} trap + 2 vesztes büntis)</div>
        </div>
      </div>
    );
  }

  return null;
}

"""

NEW3 = UTVESZTO_COMPONENT + "function QuizGame({ gameIdx, challenger, players, onAdvance, onResult, onSetHideFooter, gameMeta }) {\n  const QUIZ_DB = {"

assert OLD3 in html, 'Change 3: target string not found'
html = html.replace(OLD3, NEW3, 1)

# ── Change 4: Version bump ────────────────────────────────────────────────────
OLD4 = 'v9.432'
NEW4 = 'v9.433'
assert OLD4 in html, 'Change 4: version string not found'
html = html.replace(OLD4, NEW4)

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print('OK')
