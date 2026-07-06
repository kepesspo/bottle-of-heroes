import re
with open('index.html', encoding='utf-8') as f:
    c = f.read()

# ═══ 1. "Ki rontott?" sáv kizárása blackjacknél ══════════════════════════════
OLD = "currentGameId !== 'ovfj'"
# a Csapat loser-picker feltételsorban van; egyedi anchor kell
i = c.index("{currentGame.category === 'Csapat' && currentGameId !== 'loverseny'")
j = c.index("&&", c.index("currentGameId !== 'ovfj'", i)) if False else None
seg_end = c.index("(", i + 10)
# egyszerűbb: az 'ovfj' kizárás után fűzzük be a blackjacket ebben a blokkban
k = c.index("currentGameId !== 'ovfj'", i)
c = c[:k] + "currentGameId !== 'blackjack' && " + c[k:]

# ═══ 2. bjResultFor → zseton delta ═══════════════════════════════════════════
OLD = """function bjResultFor(state, pid) {
  const ds = bjScore(state.dealerHand), dBJ = bjIsBlackjack(state.dealerHand);
  const hand = state.hands[pid] || [], ps = bjScore(hand), pBJ = bjIsBlackjack(hand);
  const bet = state.bets[pid] || 1;
  if (state.bust[pid])   return { label:'Besokalltál 💀', drink: bet, give: 0 };
  if (pBJ && dBJ)        return { label:'Döntetlen — dupla Blackjack', drink: 0, give: 0 };
  if (pBJ)               return { label:'Blackjack! 🂡', drink: 0, give: Math.ceil(bet * 1.5) };
  if (dBJ)               return { label:'Osztó Blackjack', drink: bet, give: 0 };
  if (ds > 21)           return { label:'Osztó besokallt — nyertél! 🏆', drink: 0, give: bet };
  if (ps > ds)           return { label:'Nyertél! 🏆', drink: 0, give: bet };
  if (ps === ds)         return { label:'Döntetlen', drink: 0, give: 0 };
  return { label:'Vesztettél', drink: bet, give: 0 };
}"""
NEW = """function bjResultFor(state, pid) {
  const ds = bjScore(state.dealerHand), dBJ = bjIsBlackjack(state.dealerHand);
  const hand = state.hands[pid] || [], ps = bjScore(hand), pBJ = bjIsBlackjack(hand);
  const bet = state.bets[pid] || 1;
  if (state.bust[pid])   return { label:'Besokallt 💀', delta: -bet };
  if (pBJ && dBJ)        return { label:'Döntetlen — dupla Blackjack', delta: 0 };
  if (pBJ)               return { label:'Blackjack! 🂡', delta: Math.ceil(bet * 1.5) };
  if (dBJ)               return { label:'Osztó Blackjack', delta: -bet };
  if (ds > 21)           return { label:'Osztó besokallt — nyert! 🏆', delta: bet };
  if (ps > ds)           return { label:'Nyert! 🏆', delta: bet };
  if (ps === ds)         return { label:'Döntetlen', delta: 0 };
  return { label:'Vesztett', delta: -bet };
}
// Korty jóváírása a szoba players listájába (vendég telefonról)
function bjBookDrinksRemote(code, pid, n) {
  if (!code || !n) return;
  try {
    const dbb = firebase.firestore();
    dbb.collection('rooms').doc(code).get().then(snap => {
      const ps = (snap.data() || {}).players || [];
      return dbb.collection('rooms').doc(code).update({ players: ps.map(p => p.id === pid ? { ...p, drinks: (p.drinks || 0) + n } : p) });
    }).catch(() => {});
  } catch(e) {}
}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 3. Init: startStack/chips/cashedOut/roundsPlayed ════════════════════════
OLD = """      const parts = players.slice(1).map(p => p.id);
      const bets = {}; parts.forEach(pid => bets[pid] = 1);
      setLocalState({ phase:'betting', gameIdx, hostId: hostPlayer?.id || 'host', participants: parts, deck: bjNewDeck(), hands: {}, dealerHand: [], bets, betsDone: {}, stood: {}, bust: {}, doubled: {}, currentTurn: null });"""
NEW = """      const parts = players.slice(1).map(p => p.id);
      const bets = {}; const chips = {};
      parts.forEach(pid => { bets[pid] = 1; chips[pid] = 10; });
      setLocalState({ phase:'betting', gameIdx, hostId: hostPlayer?.id || 'host', participants: parts, deck: bjNewDeck(), hands: {}, dealerHand: [], bets, betsDone: {}, stood: {}, bust: {}, doubled: {}, currentTurn: null, startStack: 10, chips, cashedOut: {}, roundsPlayed: 0 });"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = """        bjState: { phase:'joining', gameIdx, hostId: hostPlayer?.id || 'host', participants: [], deck: [], hands: {}, dealerHand: [], bets: {}, betsDone: {}, stood: {}, bust: {}, doubled: {}, currentTurn: null },"""
NEW = """        bjState: { phase:'joining', gameIdx, hostId: hostPlayer?.id || 'host', participants: [], deck: [], hands: {}, dealerHand: [], bets: {}, betsDone: {}, stood: {}, bust: {}, doubled: {}, currentTurn: null, startStack: 10, chips: {}, cashedOut: {}, roundsPlayed: 0 },"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 4. hostStart/hostNewRound → közös startRound (zseton-tudatos) ═══════════
OLD = """  function hostStart() {
    const parts = players.filter(p => takenIds.includes(p.id) && p.id !== bjState.hostId).map(p => p.id);
    if (!parts.length) return;
    const bets = {}; parts.forEach(pid => bets[pid] = (bjState.bets || {})[pid] || 1);
    update({ ...bjState, phase:'betting', participants: parts, bets, betsDone: {}, deck: bjNewDeck(), hands: {}, dealerHand: [], stood: {}, bust: {}, doubled: {}, currentTurn: null });
  }

  function hostNewRound() {
    const parts = isOnline
      ? players.filter(p => takenIds.includes(p.id) && p.id !== bjState.hostId).map(p => p.id)
      : bjState.participants;
    const bets = {}; parts.forEach(pid => bets[pid] = (bjState.bets || {})[pid] || 1);
    update({ ...bjState, phase:'betting', participants: parts, bets, betsDone: {}, deck: bjNewDeck(), hands: {}, dealerHand: [], stood: {}, bust: {}, doubled: {}, currentTurn: null });
  }"""
