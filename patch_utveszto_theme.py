# -*- coding: utf-8 -*-
with open('index.html','r',encoding='utf-8') as f: src=f.read()

# 1. renderGrid: replace dark hardcoded cell colors with T.* theme
OLD1 = """          let bg = 'rgba(255,255,255,0.08)';
          let border = '1px solid rgba(255,255,255,0.1)';
          if (isStart) { bg='#22c55e33'; border='2px solid #22c55e'; }
          if (isEnd) { bg='#f59e0b33'; border='2px solid #f59e0b'; }
          if (inPath && !isStart && !isEnd) { bg='rgba(124,58,237,0.35)'; border='1px solid rgba(124,58,237,0.7)'; }
          if (isLast) { bg='rgba(124,58,237,0.6)'; border='2px solid #7c3aed'; }
          if (isAnimCur) { bg='rgba(251,191,36,0.7)'; border='2px solid #fbbf24'; }"""
NEW1 = """          const _pclr = (extraProps&&extraProps.pcolor) || T.mint;
          let bg = T.bgSoft;
          let border = '1.5px solid '+T.inkMute+'22';
          if (isStart) { bg=T.mint+'28'; border='2px solid '+T.mint; }
          if (isEnd) { bg=T.yellow+'28'; border='2px solid '+T.yellow; }
          if (inPath && !isStart && !isEnd) { bg=_pclr+'25'; border='1.5px solid '+_pclr+'66'; }
          if (isLast) { bg=_pclr+'55'; border='2px solid '+_pclr; }
          if (isAnimCur) { bg=T.yellow+'cc'; border='2px solid '+T.yellow; }"""
assert OLD1 in src, '1 not found'
src = src.replace(OLD1, NEW1, 1)

# 2. renderGrid cell: update onCellTap container style (background: bg, border)
OLD2 = """            <div key={idx} onClick={()=>onCellTap && onCellTap(idx)} style={{
              width:cellSize,height:cellSize,borderRadius:4,
              background:bg,border,
              display:'flex',alignItems:'center',justifyContent:'center',
              fontSize:cellSize>40?18:14,cursor:onCellTap?'pointer':'default',
              boxSizing:'border-box',position:'relative',transition:'background .1s',
            }}>"""
NEW2 = """            <div key={idx} onClick={()=>onCellTap && onCellTap(idx)} style={{
              width:cellSize,height:cellSize,borderRadius:6,
              background:bg,border,
              display:'flex',alignItems:'center',justifyContent:'center',
              fontSize:cellSize>40?18:14,cursor:onCellTap?'pointer':'default',
              boxSizing:'border-box',position:'relative',transition:'background .15s',
              boxShadow: isAnimCur ? '0 0 10px '+T.yellow+'88' : 'none',
            }}>"""
assert OLD2 in src, '2 not found'
src = src.replace(OLD2, NEW2, 1)

# 3. renderGrid signature: add extraProps param
OLD3 = "  const renderGrid = ({ board, showTraps, path, currentPath, onCellTap, animSeq, animStepVal, revMap }) => {"
NEW3 = "  const renderGrid = ({ board, showTraps, path, currentPath, onCellTap, animSeq, animStepVal, revMap, pcolor }) => {\n    const extraProps = { pcolor };"
assert OLD3 in src, '3 not found'
src = src.replace(OLD3, NEW3, 1)

# 4. Replace BG/YELLOW/wrapStyle constants
OLD4 = """  const BG = '#1e0a4e';
  const YELLOW = '#F5C518';
  const wrapStyle = {margin:'-16px',background:BG,minHeight:'100%',display:'flex',flexDirection:'column',padding:'10px 12px 14px',boxSizing:'border-box',color:'#fff',overflowY:'auto'};"""
NEW4 = "  const wrapStyle = {display:'flex',flexDirection:'column',gap:10,overflowY:'auto'};"
assert OLD4 in src, '4 not found'
src = src.replace(OLD4, NEW4, 1)

