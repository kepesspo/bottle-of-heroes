with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# Fix 1: Hide K/N buttons on host when online mode (players use their own devices)
old = """        {/* K/N buttons */}
        {!guessResult && (
          <div style={{display:'flex',gap:10}}>
            <button onClick={()=>makeGuess('K')} style={{flex:1,minHeight:52,border:`2px solid ${T.coral}`,background:'transparent',color:T.coral,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:16,borderRadius:14,cursor:'pointer'}}>▼ Kisebb</button>
            <button onClick={()=>makeGuess('N')} style={{flex:1,minHeight:52,border:`2px solid ${T.mint}`,background:'transparent',color:T.mint,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:16,borderRadius:14,cursor:'pointer'}}>▲ Nagyobb</button>
          </div>
        )}
        {/* Pontos tipp — jelez ha valaki él a lehetőséggel */}
        {buszState.busRiderBonusUsed?.[currentTurnRiderId] && (
          <div style={{textAlign:'center',fontFamily:T.font,fontSize:12,color:T.yellow}}>🃏 Big Pick aktiválva</div>
        )}"""

new = """        {/* K/N buttons — only show on host in offline mode; online players use their own device */}
        {!guessResult && !isOnline && (
          <div style={{display:'flex',gap:10}}>
            <button onClick={()=>makeGuess('K')} style={{flex:1,minHeight:52,border:`2px solid ${T.coral}`,background:'transparent',color:T.coral,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:16,borderRadius:14,cursor:'pointer'}}>▼ Kisebb</button>
            <button onClick={()=>makeGuess('N')} style={{flex:1,minHeight:52,border:`2px solid ${T.mint}`,background:'transparent',color:T.mint,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:16,borderRadius:14,cursor:'pointer'}}>▲ Nagyobb</button>
          </div>
        )}
        {!guessResult && isOnline && (
          <div style={{textAlign:'center',padding:'14px',borderRadius:14,background:T.surfaceMuted,fontFamily:T.font,fontSize:14,color:T.inkSoft}}>
            ⏳ Várjuk {currentRider?.name || '?'} tippjét a saját telefonján…
          </div>
        )}"""

assert old in html, "K/N block not found"
html = html.replace(old, new, 1)

# Fix 2: makeGuessPlayer — rotate currentTurnRiderId when not all submitted
old = """        if (!allSubmitted) {
          setBusGuessResult({waiting:true, step:myStep});
          await firebase.firestore().collection('rooms').doc(roomCode).update({buszState:{...st, busRiderPendingGuesses:pending}});
          return;
        }"""

new = """        if (!allSubmitted) {
          setBusGuessResult({waiting:true, step:myStep});
          const nextAtPos = ridersAtPos.find(rid => !pending[rid]);
          await firebase.firestore().collection('rooms').doc(roomCode).update({buszState:{...st, busRiderPendingGuesses:pending, currentTurnRiderId:nextAtPos||st.currentTurnRiderId}});
          return;
        }"""

assert old in html, "makeGuessPlayer waiting block not found"
html = html.replace(old, new, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