NEW = """  function startRound() {
    const claimed = isOnline
      ? players.filter(p => takenIds.includes(p.id) && p.id !== bjState.hostId).map(p => p.id)
      : players.slice(1).map(p => p.id);
    const chips = { ...(bjState.chips || {}) };
    const startStack = bjState.startStack || 10;
    claimed.forEach(pid => { if (chips[pid] === undefined) chips[pid] = startStack; });
    // csak akinek van zsetonja és nem szállt ki
    const parts = claimed.filter(pid => !(bjState.cashedOut || {})[pid] && chips[pid] > 0);
    if (!parts.length) return;
    const bets = {}; parts.forEach(pid => bets[pid] = Math.max(1, Math.min((bjState.bets || {})[pid] || 1, chips[pid])));
    update({ ...bjState, phase:'betting', participants: parts, chips, bets, betsDone: {}, deck: bjNewDeck(), hands: {}, dealerHand: [], stood: {}, bust: {}, doubled: {}, currentTurn: null });
  }
  const hostStart = startRound;
  const hostNewRound = startRound;"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 5. Kör lezárása: zseton-elszámolás (korty-könyvelés helyett) ═════════════
OLD = """    const timeout = setTimeout(() => {
      const finalState = { ...bjState, deck, dealerHand, phase:'results' };
      update(finalState);
      // Kortyok automatikus könyvelése a játékos statokba
      if (typeof onLiveDrinkUpdate === 'function') {
        const deltas = {};
        (bjState.participants || []).forEach(pid => {
          const r = bjResultFor(finalState, pid);
          if (r.drink > 0) deltas[pid] = r.drink;
        });
        if (Object.keys(deltas).length) onLiveDrinkUpdate(deltas);
      }
    }, 1500);"""
NEW = """    const timeout = setTimeout(() => {
      const preState = { ...bjState, deck, dealerHand };
      const chips = { ...(bjState.chips || {}) };
      const startStack = bjState.startStack || 10;
      (bjState.participants || []).forEach(pid => {
        const r = bjResultFor(preState, pid);
        chips[pid] = Math.max(0, (chips[pid] === undefined ? startStack : chips[pid]) + r.delta);
      });
      update({ ...preState, phase:'results', chips, roundsPlayed: (bjState.roundsPlayed || 0) + 1 });
    }, 1500);"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 6. Host akciók: kiszállás / visszaszállás (korty-könyveléssel) ═══════════
