# -*- coding: utf-8 -*-
with open('index.html','r',encoding='utf-8') as f: src=f.read()

# 1. Add gifts state next to distributeTarget
OLD1 = "  const [distributeTarget, setDistributeTarget] = React.useState(null);"
NEW1 = "  const [distributeTarget, setDistributeTarget] = React.useState(null);\n  const [gifts, setGifts] = React.useState({});"
assert OLD1 in src, '1 not found'
src = src.replace(OLD1, NEW1, 1)

# 2. Reset gifts on gameIdx change
OLD2 = "  React.useEffect(() => { setStreak(0); setQIdx(0); setGiftPool(null); }, [gameIdx]);"
NEW2 = "  React.useEffect(() => { setStreak(0); setQIdx(0); setGiftPool(null); setGifts({}); setDistributeTarget(null); }, [gameIdx]);"
assert OLD2 in src, '2 not found'
src = src.replace(OLD2, NEW2, 1)

# 3. bankIt: init gifts when entering distribute
OLD3 = """  const bankIt = () => {
    if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0, subtitle: kortyok > 0 ? `+1 pont — ${kortyok} kortyt oszt ki!` : '+1 pont!' });
    if (kortyok > 0) { setPhase('distribute'); }
    else { setPhase('done'); }
  };"""
NEW3 = """  const bankIt = () => {
    if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0, subtitle: kortyok > 0 ? `+1 pont — ${kortyok} kortyt oszt ki!` : '+1 pont!' });
    if (kortyok > 0) {
      const initGifts = {};
      players.filter(p => p.id !== challenger?.id).forEach(p => { initGifts[p.id] = 0; });
      setGifts(initGifts);
      setPhase('distribute');
    } else { setPhase('done'); }
  };"""
assert OLD3 in src, '3 not found'
src = src.replace(OLD3, NEW3, 1)

# 4. Replace entire distribute phase UI with Lóverseny-style
OLD4 = """  if (phase === 'distribute') {
    const others = players.filter(p => p.id !== challenger?.id);
    return (
      <div style={{display:'flex',flexDirection:'column',gap:10}}>
        <div style={{background:T.surface,borderRadius:16,padding:'14px 16px',boxShadow:T.shadow,textAlign:'center'}}>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:pColor,lineHeight:1}}>🍺 {kortyok} korty</div>
          <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:4}}>{pName} kiosztja — kire?</div>
        </div>
        <div style={{display:'flex',flexDirection:'column',gap:8}}>
          {others.map(p => {
            const isSel = distributeTarget === p.id;
            return (
              <div key={p.id} onClick={()=>setDistributeTarget(isSel ? null : p.id)} style={{
                display:'flex',alignItems:'center',gap:12,padding:'12px 14px',
                background: isSel ? p.color+'18' : T.surface,
                border:'2px solid '+(isSel ? p.color : 'transparent'),
                borderRadius:14,cursor:'pointer',transition:'all .15s',
                boxShadow:T.shadow,
              }}>
                <div style={{width:40,height:40,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:16,color:'#fff',flexShrink:0}}>
                  {(p.name||'?').charAt(0).toUpperCase()}
                </div>
                <span style={{fontFamily:T.font,fontWeight:700,fontSize:15,color:T.ink,flex:1}}>{p.name}</span>
                <span style={{fontFamily:T.font,fontSize:11,fontWeight:900,color:isSel?p.color:T.inkSoft,letterSpacing:0.5}}>
                  {isSel ? '✓ KIVÁLASZTVA' : 'KIVÁLASZT'}
                </span>
              </div>
            );
          })}
        </div>
        {distributeTarget && (
          <div style={{background:pColor+'12',borderRadius:14,padding:'14px 16px',border:'1.5px solid '+pColor+'44',textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:15,color:T.ink,marginBottom:4}}>
              {players.find(p=>p.id===distributeTarget)?.name} iszik {kortyok} kortyot 🍺
            </div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginBottom:10}}>{pName} bezsebelte a kört</div>
            <button onClick={()=>distribute(distributeTarget)} style={{
              width:'100%',padding:'13px',borderRadius:12,border:'none',
              background:pColor,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:15,cursor:'pointer',
              boxShadow:'0 4px 14px -4px '+pColor+'88',
            }}>Megerősítés ✓</button>
          </div>
        )}
      </div>
    );
  }"""
