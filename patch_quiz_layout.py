# -*- coding: utf-8 -*-
with open('index.html','r',encoding='utf-8') as f: src=f.read()

# Replace the entire question/result/bank phase UI
OLD = """  if (phase === 'question' || phase === 'result' || phase === 'bank') {
    const isResultOrBank = phase === 'result' || phase === 'bank';
    const subtitleText = phase === 'bank' ? 'Helyes! · a tét nő'
      : phase === 'result' && !correct ? 'Rossz válasz...'
      : streak > 0 ? `${pName} sorozata: ${streak} helyes` : `${pName} köre`;
    return (
      <div style={{display:'flex',flexDirection:'column',gap:10,overflowY:'auto'}}>
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
  }"""

NEW = """  if (phase === 'question' || phase === 'result' || phase === 'bank') {
    const isResultOrBank = phase === 'result' || phase === 'bank';
    // Horizontal TÉT strip: show 1..5, always visible from first question
    const tetShow = Math.max(5, streak + 2);
    const tetValues = Array.from({length:tetShow}, (_,i)=>i+1);
    return (
      <div style={{display:'flex',flexDirection:'column',gap:10,overflowY:'auto'}}>
        {/* Fejléc sor: játékos + streak chips */}
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
        </div>

        {/* Vízszintes TÉT sáv — mindig látható */}
        <div style={{background:T.surface,borderRadius:14,padding:'10px 12px',boxShadow:T.shadow}}>
          <div style={{fontFamily:T.font,fontSize:9,fontWeight:900,color:T.inkSoft,letterSpacing:1.5,marginBottom:6}}>TÉT — KORTY</div>
          <div style={{display:'flex',gap:5,alignItems:'stretch'}}>
            {tetValues.map(val => {
              const isCurrent = val === streak && streak > 0;
              const isNext = val === streak + 1;
              let bg = T.bgSoft;
              let border = 'transparent';
              let textColor = T.inkMute;
              let label = '';
              if (isCurrent) { bg = T.mint; border = T.mint; textColor = '#fff'; label = 'BANK'; }
              else if (isNext && !isResultOrBank) { bg = T.coral+'18'; border = T.coral+'55'; textColor = T.coral; label = 'KÖV'; }
              return (
                <div key={val} style={{
                  flex:1,borderRadius:8,padding:'6px 2px',
                  background:bg,border:'2px solid '+border,
                  display:'flex',flexDirection:'column',alignItems:'center',gap:2,
                  transition:'all .2s',
                }}>
                  <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:textColor,lineHeight:1}}>{val}</div>
                  {label && <div style={{fontFamily:T.font,fontSize:7,fontWeight:800,color:textColor,opacity:0.8,letterSpacing:0.5}}>{label}</div>}
                </div>
              );
            })}
          </div>
        </div>

        {/* 4 válasz egymás alatt */}
        <div style={{display:'flex',flexDirection:'column',gap:8}}>
          {['A','B','C','D'].map((letter,i) => {
            const opt = shuffled[i];
            if (!opt) return null;
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
                width:'100%',padding:'13px 14px',borderRadius:14,border:'2px solid '+border,
                background:bg,color:color,fontFamily:T.font,fontWeight:700,fontSize:15,
                cursor:isResultOrBank?'default':'pointer',transition:'all .15s',
                display:'flex',alignItems:'center',gap:10,textAlign:'left',
                boxShadow:isResultOrBank?'none':T.shadow,
              }}>
                <span style={{fontSize:11,opacity:0.5,fontWeight:900,minWidth:14}}>{letter}</span>
                <span style={{lineHeight:1.3,flex:1}}>{opt}</span>
              </button>
            );
          })}
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
  }"""

assert OLD in src, 'question phase not found'
src = src.replace(OLD, NEW, 1)

# version bump
assert 'v9.443' in src, 'version not found'
src = src.replace('v9.443', 'v9.444', 1)

with open('index.html','w',encoding='utf-8') as f: f.write(src)
print('OK')