# 5. INTRO phase: full rewrite
OLD5 = """  // ── INTRO ──
  if (phase === 'intro') {
    return (
      <div style={wrapStyle}>
        <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:8}}>
          <span style={{fontSize:22}}>🗺️</span>
          <div>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:18,color:YELLOW,lineHeight:1}}>ÚTVESZTŐ</div>
            <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.5)'}}>2 fős csapda-pálya verseny</div>
          </div>
        </div>
        <div style={{background:'rgba(255,255,255,0.08)',borderRadius:12,padding:'10px 12px',marginBottom:8}}>
          <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.85)',lineHeight:1.55}}>
            {'1️⃣ Helyezz el 5 csapdát a saját 5×5-ös pályádon\\n2️⃣ Az ellenfél vakon rajzolja az útját\\n3️⃣ Animáció — csapdák feltárulnak\\n4️⃣ Kevesebb késés = győzelem 🏆'}
          </div>
        </div>
        <div style={{background:'rgba(255,255,255,0.05)',borderRadius:10,padding:'8px 12px',marginBottom:8}}>
          <div style={{fontFamily:T.font,fontSize:10,fontWeight:900,color:'rgba(255,255,255,0.35)',letterSpacing:1,marginBottom:6}}>CSAPDÁK</div>
          {TRAP_TYPES.map(t => (
            <div key={t.id} style={{display:'flex',alignItems:'center',gap:6,marginBottom:4}}>
              <span style={{fontSize:14,flexShrink:0}}>{t.emoji}</span>
              <span style={{fontFamily:T.font,fontWeight:700,fontSize:11,color:'rgba(255,255,255,0.8)',minWidth:72}}>{t.name}</span>
              <span style={{fontFamily:T.font,fontSize:10,color:'rgba(255,255,255,0.4)'}}>{t.desc}</span>
            </div>
          ))}
        </div>
        <div style={{display:'flex',alignItems:'center',gap:8,background:'rgba(124,58,237,0.2)',borderRadius:10,padding:'8px 12px',marginBottom:10,border:'1px solid rgba(124,58,237,0.35)'}}>
          <div style={{width:30,height:30,borderRadius:'50%',background:p1?.color||'#7c3aed',display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:13,color:'#fff',flexShrink:0}}>{(p1?.name||'P1').charAt(0).toUpperCase()}</div>
          <div style={{fontFamily:T.font,fontWeight:700,fontSize:13,color:'#fff',flex:1}}>{p1?.name||'Játékos 1'}</div>
          <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.4)'}}>vs</div>
          <div style={{fontFamily:T.font,fontWeight:700,fontSize:13,color:'#fff',flex:1,textAlign:'right'}}>{p2?.name||'Játékos 2'}</div>
          <div style={{width:30,height:30,borderRadius:'50%',background:p2?.color||'#0ea5e9',display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:13,color:'#fff',flexShrink:0}}>{(p2?.name||'P2').charAt(0).toUpperCase()}</div>
        </div>
        <button onClick={()=>setPhase('setup1')} style={{padding:'13px',borderRadius:14,border:'none',background:YELLOW,color:'#1a0a3e',fontFamily:T.font,fontWeight:900,fontSize:15,cursor:'pointer'}}>
          Kezdés → {p1?.name||'Játékos 1'} elhelyezi a csapdákat
        </button>
      </div>
    );
  }"""
