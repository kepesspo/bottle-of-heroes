import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

NEW_KISEBB = r"""function KisebbGame({ gameIdx, players, onAdvance }) {
  const [gs, setGs] = React.useState(null);
  const gsRef = React.useRef(null);
  const pendRef = React.useRef(false);
  const [guessRes, setGuessRes] = React.useState(null);
  const [gameOver, setGameOver] = React.useState(false);

  // Card numeric value: 2-9 face, 10/J/Q/K=10, A=11
  const cardVal = (v) => {
    if (v === 'A') return 11;
    if (['10','J','Q','K'].includes(v)) return 10;
    return parseInt(v) || 0;
  };

  React.useEffect(()=>{
    const d = shuffleDeck(generateDeck(1));
    const st = { deck:d, deckPos:0, activePids:players.map(p=>p.id), turnPos:0, drinkMap:{}, playerLives:{}, pot:1 };
    players.forEach(p=>{ st.playerLives[p.id]=1; });
    gsRef.current=st; setGs({...st}); setGuessRes(null); setGameOver(false); pendRef.current=false;
  },[gameIdx]);

  if (!gs) return null;
  const { deck, deckPos, activePids, turnPos, drinkMap, playerLives } = gs;
  const pot = gs.pot || 1;
  const currentCard = deck[deckPos];
  const nextCard = deck[deckPos+1];
  const currentPid = activePids[turnPos % Math.max(activePids.length,1)];
  const currentPlayer = players.find(p=>p.id===currentPid);
  const remaining = deck.length - deckPos - 1;

  const handleGuess = (guess) => {
    if (pendRef.current || !nextCard || gameOver) return;
    const cv = cardVal(currentCard.value);
    const nv = cardVal(nextCard.value);
    const same = cv === nv;
    const ok = same ? null : (guess==='K' && nv<cv) || (guess==='N' && nv>cv);

    pendRef.current = true;
    setGuessRes({ correct:ok, same, pid:currentPid, card:nextCard, pot });

    setTimeout(()=>{
      const st = gsRef.current;
      const pid = st.activePids[st.turnPos % Math.max(st.activePids.length,1)];
      let nst = { ...st, deckPos:st.deckPos+1 };

      if (same) {
        // Same value: same player stays, pot grows
        nst = { ...nst, pot:(st.pot||1)+1 };
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
        // Correct: next player, pot resets
        nst = { ...nst, turnPos:(st.turnPos+1)%st.activePids.length, pot:1 };
      }

      gsRef.current=nst; setGs({...nst}); setGuessRes(null); pendRef.current=false;
    }, 1800);
  };

  if(gameOver) return (
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
  );

  const LargeCard = ({ card, faceDown }) => {
    if (faceDown || !card) return (
      <div style={{ width:128, height:178, borderRadius:14, background:'#1B2340', boxShadow:'0 6px 22px rgba(0,0,0,0.22)', display:'flex', alignItems:'center', justifyContent:'center', position:'relative', flexShrink:0 }}>
        <div style={{ position:'absolute', top:8, right:8, background:'rgba(255,255,255,0.13)', borderRadius:8, padding:'2px 8px', display:'flex', alignItems:'center', gap:3 }}>
          <span style={{ fontSize:10, color:'rgba(255,255,255,0.5)' }}>⊞</span>
          <span style={{ fontFamily:'monospace', fontWeight:700, fontSize:11, color:'rgba(255,255,255,0.65)' }}>{remaining}</span>
        </div>
        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:54, color:'rgba(255,255,255,0.35)' }}>?</span>
      </div>
    );
    const red = SUIT_RED.has(card.suit);
    const col = red ? '#CC2020' : '#141424';
    return (
      <div style={{ width:128, height:178, borderRadius:14, background:'#fff', boxShadow:'0 6px 22px rgba(0,0,0,0.14)', border:'1px solid rgba(0,0,0,0.07)', display:'flex', flexDirection:'column', padding:'10px 12px', position:'relative', flexShrink:0, animation: guessRes?.card===card ? 'popIn .3s' : 'none' }}>
        <div style={{ fontFamily:'Georgia,serif', fontWeight:700, fontSize:30, color:col, lineHeight:1 }}>{card.value}</div>
        <div style={{ fontFamily:'Georgia,serif', fontSize:22, color:col, lineHeight:1.1 }}>{card.suit}</div>
        <div style={{ position:'absolute', bottom:12, left:'50%', transform:'translateX(-50%)', fontFamily:'Georgia,serif', fontSize:44, color:col, lineHeight:1 }}>{card.suit}</div>
      </div>
    );
  };

  const shownCard = guessRes ? guessRes.card : null;

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:12 }}>

      {/* Current player + drink pot counter */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', width:'100%' }}>
        <div style={{ display:'flex', flexDirection:'column', alignItems:'flex-start', gap:4 }}>
          <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.12em' }}>Ő tippel</div>
          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
            <div style={{ width:40, height:40, borderRadius:'50%', background:currentPlayer?.color||T.coral, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:'#fff' }}>
              {(currentPlayer?.name||'?').charAt(0).toUpperCase()}
            </div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:17, color:T.ink }}>{currentPlayer?.name||'?'}</div>
          </div>
        </div>

        {/* Drink pot */}
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:2, background:'rgba(255,255,255,0.65)', borderRadius:14, padding:'8px 14px', boxShadow:'0 1px 6px rgba(0,0,0,0.08)' }}>
          <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>Tét</div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:22, color: pot>=3 ? '#D05040' : pot>=2 ? '#E0A030' : '#1B2340', lineHeight:1 }}>{pot}</div>
          <div style={{ fontFamily:T.font, fontSize:10, color:T.inkSoft }}>korty</div>
        </div>
      </div>

      {/* Cards */}
      <div style={{ display:'flex', alignItems:'center', gap:14 }}>
        <LargeCard card={currentCard} faceDown={false} />
        <div style={{ fontSize:24, color:T.inkSoft, fontWeight:700 }}>→</div>
        {shownCard ? <LargeCard card={shownCard} faceDown={false} /> : <LargeCard card={null} faceDown={true} />}
      </div>

      {/* Result feedback */}
      {guessRes && (
        <div style={{ padding:'8px 20px', borderRadius:12, textAlign:'center', animation:'popIn .3s',
          background: guessRes.same ? 'rgba(240,192,64,0.18)' : guessRes.correct ? `${T.mint}22` : `${T.coral}22`,
          border: `2px solid ${guessRes.same ? '#E0A030' : guessRes.correct ? T.mint : T.coral}` }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color: guessRes.same ? '#C08020' : guessRes.correct ? T.mint : T.coral }}>
            {guessRes.same
              ? `🔄 Ugyanaz az érték! Tét: +1 → ${guessRes.pot+1} korty`
              : guessRes.correct
                ? '✓ Helyes! Következő játékos.'
                : `✗ Rontott! ${players.find(p=>p.id===guessRes.pid)?.name} iszik ${guessRes.pot} kortyt!`
            }
          </div>
        </div>
      )}

      {/* Kisebb / Nagyobb buttons */}
      {!guessRes && (
        <div style={{ display:'flex', gap:10, width:'100%' }}>
          <button onClick={()=>handleGuess('K')} style={{ flex:1, minHeight:58, border:'none', background:'#F2C4BC', color:'#C0504A', fontFamily:T.font, fontWeight:700, fontSize:17, borderRadius:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:6 }}>
            <span style={{ fontSize:14 }}>↓</span><span>Kisebb</span>
          </button>
          <button onClick={()=>handleGuess('N')} style={{ flex:1, minHeight:58, border:'none', background:'#B8E8D4', color:'#2E8B60', fontFamily:T.font, fontWeight:700, fontSize:17, borderRadius:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:6 }}>
            <span style={{ fontSize:14 }}>↑</span><span>Nagyobb</span>
          </button>
        </div>
      )}

      {/* Active player chips */}
      <div style={{ display:'flex', gap:6, flexWrap:'wrap', justifyContent:'center' }}>
        {activePids.map(pid=>{
          const p=players.find(x=>x.id===pid);
          const isActive = pid===currentPid;
          return (
            <div key={pid} style={{ display:'flex', alignItems:'center', gap:6, padding:'5px 12px', borderRadius:999, background: isActive ? 'rgba(255,255,255,0.75)' : 'rgba(255,255,255,0.4)', border:`1.5px solid ${isActive ? p?.color||T.mint : 'transparent'}`, boxShadow: isActive ? '0 1px 6px rgba(0,0,0,0.1)' : 'none' }}>
              <div style={{ width:14, height:14, borderRadius:'50%', background:p?.color, flexShrink:0 }}/>
              <div style={{ fontFamily:T.font, fontSize:12, fontWeight: isActive ? 700 : 500, color: isActive ? T.ink : T.inkSoft }}>{p?.name||'?'}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}"""

html = re.sub(
    r'function KisebbGame\(\{ gameIdx, players, onAdvance \}\) \{.*?\n\}(?=\n\nfunction UvegGame)',
    NEW_KISEBB, html, flags=re.DOTALL
)

html = html.replace(
    'Verzió 5.17 · DNR · 2026.05.30 22:00',
    'Verzió 5.18 · DNR · 2026.05.30 23:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