OLD = """  function getPlayer(pid) { return players.find(p => p.id === pid); }"""
NEW = """  function getPlayer(pid) { return players.find(p => p.id === pid); }

  function bookDrinks(pid, n) {
    if (!n) return;
    if (typeof onLiveDrinkUpdate === 'function') onLiveDrinkUpdate({ [pid]: n });
  }
  function hostCashOut(pid) {
    const startStack = bjState.startStack || 10;
    const ch = (bjState.chips || {})[pid] || 0;
    bookDrinks(pid, Math.max(0, startStack - ch));
    update({ ...bjState, cashedOut: { ...(bjState.cashedOut || {}), [pid]: true } });
  }
  function hostRebuy(pid, mustDrink) {
    const startStack = bjState.startStack || 10;
    if (mustDrink) bookDrinks(pid, startStack);
    update({ ...bjState, chips: { ...(bjState.chips || {}), [pid]: startStack }, cashedOut: { ...(bjState.cashedOut || {}), [pid]: false } });
  }"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 7. JoiningView: kezdőkészlet választó ════════════════════════════════════
OLD = """        <button onClick={hostStart} disabled={joined.length === 0} style={{ width:'100%', padding:'14px', borderRadius:16, background: joined.length ? T.mint : T.surfaceMuted, border:'none', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor: joined.length ? 'pointer' : 'default' }}>
          Kezdés ({joined.length} játékos)
        </button>"""
NEW = """        <div style={{ background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Kezdő kortykészlet 🍺</div>
          <div style={{ display:'flex', gap:8 }}>
            {[5, 10, 20].map(v => (
              <button key={v} onClick={() => update({ ...bjState, startStack: v })} style={{ flex:1, padding:'12px 0', borderRadius:12, border:`2px solid ${(bjState.startStack || 10) === v ? T.mint : T.surfaceMuted}`, background: (bjState.startStack || 10) === v ? T.mintSoft : 'transparent', fontFamily:T.font, fontWeight:900, fontSize:17, color: (bjState.startStack || 10) === v ? T.mint : T.inkSoft, cursor:'pointer' }}>{v}</button>
            ))}
          </div>
          <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:8 }}>Kiszálláskor: aki ez alatt van, a különbséget issza — aki felette, kiosztja (az osztónak is adhatja! 🎩)</div>
        </div>
        <button onClick={hostStart} disabled={joined.length === 0} style={{ width:'100%', padding:'14px', borderRadius:16, background: joined.length ? T.mint : T.surfaceMuted, border:'none', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor: joined.length ? 'pointer' : 'default' }}>
          Kezdés ({joined.length} játékos)
        </button>"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 8. BettingView: készlet kijelzés + clamp + offline stack választó ════════