NEW4 = """  if (phase === 'distribute') {
    const others = players.filter(p => p.id !== challenger?.id);
    const totalGifted = Object.values(gifts).reduce((s,v)=>s+v,0);
    const remaining = kortyok - totalGifted;
    const confirmGifts = () => {
      const drinkMap = {};
      Object.entries(gifts).forEach(([pid,n]) => { if(n>0) drinkMap[pid]=n; });
      if (onAdvance) onAdvance(drinkMap);
      setPhase('done');
    };
    // auto-confirm when all drinks distributed
    React.useEffect(() => {
      if (phase !== 'distribute') return;
      if (remaining !== 0) return;
      const t = setTimeout(confirmGifts, 800);
      return () => clearTimeout(t);
    }, [remaining, phase]);
    return (
      <div style={{display:'flex',flexDirection:'column',gap:8,overflowY:'auto'}}>
        {/* Fejléc */}
        <div style={{background:T.surface,borderRadius:16,padding:'12px 16px',boxShadow:T.shadow,textAlign:'center'}}>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:pColor,lineHeight:1}}>🍺 {kortyok} korty</div>
          <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:3}}>{pName} kiosztja — kire?</div>
          {remaining > 0 && (
            <div style={{fontFamily:T.font,fontSize:12,fontWeight:700,color:T.inkSoft,marginTop:4}}>Még {remaining} korty kiosztható</div>
          )}
          {remaining === 0 && (
            <div style={{fontFamily:T.font,fontSize:12,fontWeight:700,color:T.mint,marginTop:4}}>✓ Minden kiosztva!</div>
          )}
        </div>
        {/* Játékos sorok +/- gombokkal */}
        <div style={{display:'flex',flexDirection:'column',gap:7}}>
          {others.map(p => {
            const given = gifts[p.id] || 0;
            return (
              <div key={p.id} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 12px',background:T.surface,borderRadius:14,boxShadow:T.shadow}}>
                <div style={{width:36,height:36,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>
                  {(p.name||'?').charAt(0).toUpperCase()}
                </div>
                <div style={{flex:1,minWidth:0}}>
                  <div style={{fontFamily:T.font,fontWeight:700,fontSize:14,color:T.ink,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{p.name}</div>
                  {given > 0 && <div style={{fontFamily:T.font,fontSize:12,color:T.coral,fontWeight:700,marginTop:1}}>+{given} 🍺 kap</div>}
                </div>
                <div style={{display:'flex',alignItems:'center',gap:6,flexShrink:0}}>
                  <button onClick={()=>setGifts(g=>({...g,[p.id]:Math.max(0,(g[p.id]||0)-1)}))} disabled={given<=0}
                    style={{width:32,height:32,borderRadius:9,border:'none',background:given>0?T.coral+'22':T.bgSoft,color:given>0?T.coral:T.inkMute,fontFamily:T.font,fontSize:20,cursor:given>0?'pointer':'default',fontWeight:700,lineHeight:1}}>−</button>
                  <div style={{fontFamily:T.font,fontWeight:800,fontSize:16,color:given>0?T.coral:T.inkMute,minWidth:20,textAlign:'center'}}>{given}</div>
                  <button onClick={()=>{if(remaining>0)setGifts(g=>({...g,[p.id]:(g[p.id]||0)+1}));}} disabled={remaining<=0}
                    style={{width:32,height:32,borderRadius:9,border:'none',background:remaining>0?T.mint+'22':T.bgSoft,color:remaining>0?T.mint:T.inkMute,fontFamily:T.font,fontSize:20,cursor:remaining>0?'pointer':'default',fontWeight:700,lineHeight:1}}>+</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }"""
assert OLD4 in src, '4 not found'
src = src.replace(OLD4, NEW4, 1)

# 5. Make question/bank/result phase scrollable too
OLD5 = "  if (phase === 'question' || phase === 'result' || phase === 'bank') {\n    const isResultOrBank = phase === 'result' || phase === 'bank';\n    const subtitleText = phase === 'bank' ? 'Helyes! · a tét nő'\n      : phase === 'result' && !correct ? 'Rossz válasz...'\n      : streak > 0 ? `${pName} sorozata: ${streak} helyes` : `${pName} köre`;\n    return (\n      <div style={{display:'flex',flexDirection:'column',gap:10}}>"
NEW5 = "  if (phase === 'question' || phase === 'result' || phase === 'bank') {\n    const isResultOrBank = phase === 'result' || phase === 'bank';\n    const subtitleText = phase === 'bank' ? 'Helyes! · a tét nő'\n      : phase === 'result' && !correct ? 'Rossz válasz...'\n      : streak > 0 ? `${pName} sorozata: ${streak} helyes` : `${pName} köre`;\n    return (\n      <div style={{display:'flex',flexDirection:'column',gap:10,overflowY:'auto'}}>"
assert OLD5 in src, '5 not found'
src = src.replace(OLD5, NEW5, 1)

# 6. version bump
assert 'v9.442' in src, 'version not found'
src = src.replace('v9.442', 'v9.443', 1)

with open('index.html','w',encoding='utf-8') as f: f.write(src)
print('OK')
