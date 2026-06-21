# -*- coding: utf-8 -*-
with open('index.html','r', encoding='utf-8') as f: src=f.read()

# 1. Replace answerQ function
OLD_ANS = """  const answerQ = (opt) => {
    if (phase !== 'question') return;
    const isCorrect = opt === currentQ.a[0];
    setChosen(opt); setCorrect(isCorrect);
    setPhase('result');
    setTimeout(() => {
      if (isCorrect) {
        setStreak(s => s + 1);
        setPhase('bank');
      } else {
        setPhase('done');
        const drinks = streak + 1;
        if (onAdvance) onAdvance({[challenger?.id]: drinks});
        if (onResult) onResult({ correct: false, playerName: challenger?.name, drinks, subtitle: (challenger?.name||'Játékos') + ` iszik ${drinks} kortyt` });
      }
    }, 1000);
  };"""

NEW_ANS = """  const answerQ = (opt) => {
    if (phase !== 'question') return;
    const isCorrect = opt === currentQ.a[0];
    setChosen(opt); setCorrect(isCorrect);
    if (isCorrect) {
      setStreak(s => s + 1);
      setPhase('bank');
    } else {
      setPhase('result');
      setTimeout(() => {
        setPhase('done');
        const drinks = streak + 1;
        if (onAdvance) onAdvance({[challenger?.id]: drinks});
        if (onResult) onResult({ correct: false, playerName: challenger?.name, drinks, subtitle: (challenger?.name||'Játékos') + ` iszik ${drinks} kortyt` });
      }, 1500);
    }
  };"""

assert OLD_ANS in src, 'answerQ not found'
src = src.replace(OLD_ANS, NEW_ANS, 1)