OLD = """      {(bjState.participants || []).map(pid => {
        const p = getPlayer(pid);
        const bet = bjState.bets[pid] || 1;
        const done = !!bjState.betsDone[pid];
        return (
          <div key={pid} style={{ display:'flex', alignItems:'center', gap:12, marginBottom:10, background:T.surface, borderRadius:14, padding:'10px 14px', boxShadow:T.shadow }}>
            <BJAvatar p={p} size={32} />
            <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink, flex:1 }}>{p?.name || pid}</span>
            {!isOnline && (
              <button onClick={() => update({ ...bjState, bets: { ...bjState.bets, [pid]: Math.max(1, bet - 1) } })} style={{ width:30, height:30, borderRadius:8, border:'none', background:T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:18, cursor:'pointer', color:T.ink }}>−</button>
            )}
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, minWidth:52, textAlign:'center' }}>{bet} 🍺</span>
            {!isOnline && (
              <button onClick={() => update({ ...bjState, bets: { ...bjState.bets, [pid]: Math.min(10, bet + 1) } })} style={{ width:30, height:30, borderRadius:8, border:'none', background:T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:18, cursor:'pointer', color:T.ink }}>+</button>
            )}
            {isOnline && (
              <span style={{ fontFamily:T.font, fontSize:12, fontWeight:T.weightTitle, color: done ? T.mint : T.inkSoft }}>{done ? '✓ Kész' : '…'}</span>
            )}
          </div>
        );
      })}"""
