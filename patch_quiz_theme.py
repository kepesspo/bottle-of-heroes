# -*- coding: utf-8 -*-
with open('index.html','r',encoding='utf-8') as f: src=f.read()

OLD = """  // ── Quiz redesign ──
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
  }"""

NEW = """  // ── Quiz UI (app téma) ──
  const tetMax = Math.max(streak + 1, 5);
  const tetLadder = [];
  for (let _v = tetMax; _v >= 1; _v--) tetLadder.push(_v);

  if (phase === 'question' || phase === 'result' || phase === 'bank') {
    const isResultOrBank = phase === 'result' || phase === 'bank';
    const subtitleText = phase === 'bank' ? 'Helyes! · a tét nő'
      : phase === 'result' && !correct ? 'Rossz válasz...'
      : streak > 0 ? `${pName} sorozata: ${streak} helyes` : `${pName} köre`;
    return (
      <div style={{display:'flex',flexDirection:'column',gap:10}}>
        {/* Fejléc sor: játékos + tét info */}
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'5px 12px',background:pColor+'22',borderRadius:999}}>
            <div style={{width:8,height:8,borderRadius:'50%',background:pColor}}/>
            <span style={{fontFamily:T.font,fontWeight:800,fontSize:13,color:T.ink}}>{pName}</span>
          </div>
          {streak > 0 && (
            <div style={{display:'flex',alignItems:'center',gap:6}}>
              <div style={{padding:'4px 10px',background:T.mint+'22',borderRadius:999,fontFamily:T.font,fontWeight:700,fontSize:12,color:T.mint}}>🔥 {streak} helyes</div>
              <div style={{padding:'4px 10px',background:T.coral+'18',borderRadius:999,fontFamily:T.font,fontWeight:700,fontSize:12,color:T.coral}}>{streak+1} ✗</div>
            </div>
          )}
        </div>

        {/* Kérdés kártya */}
        <div style={{background:T.surface,borderRadius:18,padding:'16px',boxShadow:T.shadow}}>
          <div style={{fontFamily:T.font,fontSize:10,fontWeight:900,color:T.inkSoft,letterSpacing:1.5,marginBottom:6,textAlign:'center'}}>KÉRDÉS</div>
          <div style={{fontFamily:T.font,fontWeight:800,fontSize:16,color:T.ink,lineHeight:1.4,textAlign:'center'}}>{currentQ?.q}</div>
          {streak > 0 && (
            <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft,textAlign:'center',marginTop:6}}>{subtitleText}</div>
          )}
        </div>

        {/* Válaszok + TÉT létra */}
        <div style={{display:'flex',gap:8}}>
          <div style={{flex:1,display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
            {['A','B','C','D'].map((letter,i) => {
              const opt = shuffled[i];
              if (!opt) return <div key={i}/>;
              const isChosen = chosen === opt;
              const isCorrectOpt = opt === currentQ?.a[0];
              let bg=T.surface, border=T.inkMute+'30', color=T.ink;
              if (isResultOrBank) {
                if (isChosen && correct) { bg=T.mint+'20'; border=T.mint; color=T.mint; }
                else if (isChosen && !correct) { bg=T.coral+'20'; border=T.coral; color=T.coral; }
                else if (isCorrectOpt) { bg=T.mint+'10'; border=T.mint+'88'; color=T.mint; }
              }
              return (
                <button key={i} onClick={()=>answerQ(opt)} disabled={isResultOrBank} style={{
                  padding:'12px 10px',borderRadius:14,border:'2px solid '+border,
                  background:bg,color:color,fontFamily:T.font,fontWeight:700,fontSize:14,
                  cursor:isResultOrBank?'default':'pointer',transition:'all .15s',
                  display:'flex',flexDirection:'column',alignItems:'flex-start',gap:3,
                  boxShadow:isResultOrBank?'none':T.shadow,
                }}>
                  <span style={{fontSize:10,opacity:0.5,fontWeight:900,lineHeight:1}}>{letter}</span>
                  <span style={{lineHeight:1.3,textAlign:'left'}}>{opt}</span>
                </button>
              );
            })}
          </div>
          {/* TÉT létra */}
          {streak > 0 && (
            <div style={{width:46,display:'flex',flexDirection:'column',gap:3}}>
              <div style={{fontFamily:T.font,fontSize:8,fontWeight:900,color:T.inkSoft,letterSpacing:1.5,textAlign:'center',marginBottom:2}}>TÉT</div>
              {tetLadder.slice(0,6).map(val => {
                const isCurrent = val === streak;
                return (
                  <div key={val} style={{
                    flex:1,borderRadius:8,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',
                    background: isCurrent ? T.mint : T.surface,
                    border: '2px solid '+(isCurrent ? T.mint : T.inkMute+'20'),
                    boxShadow: isCurrent ? '0 2px 8px -2px '+T.mint+'66' : 'none',
                    minHeight:28,
                  }}>
                    <div style={{fontFamily:T.font,fontWeight:900,fontSize:12,color:isCurrent?'#fff':T.inkSoft,lineHeight:1}}>{val}</div>
                    <div style={{fontFamily:T.font,fontSize:6,color:isCurrent?'rgba(255,255,255,0.8)':T.inkMute,fontWeight:700,letterSpacing:0.5}}>
                      {isCurrent ? 'MOST' : 'KORTY'}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Bank / Tovább gombok */}
        {phase === 'bank' && (
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
            <button onClick={bankIt} style={{
              padding:'14px 8px',borderRadius:14,border:'none',
              background:T.mint,color:'#fff',
              fontFamily:T.font,fontWeight:900,fontSize:13,cursor:'pointer',lineHeight:1.35,
              boxShadow:'0 4px 14px -4px '+T.mint+'88',
            }}>{'Bankolom\\n'+streak+' korty félre'}</button>
            <button onClick={pushLuck} style={{
              padding:'14px 8px',borderRadius:14,
              border:'2px solid '+T.coral+'44',background:T.coral+'12',color:T.coral,
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
  }

  if (phase === 'done') {
    const failed = !correct && chosen !== null;
    const drinkCount = streak + 1;
    return (
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:14,padding:'20px 0',textAlign:'center',animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)'}}>
        <div style={{fontSize:48}}>{failed ? '😵' : '🏆'}</div>
        {failed ? (
          <>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:T.coral}}>Rossz válasz!</div>
            <div style={{padding:'12px 20px',background:T.coral+'18',borderRadius:14,border:'1.5px solid '+T.coral+'44',fontFamily:T.font,fontWeight:700,fontSize:16,color:T.coral}}>
              {pName} iszik {drinkCount} kortyot 🍺
            </div>
            <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft}}>
              Helyes válasz: <strong style={{color:T.mint}}>{currentQ?.a[0]}</strong>
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
  }"""

assert OLD in src, 'quiz render section not found'
src = src.replace(OLD, NEW, 1)
assert 'v9.439' in src
src = src.replace('v9.439', 'v9.440', 1)
with open('index.html','w',encoding='utf-8') as f: f.write(src)
print('OK')