NEW5 = """  // ── INTRO ──
  if (phase === 'intro') {
    return (
      <div style={wrapStyle}>
        {/* Szabályok */}
        <div style={{background:T.surface,borderRadius:16,padding:'14px 16px',boxShadow:T.shadow}}>
          <div style={{fontFamily:T.font,fontSize:10,fontWeight:900,color:T.inkSoft,letterSpacing:1.5,marginBottom:8}}>HOGYAN JÁTSZIK</div>
          {['1️⃣ Helyezz el 5 csapdát a saját 5×5-ös pályádon','2️⃣ Az ellenfél vakon rajzolja az útját','3️⃣ Animáció — csapdák feltárulnak','4️⃣ Kevesebb késés = győzelem 🏆'].map((s,i)=>(
            <div key={i} style={{fontFamily:T.font,fontSize:13,color:T.ink,lineHeight:1.6}}>{s}</div>
          ))}
        </div>
        {/* Csapdák */}
        <div style={{background:T.surface,borderRadius:16,padding:'12px 16px',boxShadow:T.shadow}}>
          <div style={{fontFamily:T.font,fontSize:10,fontWeight:900,color:T.inkSoft,letterSpacing:1.5,marginBottom:8}}>CSAPDÁK</div>
          {TRAP_TYPES.map(t => (
            <div key={t.id} style={{display:'flex',alignItems:'center',gap:10,paddingBottom:6,marginBottom:6,borderBottom:'1px solid '+T.inkMute+'15'}}>
              <span style={{fontSize:18,flexShrink:0}}>{t.emoji}</span>
              <span style={{fontFamily:T.font,fontWeight:800,fontSize:13,color:T.ink,minWidth:72}}>{t.name}</span>
              <span style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,flex:1}}>{t.desc}</span>
            </div>
          ))}
        </div>
        {/* Játékosok */}
        <div style={{background:T.surface,borderRadius:16,padding:'12px 16px',boxShadow:T.shadow,display:'flex',alignItems:'center',gap:10}}>
          <div style={{width:36,height:36,borderRadius:'50%',background:p1?.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>{(p1?.name||'P1').charAt(0).toUpperCase()}</div>
          <div style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink,flex:1}}>{p1?.name||'Játékos 1'}</div>
          <div style={{fontFamily:T.font,fontSize:12,fontWeight:700,color:T.inkSoft}}>vs</div>
          <div style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink,flex:1,textAlign:'right'}}>{p2?.name||'Játékos 2'}</div>
          <div style={{width:36,height:36,borderRadius:'50%',background:p2?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>{(p2?.name||'P2').charAt(0).toUpperCase()}</div>
        </div>
        <button onClick={()=>setPhase('setup1')} style={{padding:'15px',borderRadius:16,border:'none',background:T.mint,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:15,cursor:'pointer',boxShadow:'0 4px 14px -4px '+T.mint+'88'}}>
          Kezdés → {p1?.name||'Játékos 1'} elhelyezi a csapdákat
        </button>
      </div>
    );
  }"""
assert OLD5 in src, '5 not found'
src = src.replace(OLD5, NEW5, 1)

# 6. SETUP helper: trap buttons rewrite (shared for setup1 & setup2)
OLD6A = """          {TRAP_TYPES.map(t => {
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
        {selTrap && <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.5)',textAlign:'center',marginTop:4}}>
          {TRAP_TYPES.find(t=>t.id===selTrap)?.emoji} {TRAP_TYPES.find(t=>t.id===selTrap)?.desc} — koppints a pályára!
        </div>}
        <button onClick={()=>{setSelTrap(null);setPhase('setup2');}} disabled={placed===0} style={{
          marginTop:10,padding:'13px',borderRadius:14,border:'none',
          background:placed>0?YELLOW:'rgba(255,255,255,0.1)',color:placed>0?'#1a0a3e':'rgba(255,255,255,0.3)',
          fontFamily:T.font,fontWeight:900,fontSize:14,cursor:placed>0?'pointer':'default',
        }}>Kész ({placed}/5) → Add át {p2?.name||'Játékos 2'}-nek</button>"""