NEW = """      {!isOnline && (bjState.roundsPlayed || 0) === 0 && (
        <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12, justifyContent:'center' }}>
          <span style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft }}>Kezdőkészlet:</span>
          {[5, 10, 20].map(v => (
            <button key={v} onClick={() => { const chips = {}; (bjState.participants || []).forEach(pp => chips[pp] = v); update({ ...bjState, startStack: v, chips }); }} style={{ padding:'6px 14px', borderRadius:10, border:`2px solid ${(bjState.startStack || 10) === v ? T.mint : T.surfaceMuted}`, background: (bjState.startStack || 10) === v ? T.mintSoft : 'transparent', fontFamily:T.font, fontWeight:900, fontSize:14, color: (bjState.startStack || 10) === v ? T.mint : T.inkSoft, cursor:'pointer' }}>{v}</button>
          ))}
        </div>
      )}
      {(bjState.participants || []).map(pid => {
        const p = getPlayer(pid);
        const chips = (bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : (bjState.startStack || 10);
        const bet = Math.min(bjState.bets[pid] || 1, chips);
        const done = !!bjState.betsDone[pid];
        return (
          <div key={pid} style={{ display:'flex', alignItems:'center', gap:12, marginBottom:10, background:T.surface, borderRadius:14, padding:'10px 14px', boxShadow:T.shadow }}>
            <BJAvatar p={p} size={32} />
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink }}>{p?.name || pid}</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>Készlet: {chips} 🍺</div>
            </div>
            {!isOnline && (
              <button onClick={() => update({ ...bjState, bets: { ...bjState.bets, [pid]: Math.max(1, bet - 1) } })} style={{ width:30, height:30, borderRadius:8, border:'none', background:T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:18, cursor:'pointer', color:T.ink }}>−</button>
            )}
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, minWidth:52, textAlign:'center' }}>{bet} 🍺</span>
            {!isOnline && (
              <button onClick={() => update({ ...bjState, bets: { ...bjState.bets, [pid]: Math.min(chips, bet + 1) } })} style={{ width:30, height:30, borderRadius:8, border:'none', background:T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:18, cursor:'pointer', color:T.ink }}>+</button>
            )}
            {isOnline && (
              <span style={{ fontFamily:T.font, fontSize:12, fontWeight:T.weightTitle, color: done ? T.mint : T.inkSoft }}>{done ? '✓ Kész' : '…'}</span>
            )}
          </div>
        );
      })}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 9. PlayingView sor: készlet is látszódjon ════════════════════════════════
OLD = """                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.ink, flex:1 }}>{p?.name || pid} <span style={{ color:T.inkSoft, fontWeight:400 }}>· {bjState.bets[pid] || 1} korty</span></span>"""
NEW = """                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.ink, flex:1 }}>{p?.name || pid} <span style={{ color:T.inkSoft, fontWeight:400 }}>· tét {bjState.bets[pid] || 1} · készlet {(bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : (bjState.startStack || 10)} 🍺</span></span>"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 10. Host ResultsView: zseton-elszámolás + kiszállás/visszaszállás ════════
OLD = """        {(bjState.participants || []).map(pid => {
          const p = getPlayer(pid);
          const hand = bjState.hands[pid] || [];
          const res = bjResultFor(bjState, pid);
          return (
            <div key={pid} style={{ marginBottom:10, background:T.surface, borderRadius:14, padding:'10px 14px', boxShadow:T.shadow }}>
              <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}>
                <BJAvatar p={p} size={28} />
                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink, flex:1 }}>{p?.name || pid}</span>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.inkSoft }}>{bjScore(hand)}</span>
              </div>
              <div style={{ display:'flex', gap:5, flexWrap:'wrap', marginBottom:6 }}>
                {hand.map((c, i) => <BJCardEl key={i} card={c} small />)}
              </div>
              <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color: res.drink > 0 ? T.coral : res.give > 0 ? T.mint : T.inkSoft }}>{res.label}</span>
                {res.drink > 0 && <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.coral }}>iszik {res.drink} kortyot 🍺</span>}
                {res.give > 0 && <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.mint }}>kioszt {res.give} kortyot 🎁</span>}
              </div>
            </div>
          );
        })}
        <div style={{ display:'flex', gap:10, marginTop:14 }}>
          <button onClick={hostNewRound} style={{ flex:1, padding:'14px', borderRadius:16, background:'#1a6b3c', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>Új kör 🔄</button>
          <button onClick={onAdvance} style={{ flex:1, padding:'14px', borderRadius:16, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>Kövi játék →</button>
        </div>"""
NEW = """        {(bjState.participants || []).map(pid => {
          const p = getPlayer(pid);
          const hand = bjState.hands[pid] || [];
          const res = bjResultFor(bjState, pid);
          const startStack = bjState.startStack || 10;
          const chips = (bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : startStack;
          const out = !!(bjState.cashedOut || {})[pid];
          const broke = !out && chips === 0;
          const diff = chips - startStack;
          return (
            <div key={pid} style={{ marginBottom:10, background:T.surface, borderRadius:14, padding:'10px 14px', boxShadow:T.shadow, opacity: out ? 0.6 : 1 }}>
              <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}>
                <BJAvatar p={p} size={28} />
                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink, flex:1 }}>{p?.name || pid}{out ? ' · kiszállt 🚪' : ''}</span>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.inkSoft }}>{bjScore(hand)}</span>
              </div>
              <div style={{ display:'flex', gap:5, flexWrap:'wrap', marginBottom:6 }}>
                {hand.map((c, i) => <BJCardEl key={i} card={c} small />)}
              </div>
              <div style={{ display:'flex', alignItems:'center', gap:8, flexWrap:'wrap' }}>
                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft }}>{res.label}</span>
                <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft }}>
                  {res.delta > 0 ? '+' : ''}{res.delta} → {chips} 🍺
                </span>
              </div>
              {broke && (
                <div style={{ marginTop:8, padding:'8px 10px', borderRadius:10, background:T.coralSoft }}>
                  <div style={{ fontFamily:T.font, fontSize:13, fontWeight:900, color:T.coral }}>💀 Elfogyott a készlete — igyon {startStack} kortyot!</div>
                  {!isOnline && (
                    <div style={{ display:'flex', gap:8, marginTop:8 }}>
                      <button onClick={() => hostRebuy(pid, true)} style={{ flex:1, padding:'9px', borderRadius:10, border:'none', background:T.mint, fontFamily:T.font, fontWeight:800, fontSize:12, color:'#fff', cursor:'pointer' }}>🔄 Megitta — újra beszáll</button>
                      <button onClick={() => update({ ...bjState, cashedOut: { ...(bjState.cashedOut || {}), [pid]: true } })} style={{ flex:1, padding:'9px', borderRadius:10, border:'none', background:'#555', fontFamily:T.font, fontWeight:800, fontSize:12, color:'#fff', cursor:'pointer' }}>🚪 Megitta — kiszáll</button>
                    </div>
                  )}
                </div>
              )}
              {!broke && !out && !isOnline && (
                <button onClick={() => hostCashOut(pid)} style={{ marginTop:8, width:'100%', padding:'8px', borderRadius:10, border:`1.5px solid ${T.surfaceMuted}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:12, color:T.inkSoft, cursor:'pointer' }}>
                  🚪 Kiszáll {diff < 0 ? `— iszik ${-diff} kortyot` : diff > 0 ? `— kioszt ${diff} kortyot (az osztónak is adhatja 🎩)` : '— nullán van, se nem iszik, se nem oszt'}
                </button>
              )}
            </div>
          );
        })}
        <button onClick={hostNewRound} style={{ width:'100%', padding:'14px', borderRadius:16, background:'#1a6b3c', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer', marginTop:14 }}>Új kör 🔄</button>"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 11. Observer: zseton kijelzés, tét clamp, eredmény + kiszállás UI ════════
OLD = """  const setMyBet = (v) => { if (typeof syncRoom === 'function') syncRoom(code, { bjState: { bets: { [playerId]: Math.max(1, Math.min(10, v)) } } }); };"""
NEW = """  const startStack = bj.startStack || 10;
  const myChips = (bj.chips || {})[playerId] !== undefined ? bj.chips[playerId] : startStack;
  const amOut = !!(bj.cashedOut || {})[playerId];
  const setMyBet = (v) => { if (typeof syncRoom === 'function') syncRoom(code, { bjState: { bets: { [playerId]: Math.max(1, Math.min(myChips, v)) } } }); };
  const guestRebuy = (drinkN) => {
    if (drinkN > 0) bjBookDrinksRemote(code, playerId, drinkN);
    bjWrite(code, { ...bj, chips: { ...(bj.chips || {}), [playerId]: startStack }, cashedOut: { ...(bj.cashedOut || {}), [playerId]: false } });
  };
  const guestCashOut = () => {
    const deficit = Math.max(0, startStack - myChips);
    if (deficit > 0) bjBookDrinksRemote(code, playerId, deficit);
    bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } });
  };"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = """          {bj.phase !== 'joining' && inRound && <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:13, color:T.inkSoft }}>Tét: {myBet} korty 🍺</span>}"""
NEW = """          {bj.phase !== 'joining' && <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:13, color:T.inkSoft }}>Készlet: <b style={{ color: myChips < startStack ? T.coral : T.mint }}>{myChips}</b> 🍺{inRound ? ` · Tét: ${myBet}` : ''}</span>}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# kimaradtál nézet → kiszállt / visszaszállás kezelése
OLD = """        {bj.phase !== 'joining' && !inRound && (
          <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:44 }}>⏳</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginTop:8 }}>Ebből a körből kimaradtál</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:6 }}>A következő körben már játszol!</div>
          </div>
        )}"""
