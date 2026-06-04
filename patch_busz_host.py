with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

old = """        {!guessResult && isOnline && (
          <div style={{textAlign:'center',padding:'14px',borderRadius:14,background:T.surfaceMuted,fontFamily:T.font,fontSize:14,color:T.inkSoft}}>
            ⏳ Várjuk {currentRider?.name || '?'} tippjét a saját telefonján…
          </div>
        )}"""

new = """        {!guessResult && isOnline && (
          <div style={{borderRadius:14,background:T.surfaceMuted,overflow:'hidden'}}>
            <div style={{padding:'12px 14px',fontFamily:T.font,fontSize:13,color:T.inkSoft,textAlign:'center'}}>
              ⏳ Várjuk <b style={{color:T.ink}}>{currentRider?.name || '?'}</b> tippjét a saját telefonján…
            </div>
            <div style={{borderTop:`1px solid ${T.surface}`,padding:'10px 12px'}}>
              <div style={{fontFamily:T.font,fontSize:10,fontWeight:700,color:T.inkMute,textTransform:'uppercase',letterSpacing:'0.08em',textAlign:'center',marginBottom:8}}>Host beavatkozás — tippelj helyette</div>
              <div style={{display:'flex',gap:8}}>
                <button onClick={()=>makeGuess('K')} style={{flex:1,minHeight:44,border:`2px solid ${T.coral}`,background:'transparent',color:T.coral,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,borderRadius:12,cursor:'pointer'}}>▼ Kisebb</button>
                <button onClick={()=>makeGuess('N')} style={{flex:1,minHeight:44,border:`2px solid ${T.mint}`,background:'transparent',color:T.mint,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,borderRadius:12,cursor:'pointer'}}>▲ Nagyobb</button>
              </div>
            </div>
          </div>
        )}"""

assert old in html, "waiting block not found"
html = html.replace(old, new, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