NEW6A = """          {TRAP_TYPES.map(t => {
            const used = board1.includes(t.id);
            const isSel = selTrap===t.id;
            return (
              <button key={t.id} onClick={()=>setSelTrap(isSel?null:t.id)} disabled={used && !isSel} style={{
                padding:'8px 12px',borderRadius:10,
                border:'2px solid '+(isSel?(p1?.color||T.mint):used?T.inkMute+'20':T.inkMute+'30'),
                background:isSel?(p1?.color||T.mint)+'18':used?T.bgSoft:T.surface,
                color:used&&!isSel?T.inkMute:isSel?(p1?.color||T.mint):T.ink,
                fontFamily:T.font,fontWeight:700,fontSize:12,cursor:used&&!isSel?'default':'pointer',
                boxShadow:isSel?'none':T.shadow,
              }}>
                {t.emoji} {t.name}{used?' ✓':''}
              </button>
            );
          })}
        </div>
        {selTrap && <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,textAlign:'center',marginTop:4,padding:'6px 12px',background:T.bgSoft,borderRadius:10}}>
          {TRAP_TYPES.find(t=>t.id===selTrap)?.emoji} {TRAP_TYPES.find(t=>t.id===selTrap)?.desc} — koppints a pályára!
        </div>}
        <button onClick={()=>{setSelTrap(null);setPhase('setup2');}} disabled={placed===0} style={{
          marginTop:4,padding:'14px',borderRadius:14,border:'none',
          background:placed>0?T.mint:T.bgSoft,color:placed>0?'#fff':T.inkMute,
          fontFamily:T.font,fontWeight:900,fontSize:14,cursor:placed>0?'pointer':'default',
          boxShadow:placed>0?'0 4px 14px -4px '+T.mint+'88':'none',
        }}>Kész ({placed}/5) → Add át {p2?.name||'Játékos 2'}-nek</button>"""
assert OLD6A in src, '6A not found'
src = src.replace(OLD6A, NEW6A, 1)

OLD6B = """          {TRAP_TYPES.map(t => {
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
        {selTrap && <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.5)',textAlign:'center',marginTop:4}}>
          {TRAP_TYPES.find(t=>t.id===selTrap)?.emoji} {TRAP_TYPES.find(t=>t.id===selTrap)?.desc} — koppints a pályára!
        </div>}
        <button onClick={()=>{setSelTrap(null);setPhase('path1');}} disabled={placed===0} style={{
          marginTop:10,padding:'13px',borderRadius:14,border:'none',
          background:placed>0?YELLOW:'rgba(255,255,255,0.1)',color:placed>0?'#1a0a3e':'rgba(255,255,255,0.3)',
          fontFamily:T.font,fontWeight:900,fontSize:14,cursor:placed>0?'pointer':'default',
        }}>Kész ({placed}/5) → Útvonal rajzolás</button>"""
NEW6B = """          {TRAP_TYPES.map(t => {
            const used = board2.includes(t.id);
            const isSel = selTrap===t.id;
            return (
              <button key={t.id} onClick={()=>setSelTrap(isSel?null:t.id)} disabled={used && !isSel} style={{
                padding:'8px 12px',borderRadius:10,
                border:'2px solid '+(isSel?(p2?.color||T.coral):used?T.inkMute+'20':T.inkMute+'30'),
                background:isSel?(p2?.color||T.coral)+'18':used?T.bgSoft:T.surface,
                color:used&&!isSel?T.inkMute:isSel?(p2?.color||T.coral):T.ink,
                fontFamily:T.font,fontWeight:700,fontSize:12,cursor:used&&!isSel?'default':'pointer',
                boxShadow:isSel?'none':T.shadow,
              }}>
                {t.emoji} {t.name}{used?' ✓':''}
              </button>
            );
          })}
        </div>
        {selTrap && <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,textAlign:'center',marginTop:4,padding:'6px 12px',background:T.bgSoft,borderRadius:10}}>
          {TRAP_TYPES.find(t=>t.id===selTrap)?.emoji} {TRAP_TYPES.find(t=>t.id===selTrap)?.desc} — koppints a pályára!
        </div>}
        <button onClick={()=>{setSelTrap(null);setPhase('path1');}} disabled={placed===0} style={{
          marginTop:4,padding:'14px',borderRadius:14,border:'none',
          background:placed>0?T.mint:T.bgSoft,color:placed>0?'#fff':T.inkMute,
          fontFamily:T.font,fontWeight:900,fontSize:14,cursor:placed>0?'pointer':'default',
          boxShadow:placed>0?'0 4px 14px -4px '+T.mint+'88':'none',
        }}>Kész ({placed}/5) → Útvonal rajzolás</button>"""