NEW = """        {bj.phase !== 'joining' && !inRound && (
          <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:44 }}>{amOut ? '🚪' : '⏳'}</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginTop:8 }}>{amOut ? 'Kiszálltál' : 'Ebből a körből kimaradtál'}</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:6 }}>{amOut ? 'Visszaszállhatsz egy új készlettel — a következő körtől játszol.' : 'A következő körben már játszol!'}</div>
            {amOut && (
              <button onClick={() => guestRebuy(0)} style={{ marginTop:14, width:'100%', padding:'13px', borderRadius:14, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>🔄 Visszaszállok ({startStack} 🍺 készlettel)</button>
            )}
          </div>
        )}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# tét fázis: max jelzés
OLD = """            <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:16 }}>Ha veszítesz, ennyit iszol — ha nyersz, ennyit osztasz ki!</div>"""
NEW = """            <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:16 }}>A tét a kortykészletedből megy — max {myChips} 🍺</div>"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# eredmény blokk a telefonon: delta + készlet + kiszállás/rebuy
OLD = """              {bj.phase === 'results' && (() => {
                const res = bjResultFor(bj, playerId);
                return (
                  <div style={{ marginTop:12, padding:'12px', borderRadius:14, background: res.drink > 0 ? T.coralSoft : res.give > 0 ? `${T.mint}20` : T.surfaceMuted, textAlign:'center' }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color: res.drink > 0 ? T.coral : res.give > 0 ? T.mint : T.ink }}>{res.label}</div>
                    {res.drink > 0 && <div style={{ fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color:T.coral, marginTop:4 }}>Igyál {res.drink} kortyot! 🍺</div>}
                    {res.give > 0 && <div style={{ fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color:T.mint, marginTop:4 }}>Kioszthatsz {res.give} kortyot! 🎁</div>}
                  </div>
                );
              })()}"""
