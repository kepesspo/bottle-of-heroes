with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# 1. Add onResult to function signature
old = "function KisebbGame({ gameIdx, players, onAdvance, gameMeta }) {"
new = "function KisebbGame({ gameIdx, players, onAdvance, onResult, gameMeta }) {"
assert old in html, "sig not found"
html = html.replace(old, new, 1)

# 2. After wrong guess, call onResult with the drink info
# In the setTimeout, after building nst when !ok:
old = """      if (same) {
        // Same value: same player stays, pot grows
        const cfg2 = (gameMeta?.kisebbConfig)||{}; const sm = cfg2.stackMode??'plus1';
        nst = { ...nst, pot: sm==='times2' ? (st.pot||1)*2 : (st.pot||1)+1 };
      } else if (!ok) {
        // Wrong: player drinks pot, next player, pot resets
        const newLives = { ...st.playerLives, [pid]:(st.playerLives[pid]||1)-1 };
        const dm = { ...st.drinkMap, [pid]:(st.drinkMap[pid]||0)+(st.pot||1) };
        nst = { ...nst, drinkMap:dm, playerLives:newLives, pot:1,
                turnPos:(st.turnPos+1)%st.activePids.length };
        if ((newLives[pid]||0)<=0) {
          const newActive = st.activePids.filter(p=>p!==pid);
          nst = { ...nst, activePids:newActive, turnPos:st.turnPos%Math.max(newActive.length,1) };
          if (newActive.length<=1) { setGameOver(true); onAdvance&&onAdvance(dm); }
        }
      } else {
        // Correct: next player, pot stays
        nst = { ...nst, turnPos:(st.turnPos+1)%st.activePids.length };
      }"""

new = """      if (same) {
        // Same value: same player stays, pot grows
        const cfg2 = (gameMeta?.kisebbConfig)||{}; const sm = cfg2.stackMode??'plus1';
        nst = { ...nst, pot: sm==='times2' ? (st.pot||1)*2 : (st.pot||1)+1 };
      } else if (!ok) {
        // Wrong: player drinks pot, next player, pot resets
        const newLives = { ...st.playerLives, [pid]:(st.playerLives[pid]||1)-1 };
        const dm = { ...st.drinkMap, [pid]:(st.drinkMap[pid]||0)+(st.pot||1) };
        const loserPlayer = players.find(p=>p.id===pid);
        onResult && onResult({ correct: false, playerName: loserPlayer?.name, drinks: st.pot||1, subtitle: `${loserPlayer?.name||'Játékos'} iszik ${st.pot||1} kortyt` });
        nst = { ...nst, drinkMap:dm, playerLives:newLives, pot:1,
                turnPos:(st.turnPos+1)%st.activePids.length };
        if ((newLives[pid]||0)<=0) {
          const newActive = st.activePids.filter(p=>p!==pid);
          nst = { ...nst, activePids:newActive, turnPos:st.turnPos%Math.max(newActive.length,1) };
          if (newActive.length<=1) { setGameOver(true); onAdvance&&onAdvance(dm); }
        }
      } else {
        // Correct: next player, pot stays
        nst = { ...nst, turnPos:(st.turnPos+1)%st.activePids.length };
      }"""

assert old in html, "timeout block not found"
html = html.replace(old, new, 1)

# 3. Replace custom gameOver screen with standard result screen
old = """  if(gameOver) return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:12 }}>
      <div style={{ fontSize:48 }}>🏆</div>
      <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:T.mint }}>Játék vége!</div>
      <div style={{ display:'flex', flexDirection:'column', gap:6, width:'100%' }}>
        {players.map(p=>{
          const d=drinkMap[p.id]||0, won=activePids.includes(p.id);
          return <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8, padding:'8px 12px', background:won?`${T.mint}18`:T.surfaceMuted, borderRadius:10 }}>
            <div style={{ width:28, height:28, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff' }}>{p.name.charAt(0)}</div>
            <div style={{ flex:1, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink }}>{p.name}</div>
            <div style={{ fontFamily:'monospace', fontWeight:700, fontSize:14, color:won?T.mint:T.coral }}>{won?'🏆 Győztes':`${d} korty`}</div>
          </div>;
        })}
      </div>
    </div>
  );"""

new = """  if(gameOver) return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontSize:48 }}>🏆</div>
      <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:T.mint }}>Játék vége!</div>
      <div style={{ display:'flex', flexDirection:'column', gap:6, width:'100%' }}>
        {players.map(p=>{
          const d=drinkMap[p.id]||0, won=activePids.includes(p.id);
          return (
            <div key={p.id} style={{ borderRadius:14, padding:'10px 14px', display:'flex', alignItems:'center', gap:12, background: won ? `${T.mint}15` : `${T.coral}15`, border:`2px solid ${won ? T.mint : T.coral}` }}>
              <div style={{ width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>
              <div style={{ flex:1 }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color: won ? T.mint : T.coral }}>{won ? '🏆 Győztes!' : 'Inni kell!'}</div>
                {d > 0 && <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:1 }}>{p.name} — {d} korty összesen</div>}
              </div>
              {d > 0 && <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.coral }}>{d}🍺</div>}
            </div>
          );
        })}
      </div>
    </div>
  );"""

assert old in html, "gameOver screen not found"
html = html.replace(old, new, 1)

# 4. Fix PlayScreen render to pass onResult
old = "  if (gameId === 'kisebb') return <KisebbGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} gameMeta={gameMeta} />;"
new = "  if (gameId === 'kisebb') return <KisebbGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />;"
assert old in html, "PlayScreen kisebb line not found"
html = html.replace(old, new, 1)

assert html != orig, "no changes made"
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