assert OLD6B in src, '6B not found'
src = src.replace(OLD6B, NEW6B, 1)

# 7. SETUP1 header
OLD7 = """        <div style={{fontFamily:T.font,fontWeight:900,fontSize:16,color:YELLOW,marginBottom:2}}>{p1?.name||'Játékos 1'} csapdái</div>
        <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.5)',marginBottom:10}}>Helyezz el {5-placed} csapdát! Start mezőre nem tehetsz.</div>
        {renderGrid({ board:board1, showTraps:true, onCellTap:(idx)=>placeOrRemove(board1,setBoard1,idx) })}"""
NEW7 = """        <div style={{background:T.surface,borderRadius:14,padding:'10px 14px',boxShadow:T.shadow,display:'flex',alignItems:'center',gap:10}}>
          <div style={{width:34,height:34,borderRadius:'50%',background:p1?.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff',flexShrink:0}}>{(p1?.name||'P1').charAt(0).toUpperCase()}</div>
          <div>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:T.ink}}>{p1?.name||'Játékos 1'} csapdái</div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>Helyezz el {5-placed} csapdát · Start mező védett</div>
          </div>
          <div style={{marginLeft:'auto',fontFamily:T.font,fontWeight:900,fontSize:16,color:T.mint}}>{placed}/5</div>
        </div>
        {renderGrid({ board:board1, showTraps:true, onCellTap:(idx)=>placeOrRemove(board1,setBoard1,idx), pcolor:p1?.color||T.mint })}"""
assert OLD7 in src, '7 not found'
src = src.replace(OLD7, NEW7, 1)

# 8. SETUP2 header
OLD8 = """        <div style={{fontFamily:T.font,fontWeight:900,fontSize:16,color:YELLOW,marginBottom:2}}>{p2?.name||'Játékos 2'} csapdái</div>
        <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.5)',marginBottom:10}}>Helyezz el {5-placed} csapdát! Az ellenfél nem látja.</div>
        {renderGrid({ board:board2, showTraps:true, onCellTap:(idx)=>placeOrRemove(board2,setBoard2,idx) })}"""
NEW8 = """        <div style={{background:T.surface,borderRadius:14,padding:'10px 14px',boxShadow:T.shadow,display:'flex',alignItems:'center',gap:10}}>
          <div style={{width:34,height:34,borderRadius:'50%',background:p2?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff',flexShrink:0}}>{(p2?.name||'P2').charAt(0).toUpperCase()}</div>
          <div>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:T.ink}}>{p2?.name||'Játékos 2'} csapdái</div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>Helyezz el {5-placed} csapdát · Az ellenfél nem látja</div>
          </div>
          <div style={{marginLeft:'auto',fontFamily:T.font,fontWeight:900,fontSize:16,color:T.mint}}>{placed}/5</div>
        </div>
        {renderGrid({ board:board2, showTraps:true, onCellTap:(idx)=>placeOrRemove(board2,setBoard2,idx), pcolor:p2?.color||T.coral })}"""
assert OLD8 in src, '8 not found'
src = src.replace(OLD8, NEW8, 1)

# 9. PATH 1 phase
OLD9 = """  // ── PATH 1 (P1 draws on P2's board — traps hidden) ──
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
  }"""