# 2. Replace all render sections
OLD_RENDER = """  // ── Kérdés UI ──
  if (phase === 'question' || phase === 'result') {
    return (
      <div style={{display:'flex',flexDirection:'column',gap:14}}>
        {/* Fejléc */}
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'5px 14px',background:pColor+'22',borderRadius:999}}>
            <div style={{width:8,height:8,borderRadius:'50%',background:pColor}} />
            <span style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink}}>{pName}</span>
          </div>
          <div style={{display:'flex',gap:6,alignItems:'center'}}>
            {streak > 0 && <div style={{padding:'4px 10px',background:T.mint+'22',borderRadius:999,fontFamily:T.font,fontWeight:700,fontSize:12,color:T.mint}}>🔥 {streak} helyes</div>}
            <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft}}>{currentQ?.cat}</div>
          </div>
        </div>

        {/* Kérdés kártya */}
        <div style={{background:T.surface,borderRadius:20,padding:'20px 18px',boxShadow:T.shadow}}>
          <div style={{fontFamily:T.font,fontWeight:800,fontSize:17,color:T.ink,lineHeight:1.4,textAlign:'center'}}>
            {currentQ?.q}
          </div>
        </div>

        {/* Tét mutató */}
        {streak > 0 && (
          <div style={{display:'flex',gap:8}}>
            <div style={{flex:1,padding:'8px 12px',background:T.mint+'15',borderRadius:12,textAlign:'center',fontFamily:T.font,fontSize:12,color:T.mint,fontWeight:700}}>
              ✓ Bankol: +1 pont, {streak} korty osztani
            </div>
            <div style={{flex:1,padding:'8px 12px',background:T.coral+'15',borderRadius:12,textAlign:'center',fontFamily:T.font,fontSize:12,color:T.coral,fontWeight:700}}>
              ✗ Hibázik: {streak+1} korty iszik
            </div>
          </div>
        )}

        {/* Válaszok */}
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
          {shuffled.map((opt,i) => {
            const isChosen = chosen === opt;
            const isCorrectOpt = opt === currentQ?.a[0];
            let bg = T.surface, border = T.inkMute+'28', color = T.ink;
            if (phase === 'result' && isChosen && correct) { bg=T.mint+'22'; border=T.mint; color=T.mint; }
            if (phase === 'result' && isChosen && !correct) { bg=T.coral+'22'; border=T.coral; color=T.coral; }
            if (phase === 'result' && !isChosen && isCorrectOpt) { bg=T.mint+'15'; border=T.mint+'88'; color=T.mint; }
            return (
              <button key={i} onClick={()=>answerQ(opt)} disabled={phase==='result'} style={{
                padding:'14px 10px', borderRadius:14, border:'2px solid '+border,
                background:bg, color:color, fontFamily:T.font, fontWeight:700, fontSize:14,
                cursor: phase==='result'?'default':'pointer', transition:'all .15s', textAlign:'center',
                boxShadow: phase==='question' ? T.shadow : 'none',
              }}>{opt}</button>
            );
          })}
        </div>
      </div>
    );
  }

  // ── Bank / Push luck döntés ──
  if (phase === 'bank') {
    const nextDrinks = streak + 1;
    return (
      <div style={{display:'flex',flexDirection:'column',gap:14,alignItems:'center',textAlign:'center'}}>
        <div style={{fontSize:40,animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)'}}>✅</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:T.mint}}>Helyes!</div>
        <div style={{fontFamily:T.font,fontSize:14,color:T.inkSoft}}>Kategória: {currentQ?.cat}</div>

        {/* Döntés */}
        <div style={{width:'100%',display:'flex',flexDirection:'column',gap:10,marginTop:8}}>
          <button onClick={bankIt} style={{
            padding:'18px', borderRadius:16, border:'none', background:T.mint, color:'#fff',
            fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer',
            boxShadow:'0 5px 16px -5px '+T.mint+'88',
          }}>
            🏦 Pontot kérek{streak>1?' + '+kortyok+' kortyot osztok':''}
          </button>
          <button onClick={pushLuck} style={{
            padding:'16px', borderRadius:16, border:'2px solid '+T.coral+'44',
            background:T.coral+'12', color:T.coral,
            fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer',
          }}>
            🎲 Tovább megyek — {streak+1} kortyt oszthat vs. {nextDrinks} kortyt iszik
          </button>
        </div>

        <div style={{fontFamily:T.font,fontSize:12,color:T.inkMute,marginTop:4}}>
          Jelenlegi sorozat: {streak} helyes kérdés
        </div>
      </div>
    );
  }

  // ── Korty szétosztás ──
  if (phase === 'distribute') {
    const others = players.filter(p => p.id !== challenger?.id);
    const gp = giftPool || { pool: kortyok, assigned: {} };
    const remaining = gp.pool;
    return (
      <div style={{display:'flex',flexDirection:'column',gap:12}}>
        {/* Fejléc */}
        <div style={{background:`linear-gradient(135deg,${pColor}22,${pColor}08)`,borderRadius:16,padding:'14px 16px',display:'flex',alignItems:'center',justifyContent:'space-between',border:`1px solid ${pColor}25`}}>
          <div>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:28,color:pColor,lineHeight:1}}>
              {remaining > 0 ? `${remaining} korty` : '✓ Kész!'}
            </div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:4}}>
              {remaining > 0 ? `${challenger?.name} kiosztja — koppints a névre (+1)` : 'Minden korty ki van osztva'}
            </div>
          </div>
          <div style={{fontSize:32}}>🍺</div>
        </div>

        {/* Játékos lista */}
        <div style={{display:'flex',flexDirection:'column',gap:8}}>
          {others.map(p => {
            const assigned = (giftPool?.assigned[p.id]||0);
            const hasAny = assigned > 0;
            return (
              <div key={p.id} style={{
                display:'flex',alignItems:'center',gap:10,padding:'12px 14px',
                background: hasAny ? p.color+'15' : T.surface,
                border:`1.5px solid ${hasAny ? p.color+'60' : 'transparent'}`,
                borderRadius:14,transition:'all .15s',
              }}>
                {/* Avatar + név — koppintásra +1 */}
                <div onClick={()=>{ if(!giftPool) openGiftPool(); giveOneDrink(p.id); }}
                  style={{display:'flex',alignItems:'center',gap:10,flex:1,cursor:remaining>0||!giftPool?'pointer':'default',minWidth:0}}>
                  <div style={{width:36,height:36,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>
                    {(p.name||'?').charAt(0).toUpperCase()}
                  </div>
                  <span style={{fontFamily:T.font,fontWeight:700,fontSize:15,color:T.ink,flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{p.name}</span>
                  {(remaining>0||(giftPool&&remaining>0)) && <span style={{fontFamily:T.font,fontSize:13,fontWeight:700,color:pColor,flexShrink:0}}>+1</span>}
                </div>
                {/* Assigned counter */}
                {hasAny && (
                  <div style={{display:'flex',alignItems:'center',gap:6,flexShrink:0}}>
                    <button onClick={()=>takeOneDrink(p.id)} style={{
                      width:28,height:28,borderRadius:'50%',background:T.coralSoft||T.coral+'22',
                      border:`1.5px solid ${T.coral}44`,color:T.coral,
                      fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer',lineHeight:1,
                    }}>−</button>
                    <span style={{fontFamily:T.font,fontWeight:900,fontSize:16,color:p.color,minWidth:20,textAlign:'center'}}>{assigned}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Megerősítés gomb */}
        {giftPool && (
          <button onClick={confirmGift} style={{
            padding:'15px',borderRadius:14,border:'none',
            background: giftPool.pool===0 ? pColor : T.surface,
            color: giftPool.pool===0 ? '#fff' : T.inkSoft,
            fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer',
            boxShadow: giftPool.pool===0 ? `0 5px 16px -5px ${pColor}88` : T.shadow,
            transition:'all .2s',
          }}>
            {giftPool.pool===0 ? '✓ Kiosztás megerősítése' : `Még ${giftPool.pool} korty marad`}
          </button>
        )}
        {!giftPool && (
          <button onClick={openGiftPool} style={{
            padding:'15px',borderRadius:14,border:'none',
            background:pColor,color:'#fff',
            fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer',
            boxShadow:`0 5px 16px -5px ${pColor}88`,
          }}>Kiosztás indítása →</button>
        )}
      </div>
    );
  }

  // ── Done ──
  if (phase === 'done') {
    const failed = !correct && chosen !== null;
    const drinkCount = streak + 1;
    return (
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:16,padding:'20px 0',textAlign:'center',animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)'}}>
        <div style={{fontSize:48}}>{failed ? '😵' : '🏆'}</div>
        {failed ? (
          <>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:T.coral}}>Hibás válasz!</div>
            <div style={{padding:'12px 20px',background:T.coral+'18',borderRadius:14,border:'1.5px solid '+T.coral+'44',fontFamily:T.font,fontWeight:700,fontSize:16,color:T.coral}}>
              {pName} iszik {drinkCount} kortyot 🍺
            </div>
            <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft}}>
              Helyes válasz: <strong>{currentQ?.a[0]}</strong>
            </div>
          </>
        ) : (
          <>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:T.mint}}>{pName} bankolt!</div>
            <div style={{padding:'12px 20px',background:T.mint+'18',borderRadius:14,border:'1.5px solid '+T.mint+'44',fontFamily:T.font,fontWeight:700,fontSize:16,color:T.mint}}>
              +1 pont{distributeTarget ? ` · ${kortyok} korty → ${players.find(p=>p.id===distributeTarget)?.name}` : ''}
            </div>
          </>
        )}
        <div style={{fontFamily:T.font,fontSize:12,color:T.inkMute,marginTop:4}}>
          Sorozat: {streak} helyes kérdés
        </div>
      </div>
    );
  }

  return null;
}"""