NEW = """              {bj.phase === 'results' && (() => {
                const res = bjResultFor(bj, playerId);
                const broke = !amOut && myChips === 0;
                const diff = myChips - startStack;
                const dealerName = players.find(p => p.id === bj.hostId)?.name || 'az osztó';
                return (
                  <div style={{ marginTop:12 }}>
                    <div style={{ padding:'12px', borderRadius:14, background: res.delta < 0 ? T.coralSoft : res.delta > 0 ? `${T.mint}20` : T.surfaceMuted, textAlign:'center' }}>
                      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.ink }}>{res.label}</div>
                      <div style={{ fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft, marginTop:4 }}>
                        {res.delta > 0 ? '+' : ''}{res.delta} 🍺 → készleted: {myChips}
                      </div>
                    </div>
                    {broke ? (
                      <div style={{ marginTop:10, padding:'12px', borderRadius:14, background:T.coralSoft, textAlign:'center' }}>
                        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.coral }}>💀 Elfogyott a készleted!</div>
                        <div style={{ fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.coral, marginTop:4 }}>Igyál {startStack} kortyot!</div>
                        <div style={{ display:'flex', gap:8, marginTop:10 }}>
                          <button onClick={() => guestRebuy(startStack)} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🔄 Megittam — újra beszállok</button>
                          <button onClick={() => { bjBookDrinksRemote(code, playerId, startStack); bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } }); }} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:'#555', fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🚪 Kiszállok</button>
                        </div>
                      </div>
                    ) : !amOut ? (
                      <button onClick={guestCashOut} style={{ marginTop:10, width:'100%', padding:'11px', borderRadius:12, border:`1.5px solid ${T.surfaceMuted}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, cursor:'pointer' }}>
                        🚪 Kiszállok {diff < 0 ? `— megiszom ${-diff} kortyot` : diff > 0 ? `— kiosztok ${diff} kortyot (${dealerName} 🎩 is kaphat!)` : '— nullán vagyok'}
                      </button>
                    ) : null}
                  </div>
                );
              })()}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# Többiek lista: készlet mutatása eredménynél
OLD = """                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color: bj.bust[pid] ? T.coral : bjIsBlackjack(hand) ? T.mint : T.inkSoft }}>
                      {bj.bust[pid] ? '💀' : bjIsBlackjack(hand) ? 'BJ 🂡' : bj.phase === 'results' || bj.stood[pid] ? score : hand.length + ' lap'}
                    </span>"""
NEW = """                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color: bj.bust[pid] ? T.coral : bjIsBlackjack(hand) ? T.mint : T.inkSoft }}>
                      {bj.bust[pid] ? '💀' : bjIsBlackjack(hand) ? 'BJ 🂡' : bj.phase === 'results' || bj.stood[pid] ? score : hand.length + ' lap'}
                      {bj.phase === 'results' ? ` · ${(bj.chips || {})[pid] !== undefined ? bj.chips[pid] : startStack} 🍺` : ''}
                    </span>"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

c = re.sub(r'v9\.790', 'v9.791', c, count=2)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Done v9.791")