NEW9 = """  // ── PATH 1 (P1 draws on P2's board — traps hidden) ──
  if (phase === 'path1') {
    const pathDone = path1.length > 0 && path1[path1.length-1] === END_IDX;
    return (
      <div style={wrapStyle}>
        <div style={{background:T.surface,borderRadius:14,padding:'10px 14px',boxShadow:T.shadow,display:'flex',alignItems:'center',gap:10}}>
          <div style={{width:34,height:34,borderRadius:'50%',background:p1?.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff',flexShrink:0}}>{(p1?.name||'P1').charAt(0).toUpperCase()}</div>
          <div>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:T.ink}}>{p1?.name||'P1'} — rajzold az utadat!</div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>Ez {p2?.name||'P2'} pályája · csapdák rejtve 🚩→🏁</div>
          </div>
        </div>
        {renderGrid({ board:board2, showTraps:false, currentPath:path1, onCellTap:(idx)=>extendPath(setPath1, path1, idx), pcolor:p1?.color||T.mint })}
        <div style={{fontFamily:T.font,fontSize:13,color:pathDone?T.mint:T.inkSoft,textAlign:'center',fontWeight:pathDone?700:400}}>
          {path1.length===0 ? 'Koppints a 🚩 start mezőre!' : pathDone ? '✅ Célba értél!' : `${path1.length} lépés — érd el a 🏁 célt!`}
        </div>
        <div style={{display:'flex',gap:8}}>
          <button onClick={()=>setPath1([])} style={{flex:1,padding:'12px',borderRadius:12,border:'1.5px solid '+T.inkMute+'30',background:T.surface,color:T.inkSoft,fontFamily:T.font,fontWeight:700,fontSize:13,cursor:'pointer',boxShadow:T.shadow}}>
            ↺ Újra
          </button>
          <button onClick={()=>setPhase('path2')} disabled={!pathDone} style={{
            flex:2,padding:'13px',borderRadius:14,border:'none',
            background:pathDone?T.mint:T.bgSoft,color:pathDone?'#fff':T.inkMute,
            fontFamily:T.font,fontWeight:900,fontSize:14,cursor:pathDone?'pointer':'default',
            boxShadow:pathDone?'0 4px 14px -4px '+T.mint+'88':'none',
          }}>Kész → Add át {p2?.name||'P2'}-nek</button>
        </div>
      </div>
    );
  }"""
assert OLD9 in src, '9 not found'
src = src.replace(OLD9, NEW9, 1)

# 10. PATH 2 phase
OLD10 = """  // ── PATH 2 (P2 draws on P1's board — traps hidden) ──
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
  }"""
NEW10 = """  // ── PATH 2 (P2 draws on P1's board — traps hidden) ──
  if (phase === 'path2') {
    const pathDone = path2.length > 0 && path2[path2.length-1] === END_IDX;
    return (
      <div style={wrapStyle}>
        <div style={{background:T.surface,borderRadius:14,padding:'10px 14px',boxShadow:T.shadow,display:'flex',alignItems:'center',gap:10}}>
          <div style={{width:34,height:34,borderRadius:'50%',background:p2?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff',flexShrink:0}}>{(p2?.name||'P2').charAt(0).toUpperCase()}</div>
          <div>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:T.ink}}>{p2?.name||'P2'} — rajzold az utadat!</div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>Ez {p1?.name||'P1'} pályája · csapdák rejtve 🚩→🏁</div>
          </div>
        </div>
        {renderGrid({ board:board1, showTraps:false, currentPath:path2, onCellTap:(idx)=>extendPath(setPath2, path2, idx), pcolor:p2?.color||T.coral })}
        <div style={{fontFamily:T.font,fontSize:13,color:pathDone?T.mint:T.inkSoft,textAlign:'center',fontWeight:pathDone?700:400}}>
          {path2.length===0 ? 'Koppints a 🚩 start mezőre!' : pathDone ? '✅ Célba értél!' : `${path2.length} lépés — érd el a 🏁 célt!`}
        </div>
        <div style={{display:'flex',gap:8}}>
          <button onClick={()=>setPath2([])} style={{flex:1,padding:'12px',borderRadius:12,border:'1.5px solid '+T.inkMute+'30',background:T.surface,color:T.inkSoft,fontFamily:T.font,fontWeight:700,fontSize:13,cursor:'pointer',boxShadow:T.shadow}}>
            ↺ Újra
          </button>
          <button onClick={()=>{setPhase('reveal1');startReveal(1);}} disabled={!pathDone} style={{
            flex:2,padding:'13px',borderRadius:14,border:'none',
            background:pathDone?T.coral:T.bgSoft,color:pathDone?'#fff':T.inkMute,
            fontFamily:T.font,fontWeight:900,fontSize:14,cursor:pathDone?'pointer':'default',
            boxShadow:pathDone?'0 4px 14px -4px '+T.coral+'88':'none',
          }}>🎬 FELTÁRÁS!</button>
        </div>
      </div>
    );
  }"""