NEW_RENDER = """  // ── Quiz redesign ──
  const QPURPLE = '#251650';
  const QYELLOW = '#F5C518';
  const QBLUE = '#0ea5e9';

  const tetMax = Math.max(streak + 1, 5);
  const tetLadder = [];
  for (let _v = tetMax; _v >= 1; _v--) tetLadder.push(_v);

  if (phase === 'question' || phase === 'result' || phase === 'bank') {
    const isResultOrBank = phase === 'result' || phase === 'bank';
    const bannerText = streak > 0 ? `KOCKÁN 🍺 ${streak} KORTY` : 'KVÍZ';
    const subtitleText = phase === 'bank' ? 'Helyes! · a tét nő'
      : phase === 'result' && !correct ? 'Rossz válasz...'
      : streak > 0 ? `${pName} sorozata: ${streak} helyes` : `${pName} köre`;
    return (
      <div style={{margin:'-16px',background:QPURPLE,minHeight:'100%',display:'flex',flexDirection:'column',padding:'12px 12px 14px',boxSizing:'border-box'}}>
        <div style={{background:QYELLOW,borderRadius:12,padding:'9px 16px',textAlign:'center',marginBottom:6,flexShrink:0}}>
          <span style={{fontFamily:T.font,fontWeight:900,fontSize:15,color:'#1a0a3e'}}>{bannerText}</span>
        </div>
        <div style={{textAlign:'center',fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.65)',marginBottom:8,minHeight:16,flexShrink:0}}>
          {subtitleText}
        </div>
        <div style={{background:'rgba(255,255,255,0.1)',borderRadius:16,padding:'12px 14px',marginBottom:10,flexShrink:0}}>
          <div style={{fontFamily:T.font,fontSize:10,fontWeight:900,color:'rgba(255,255,255,0.4)',letterSpacing:1.5,marginBottom:5,textAlign:'center'}}>KÉRDÉS</div>
          <div style={{fontFamily:T.font,fontWeight:800,fontSize:15,color:'#fff',lineHeight:1.4,textAlign:'center'}}>{currentQ?.q}</div>
        </div>
        <div style={{display:'flex',gap:8,flex:1,marginBottom:10,minHeight:0}}>
          <div style={{flex:1,display:'grid',gridTemplateColumns:'1fr 1fr',gridTemplateRows:'1fr 1fr',gap:8}}>
            {['A','B','C','D'].map((letter,i) => {
              const opt = shuffled[i];
              if (!opt) return <div key={i}/>;
              const isChosen = chosen === opt;
              const isCorrectOpt = opt === currentQ?.a[0];
              let bg='rgba(255,255,255,0.08)', border='rgba(255,255,255,0.12)', color='rgba(255,255,255,0.9)';
              if (isResultOrBank) {
                if (isChosen && correct) { bg='#22c55e22'; border='#22c55e'; color='#22c55e'; }
                else if (isChosen && !correct) { bg='#ef444422'; border='#ef4444'; color='#ef4444'; }
                else if (isCorrectOpt) { bg='#22c55e15'; border='#22c55e66'; color='#22c55e'; }
              }
              return (
                <button key={i} onClick={()=>answerQ(opt)} disabled={isResultOrBank} style={{
                  padding:'10px 8px',borderRadius:12,border:'2px solid '+border,
                  background:bg,color:color,fontFamily:T.font,fontWeight:700,fontSize:13,
                  cursor:isResultOrBank?'default':'pointer',transition:'all .15s',
                  display:'flex',flexDirection:'column',alignItems:'flex-start',gap:2,minHeight:0,
                }}>
                  <span style={{fontSize:10,opacity:0.55,fontWeight:900,lineHeight:1}}>{letter}</span>
                  <span style={{lineHeight:1.3,textAlign:'left'}}>{opt}</span>
                </button>
              );
            })}
          </div>
          {streak > 0 && (
            <div style={{width:50,display:'flex',flexDirection:'column',gap:3}}>
              <div style={{fontFamily:T.font,fontSize:8,fontWeight:900,color:'rgba(255,255,255,0.4)',letterSpacing:1.5,textAlign:'center',marginBottom:2}}>TÉT</div>
              {tetLadder.slice(0,6).map(val => {
                const isCurrent = val === streak;
                return (
                  <div key={val} style={{
                    flex:1,borderRadius:8,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',
                    background: isCurrent ? QBLUE : 'rgba(255,255,255,0.07)',
                    border: '2px solid '+(isCurrent ? QBLUE : 'transparent'),minHeight:0,
                  }}>
                    <div style={{fontFamily:T.font,fontWeight:900,fontSize:12,color:isCurrent?'#fff':'rgba(255,255,255,0.32)',lineHeight:1}}>{val}</div>
                    <div style={{fontFamily:T.font,fontSize:6,color:isCurrent?'rgba(255,255,255,0.85)':'rgba(255,255,255,0.2)',fontWeight:700,letterSpacing:0.5}}>
                      {isCurrent ? 'MOST' : 'KORTY'}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
        {phase === 'bank' && (
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,flexShrink:0}}>
            <button onClick={bankIt} style={{
              padding:'13px 8px',borderRadius:14,border:'none',background:QYELLOW,color:'#1a0a3e',
              fontFamily:T.font,fontWeight:900,fontSize:13,cursor:'pointer',lineHeight:1.35,
            }}>{'Bankolom\\n'+streak+' korty félre'}</button>
            <button onClick={pushLuck} style={{
              padding:'13px 8px',borderRadius:14,border:'none',background:QBLUE,color:'#fff',
              fontFamily:T.font,fontWeight:900,fontSize:13,cursor:'pointer',lineHeight:1.35,
            }}>{'Tovább\\ntét → '+(streak+1)+' korty'}</button>
          </div>
        )}
      </div>
    );
  }

  if (phase === 'distribute') {
    const others = players.filter(p => p.id !== challenger?.id);
    return (
      <div style={{margin:'-16px',background:QPURPLE,minHeight:'100%',display:'flex',flexDirection:'column',padding:'12px 12px 14px',boxSizing:'border-box'}}>
        <div style={{background:QYELLOW,borderRadius:12,padding:'9px 16px',textAlign:'center',marginBottom:6,flexShrink:0}}>
          <span style={{fontFamily:T.font,fontWeight:900,fontSize:15,color:'#1a0a3e'}}>BANKBAN 🍺 {kortyok} KORTY</span>
        </div>
        <div style={{textAlign:'center',fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.65)',marginBottom:14,flexShrink:0}}>
          {pName} kiosztja a {kortyok} kortyot — kire?
        </div>
        <div style={{display:'flex',flexDirection:'column',gap:8,flex:1}}>
          {others.map(p => {
            const isSel = distributeTarget === p.id;
            return (
              <div key={p.id} onClick={()=>setDistributeTarget(isSel ? null : p.id)} style={{
                display:'flex',alignItems:'center',gap:12,padding:'12px 16px',
                background: isSel ? 'rgba(14,165,233,0.18)' : 'rgba(255,255,255,0.07)',
                border:'2px solid '+(isSel ? QBLUE : 'transparent'),
                borderRadius:14,cursor:'pointer',transition:'all .15s',
              }}>
                <div style={{width:40,height:40,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:16,color:'#fff',flexShrink:0}}>
                  {(p.name||'?').charAt(0).toUpperCase()}
                </div>
                <span style={{fontFamily:T.font,fontWeight:700,fontSize:15,color:'#fff',flex:1}}>{p.name}</span>
                <span style={{fontFamily:T.font,fontSize:11,fontWeight:900,color:isSel?QBLUE:'rgba(255,255,255,0.3)',letterSpacing:0.5}}>
                  {isSel ? '✓ KIVÁLASZTVA' : 'KIVÁLASZT'}
                </span>
              </div>
            );
          })}
        </div>
        {distributeTarget && (
          <div style={{marginTop:12,flexShrink:0}}>
            <div style={{background:'rgba(255,255,255,0.1)',borderRadius:16,padding:'14px 16px',marginBottom:10,textAlign:'center'}}>
              <div style={{fontSize:22,marginBottom:4}}>🍺🍺</div>
              <div style={{fontFamily:T.font,fontWeight:900,fontSize:16,color:'#fff',marginBottom:4}}>
                {players.find(p=>p.id===distributeTarget)?.name} iszik {kortyok} kortyot
              </div>
              <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.55)'}}>{pName} bezsebelte a kört</div>
            </div>
            <button onClick={()=>distribute(distributeTarget)} style={{
              width:'100%',padding:'15px',borderRadius:14,border:'none',
              background:QYELLOW,color:'#1a0a3e',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer',
            }}>Megerősítés ✓</button>
          </div>
        )}
      </div>
    );
  }

  if (phase === 'done') {
    const failed = !correct && chosen !== null;
    const drinkCount = streak + 1;
    return (
      <div style={{margin:'-16px',background:QPURPLE,minHeight:'100%',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',padding:'20px 16px',boxSizing:'border-box',textAlign:'center',animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)'}}>
        <div style={{fontSize:52,marginBottom:16}}>{failed ? '😵' : '🏆'}</div>
        {failed ? (
          <>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:'#ef4444',marginBottom:12}}>Rossz válasz!</div>
            <div style={{padding:'14px 24px',background:'rgba(239,68,68,0.15)',borderRadius:16,border:'1.5px solid rgba(239,68,68,0.4)',fontFamily:T.font,fontWeight:700,fontSize:16,color:'#ef4444',marginBottom:10}}>
              {pName} iszik {drinkCount} kortyot 🍺
            </div>
            <div style={{fontFamily:T.font,fontSize:13,color:'rgba(255,255,255,0.5)'}}>
              Helyes válasz: <strong style={{color:'#22c55e'}}>{currentQ?.a[0]}</strong>
            </div>
          </>
        ) : (
          <>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:'#22c55e',marginBottom:12}}>{pName} bankolt!</div>
            <div style={{padding:'14px 24px',background:'rgba(34,197,94,0.15)',borderRadius:16,border:'1.5px solid rgba(34,197,94,0.4)',fontFamily:T.font,fontWeight:700,fontSize:16,color:'#22c55e'}}>
              +1 pont{distributeTarget ? ` · ${kortyok} korty → ${players.find(p=>p.id===distributeTarget)?.name}` : ''}
            </div>
          </>
        )}
        <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.35)',marginTop:12}}>
          Sorozat: {streak} helyes kérdés
        </div>
      </div>
    );
  }

  return null;
}"""

assert OLD_RENDER in src, 'render section not found'
src = src.replace(OLD_RENDER, NEW_RENDER, 1)

# 3. Version bump
assert 'v9.431' in src, 'version not found'
src = src.replace('v9.431', 'v9.432', 1)

with open('index.html','w', encoding='utf-8') as f: f.write(src)
print('OK')