assert OLD10 in src, '10 not found'
src = src.replace(OLD10, NEW10, 1)

# 11. REVEAL 1 phase
OLD11 = """  // ── REVEAL 1 (P1's run on P2's board) ──
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
  }"""
NEW11 = """  // ── REVEAL 1 (P1's run on P2's board) ──
  if (phase === 'reveal1') {
    const seq = result1?.seq || [];
    const cur = animStep >= 0 && animStep < seq.length ? seq[animStep] : null;
    const animDoneHere = animStep >= seq.length;
    const trapNow = cur?.trap ? TRAP_TYPES.find(t=>t.id===cur.trap) : null;
    return (
      <div style={wrapStyle}>
        <div style={{background:T.surface,borderRadius:14,padding:'10px 14px',boxShadow:T.shadow,display:'flex',alignItems:'center',gap:10}}>
          <div style={{width:34,height:34,borderRadius:'50%',background:p1?.color||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff',flexShrink:0}}>{(p1?.name||'P1').charAt(0).toUpperCase()}</div>
          <div style={{flex:1}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:T.ink}}>{p1?.name||'P1'} fut</div>
            <div style={{fontFamily:T.font,fontSize:12,color:trapNow?T.coral:animDoneHere?T.mint:T.inkSoft,fontWeight:trapNow?700:400}}>
              {trapNow ? `${trapNow.emoji} ${trapNow.name}!` : animDoneHere ? '🏁 Megérkezett!' : '🏃 fut...'}
            </div>
          </div>
          {animDoneHere && <div style={{fontFamily:T.font,fontWeight:900,fontSize:13,color:result1?.korty>0?T.coral:T.mint}}>{result1?.korty>0?`+${result1.korty} 🍺`:'✅ tiszta'}</div>}
        </div>
        {renderGrid({ board:board2, showTraps:false, path:path1, animSeq:seq, animStepVal:animStep, revMap:revealMap, pcolor:p1?.color||T.mint })}
        {animDoneHere && (
          <button onClick={()=>{setAnimStep(-1);setRevealMap({});startReveal(2);setPhase('reveal2');}} style={{
            padding:'14px',borderRadius:14,border:'none',background:p2?.color||T.coral,color:'#fff',
            fontFamily:T.font,fontWeight:900,fontSize:14,cursor:'pointer',
            boxShadow:'0 4px 14px -4px '+(p2?.color||T.coral)+'88',
          }}>→ {p2?.name||'P2'} futása!</button>
        )}
      </div>
    );
  }"""
assert OLD11 in src, '11 not found'
src = src.replace(OLD11, NEW11, 1)

# 12. REVEAL 2 phase
OLD12 = """  // ── REVEAL 2 (P2's run on P1's board) ──
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
          <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.4)',textAlign:'center',marginTop:8}}>
            Az eredmény kiszámítása...
          </div>
        )}
      </div>
    );
  }"""
NEW12 = """  // ── REVEAL 2 (P2's run on P1's board) ──
  if (phase === 'reveal2') {
    const seq = result2?.seq || [];
    const cur = animStep >= 0 && animStep < seq.length ? seq[animStep] : null;
    const animDoneHere = animStep >= seq.length;
    const trapNow = cur?.trap ? TRAP_TYPES.find(t=>t.id===cur.trap) : null;
    return (
      <div style={wrapStyle}>
        <div style={{background:T.surface,borderRadius:14,padding:'10px 14px',boxShadow:T.shadow,display:'flex',alignItems:'center',gap:10}}>
          <div style={{width:34,height:34,borderRadius:'50%',background:p2?.color||T.coral,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:14,color:'#fff',flexShrink:0}}>{(p2?.name||'P2').charAt(0).toUpperCase()}</div>
          <div style={{flex:1}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:T.ink}}>{p2?.name||'P2'} fut</div>
            <div style={{fontFamily:T.font,fontSize:12,color:trapNow?T.coral:animDoneHere?T.mint:T.inkSoft,fontWeight:trapNow?700:400}}>
              {trapNow ? `${trapNow.emoji} ${trapNow.name}!` : animDoneHere ? '🏁 Megérkezett!' : '🏃 fut...'}
            </div>
          </div>
          {animDoneHere && <div style={{fontFamily:T.font,fontWeight:900,fontSize:13,color:result2?.korty>0?T.coral:T.mint}}>{result2?.korty>0?`+${result2.korty} 🍺`:'✅ tiszta'}</div>}
        </div>
        {renderGrid({ board:board1, showTraps:false, path:path2, animSeq:seq, animStepVal:animStep, revMap:revealMap, pcolor:p2?.color||T.coral })}
        {animDoneHere && (
          <div style={{background:T.bgSoft,borderRadius:12,padding:'10px 14px',textAlign:'center',fontFamily:T.font,fontSize:12,color:T.inkSoft}}>
            Az eredmény kiszámítása...
          </div>
        )}
      </div>
    );
  }"""
assert OLD12 in src, '12 not found'
src = src.replace(OLD12, NEW12, 1)

# 13. DONE phase
OLD13 = """  // ── DONE ──
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
  }"""
NEW13 = """  // ── DONE ──
  if (phase === 'done') {
    const r1 = result1 || {steps:999,korty:0};
    const r2 = result2 || {steps:999,korty:0};
    const p1wins = r1.steps <= r2.steps;
    const winner = p1wins ? p1 : p2;
    const loser = p1wins ? p2 : p1;
    const loserKorty = (p1wins ? r2.korty : r1.korty) + 2;
    return (
      <div style={{...wrapStyle,alignItems:'center',textAlign:'center'}}>
        <div style={{background:T.mint+'18',borderRadius:20,padding:'20px 16px',border:'2px solid '+T.mint+'44',width:'100%',boxSizing:'border-box',animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)'}}>
          <div style={{fontSize:44,marginBottom:8}}>🏆</div>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:T.mint}}>{winner?.name||'Győztes'} nyert!</div>
        </div>
        <div style={{display:'flex',gap:10,width:'100%'}}>
          {[{p:p1,r:r1,wins:p1wins},{p:p2,r:r2,wins:!p1wins}].map(({p,r,wins})=>(
            <div key={p?.id||Math.random()} style={{flex:1,background:T.surface,borderRadius:14,padding:'12px',boxShadow:T.shadow,border:'2px solid '+(wins?T.mint+'44':'transparent')}}>
              <div style={{width:32,height:32,borderRadius:'50%',background:p?.color||T.inkMute,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:13,color:'#fff',margin:'0 auto 6px'}}>{(p?.name||'P').charAt(0).toUpperCase()}</div>
              <div style={{fontFamily:T.font,fontWeight:800,fontSize:13,color:T.ink}}>{p?.name||'?'}</div>
              <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:2}}>{r.steps} lépés</div>
              <div style={{fontFamily:T.font,fontSize:11,color:T.inkMute}}>{r.korty} korty trap</div>
            </div>
          ))}
        </div>
        <div style={{background:T.coral+'18',borderRadius:16,padding:'16px 20px',border:'2px solid '+T.coral+'44',width:'100%',boxSizing:'border-box'}}>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:16,color:T.coral}}>{loser?.name||'Vesztes'} iszik!</div>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:24,color:T.coral,marginTop:4}}>{loserKorty} korty 🍺</div>
          <div style={{fontFamily:T.font,fontSize:11,color:T.inkMute,marginTop:4}}>{loserKorty-2} trap + 2 vesztes büntis</div>
        </div>
      </div>
    );
  }"""
assert OLD13 in src, '13 not found'
src = src.replace(OLD13, NEW13, 1)

# 14. version bump
assert 'v9.444' in src, 'version not found'
src = src.replace('v9.444', 'v9.445', 1)

with open('index.html','w',encoding='utf-8') as f: f.write(src)
print('OK')
