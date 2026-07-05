with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. GAMES entry: enable + new desc ─────────────────────────────────────────
OLD_DESC = "desc:'Mindenki tét helyez kortykban, majd az osztó lapokat oszt. Célod hogy közelebb legyél 21-hez mint az osztó, anélkül hogy túlmennél. Hit, Stand vagy Double Down! Az osztó 17-nél megáll.', comingSoon:true }"
NEW_DESC = "desc:'Csatlakozz a telefonoddal, tegyél tétet kortyokban, és játssz az osztó (a host) ellen! Hit, Stand vagy Double Down — aki veszít, megissza a tétjét, aki nyer, kiosztja. Blackjack másfélszeresét ér!' }"
assert OLD_DESC in content, "GAMES desc not found"
content = content.replace(OLD_DESC, NEW_DESC, 1)

# ── 2. Replace whole BlackjackGame with reworked version + observer view ──────
START = "function BlackjackGame({ players, roomCode, gameIdx, gameMeta, onAdvance, onSetHideFooter }) {"
END = "\nfunction BuszGame("
si = content.index(START)
ei = content.index(END, si)

NEW_BJ = '''// ═══════════════ BLACKJACK — shared helpers ═══════════════
const BJ_SUITS = ['♠','♥','♦','♣'];
const BJ_RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K'];
function bjNewDeck() {
  const d = [];
  for (const s of BJ_SUITS) for (const r of BJ_RANKS) d.push(r + s);
  for (let i = d.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [d[i], d[j]] = [d[j], d[i]];
  }
  return d;
}
function bjCardValue(rank) {
  if (['J','Q','K'].includes(rank)) return 10;
  if (rank === 'A') return 11;
  return parseInt(rank);
}
function bjScore(hand) {
  let total = 0, aces = 0;
  for (const c of (hand || [])) {
    const r = c.replace(/[♠♥♦♣]/g, '');
    total += bjCardValue(r);
    if (r === 'A') aces++;
  }
  while (total > 21 && aces > 0) { total -= 10; aces--; }
  return total;
}
function bjIsBlackjack(hand) { return (hand || []).length === 2 && bjScore(hand) === 21; }
function bjIsRed(card) { return card.endsWith('♥') || card.endsWith('♦'); }

function bjAdvanceTurn(state) {
  const parts = state.participants || [];
  const rem = parts.filter(pid => !state.stood[pid] && !state.bust[pid]);
  if (rem.length === 0) return { ...state, phase:'dealer', currentTurn:null };
  const curIdx = parts.indexOf(state.currentTurn);
  const next = rem.find(pid => parts.indexOf(pid) > curIdx) || rem[0];
  return { ...state, currentTurn: next };
}
function bjDoHit(state, pid) {
  const deck = [...state.deck];
  const card = deck.pop();
  const hand = [...(state.hands[pid] || []), card];
  let ns = { ...state, deck, hands: { ...state.hands, [pid]: hand } };
  if (bjScore(hand) > 21) {
    ns.bust = { ...state.bust, [pid]: true };
    ns = bjAdvanceTurn(ns);
  }
  return ns;
}
function bjDoStand(state, pid) {
  return bjAdvanceTurn({ ...state, stood: { ...state.stood, [pid]: true } });
}
function bjDoDouble(state, pid) {
  const deck = [...state.deck];
  const card = deck.pop();
  const hand = [...(state.hands[pid] || []), card];
  let ns = { ...state, deck,
    hands: { ...state.hands, [pid]: hand },
    bets: { ...state.bets, [pid]: (state.bets[pid] || 1) * 2 },
    doubled: { ...state.doubled, [pid]: true },
    stood: { ...state.stood, [pid]: true } };
  if (bjScore(hand) > 21) ns.bust = { ...ns.bust, [pid]: true };
  return bjAdvanceTurn(ns);
}
function bjDeal(state) {
  const deck = [...state.deck];
  const hands = {};
  const dealerHand = [];
  (state.participants || []).forEach(pid => hands[pid] = []);
  // Standard osztás: kör 1 — játékosok + osztó (felfelé), kör 2 — játékosok + osztó (hole card)
  for (let i = 0; i < 2; i++) {
    (state.participants || []).forEach(pid => hands[pid].push(deck.pop()));
    dealerHand.push(deck.pop());
  }
  const stood = {};
  (state.participants || []).forEach(pid => { if (bjIsBlackjack(hands[pid])) stood[pid] = true; });
  const rem = (state.participants || []).filter(pid => !stood[pid]);
  return { ...state, phase: rem.length ? 'playing' : 'dealer', deck, hands, dealerHand, stood, bust: {}, doubled: {}, currentTurn: rem[0] || null };
}
function bjResultFor(state, pid) {
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
}
function bjWrite(code, ns) {
  try { firebase.firestore().collection('rooms').doc(code).update({ bjState: ns }); } catch(e) { console.warn('bjWrite', e); }
}
function BJCardEl({ card, faceDown, small }) {
  const W = small ? 36 : 48, H = small ? 52 : 70;
  if (faceDown) return (
    <div style={{ width:W, height:H, borderRadius:8, background:'#1a3a5c', border:'2px solid rgba(255,255,255,0.25)', display:'grid', placeItems:'center', fontSize:small?18:24, flexShrink:0 }}>🂠</div>
  );
  if (!card) return null;
  const isRed = bjIsRed(card);
  const rank = card.replace(/[♠♥♦♣]/g, '');
  const suit = card.slice(-1);
  return (
    <div style={{ width:W, height:H, borderRadius:8, background:'#fff', border:'2px solid #ddd', display:'flex', flexDirection:'column', padding:'3px 5px', flexShrink:0, userSelect:'none' }}>
      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:small?13:15, color: isRed ? '#c02828' : '#111', lineHeight:1 }}>{rank}</span>
      <div style={{ flex:1, display:'grid', placeItems:'center' }}>
        <span style={{ fontSize:small?16:20, color: isRed ? '#c02828' : '#111' }}>{suit}</span>
      </div>
    </div>
  );
}
function BJAvatar({ p, size }) {
  const s = size || 28;
  return p?.img ? (
    <div style={{ width:s, height:s, borderRadius:'50%', background:p.color||T.mint, overflow:'hidden', flexShrink:0 }}>
      <img src={p.img} style={{ width:s, height:s, objectFit:'cover' }} />
    </div>
  ) : (
    <div style={{ width:s, height:s, borderRadius:'50%', background:p?.color||'#555', display:'grid', placeItems:'center', flexShrink:0 }}>
      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:Math.round(s*0.42), color:'#fff' }}>{(p?.name||'?').charAt(0).toUpperCase()}</span>
    </div>
  );
}

// ═══════════════ BLACKJACK — host (osztó) nézet ═══════════════
function BlackjackGame({ players, roomCode, gameIdx, gameMeta, onAdvance, onSetHideFooter }) {
  const isOnline = !!roomCode;
  const [room, setRoom] = React.useState(null);
  const [localState, setLocalState] = React.useState(null);
  const [showQR, setShowQR] = React.useState(false);
  const initRef = React.useRef(false);
  const bjState = isOnline ? (room?.bjState || null) : localState;
  const takenIds = isOnline ? (room?.bjTakenIds || []) : [];
  const hostPlayer = players && players[0];

  React.useEffect(() => {
    if (!isOnline) {
      // Offline: mindenki a host telefonján játszik, a host az osztó
      const parts = players.slice(1).map(p => p.id);
      const bets = {}; parts.forEach(pid => bets[pid] = 1);
      setLocalState({ phase:'betting', gameIdx, hostId: hostPlayer?.id || 'host', participants: parts, deck: bjNewDeck(), hands: {}, dealerHand: [], bets, betsDone: {}, stood: {}, bust: {}, doubled: {}, currentTurn: null });
      return;
    }
    const unsub = firebase.firestore().collection('rooms').doc(roomCode).onSnapshot(snap => setRoom(snap.data() || null));
    return unsub;
  }, [roomCode, gameIdx]);

  // Host inicializál: csatlakozási fázis
  React.useEffect(() => {
    if (!isOnline || !room || initRef.current) return;
    if (!room.bjState || room.bjState.gameIdx !== gameIdx) {
      initRef.current = true;
      firebase.firestore().collection('rooms').doc(roomCode).update({
        bjState: { phase:'joining', gameIdx, hostId: hostPlayer?.id || 'host', participants: [], deck: [], hands: {}, dealerHand: [], bets: {}, betsDone: {}, stood: {}, bust: {}, doubled: {}, currentTurn: null },
        bjTakenIds: []
      });
    }
  }, [room]);

  function update(ns) {
    if (isOnline) bjWrite(roomCode, ns);
    else setLocalState(ns);
  }

  function hostStart() {
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
  }

  // Osztó automatikus játéka: 17-ig húz, aztán eredmények
  React.useEffect(() => {
    if (!bjState || bjState.phase !== 'dealer') return;
    const deck = [...bjState.deck];
    const dealerHand = [...bjState.dealerHand];
    while (bjScore(dealerHand) < 17) dealerHand.push(deck.pop());
    const timeout = setTimeout(() => {
      update({ ...bjState, deck, dealerHand, phase:'results' });
    }, 1500);
    return () => clearTimeout(timeout);
  }, [bjState?.phase]);

  function getPlayer(pid) { return players.find(p => p.id === pid); }

  if (!bjState) return (
    <div style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center' }}>
      <span style={{ fontFamily:T.font, fontSize:16, color:T.inkSoft }}>Betöltés…</span>
    </div>
  );

  const roomUrl = roomCode ? (window.location.origin + window.location.pathname + '?room=' + roomCode) : null;
  const allBetsDone = (bjState.participants || []).length > 0 && (bjState.participants || []).every(pid => bjState.betsDone[pid]);

  // ── Csatlakozási fázis (online) ──
  const JoiningView = () => {
    const joined = players.filter(p => takenIds.includes(p.id) && p.id !== bjState.hostId);
    return (
      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ textAlign:'center', marginBottom:14 }}>
          <div style={{ fontSize:44 }}>🂡</div>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:T.ink, textTransform:'uppercase', letterSpacing:'0.04em', marginTop:4 }}>Csatlakozás</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:4 }}>A játékosok a telefonjukon válasszák ki magukat — te vagy az osztó!</div>
        </div>
        <div style={{ background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>Csatlakozott játékosok ({joined.length})</div>
          {joined.length === 0 && <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', padding:'10px 0' }}>Még senki — mutasd a QR kódot! 📱</div>}
          {joined.map(p => (
            <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, padding:'6px 0' }}>
              <BJAvatar p={p} size={30} />
              <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink }}>{p.name}</span>
              <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:12, fontWeight:T.weightTitle, color:T.mint }}>✓ Kész</span>
            </div>
          ))}
        </div>
        <button onClick={hostStart} disabled={joined.length === 0} style={{ width:'100%', padding:'14px', borderRadius:16, background: joined.length ? T.mint : T.surfaceMuted, border:'none', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor: joined.length ? 'pointer' : 'default' }}>
          Kezdés ({joined.length} játékos)
        </button>
      </div>
    );
  };

  // ── Tét fázis ──
  const BettingView = () => (
    <div style={{ padding:'0 16px 16px' }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, marginBottom:4, textAlign:'center' }}>Tétek 🍺</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginBottom:14, textAlign:'center' }}>{isOnline ? 'A játékosok a telefonjukon állítják be a tétjüket' : 'Állítsátok be, ki hány kortyot tesz fel'}</div>
      {(bjState.participants || []).map(pid => {
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
      })}
      <button onClick={() => update(bjDeal(bjState))} disabled={isOnline && !allBetsDone} style={{ marginTop:8, width:'100%', padding:'14px', borderRadius:16, background: (!isOnline || allBetsDone) ? '#1a6b3c' : T.surfaceMuted, border:'none', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor:(!isOnline || allBetsDone) ? 'pointer' : 'default' }}>
        {(!isOnline || allBetsDone) ? 'Lapok osztása 🂡' : 'Várakozás a tétekre…'}
      </button>
    </div>
  );

  // ── Játék fázis (asztal nézet) ──
  const PlayingView = () => {
    const revealed = bjState.phase === 'dealer' || bjState.phase === 'results';
    return (
      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ background:'#1a6b3c', borderRadius:18, padding:'12px 14px', marginBottom:14 }}>
          <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:8 }}>
            <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:'rgba(255,255,255,0.85)', textTransform:'uppercase', letterSpacing:'0.06em' }}>🎩 Osztó{revealed ? ` — ${bjScore(bjState.dealerHand)}` : ''}</span>
          </div>
          <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
            {(bjState.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} faceDown={i === 1 && !revealed} />)}
          </div>
        </div>
        {(bjState.participants || []).map(pid => {
          const p = getPlayer(pid);
          const hand = bjState.hands[pid] || [];
          const score = bjScore(hand);
          const isTurn = bjState.currentTurn === pid && bjState.phase === 'playing';
          const isStood = bjState.stood[pid];
          const isBust = bjState.bust[pid];
          const isBJ = bjIsBlackjack(hand);
          const canDouble = hand.length === 2 && !bjState.doubled[pid];
          return (
            <div key={pid} style={{ marginBottom:10, background: isTurn ? T.surface : 'transparent', borderRadius:14, padding: isTurn ? '10px 12px' : '4px 2px', border: isTurn ? `2px solid ${T.mint}` : '2px solid transparent', boxShadow: isTurn ? T.shadow : 'none' }}>
              <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}>
                <BJAvatar p={p} size={26} />
                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.ink, flex:1 }}>{p?.name || pid} <span style={{ color:T.inkSoft, fontWeight:400 }}>· {bjState.bets[pid] || 1} korty</span></span>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color: isBust ? T.coral : isBJ ? T.mint : T.ink }}>
                  {isBust ? 'Bust 💀' : isBJ ? 'BJ! 🂡' : isStood ? `${score} ✋` : score}
                </span>
              </div>
              <div style={{ display:'flex', gap:5, flexWrap:'wrap' }}>
                {hand.map((c, i) => <BJCardEl key={i} card={c} small />)}
              </div>
              {isTurn && !isOnline && (
                <div style={{ display:'flex', gap:8, marginTop:10 }}>
                  <button onClick={() => update(bjDoHit(bjState, pid))} style={{ flex:1, padding:'10px', borderRadius:12, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Hit 🃏</button>
                  <button onClick={() => update(bjDoStand(bjState, pid))} style={{ flex:1, padding:'10px', borderRadius:12, background:'#555', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Stand ✋</button>
                  {canDouble && <button onClick={() => update(bjDoDouble(bjState, pid))} style={{ flex:1, padding:'10px', borderRadius:12, background:'#c07a10', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Double 2×</button>}
                </div>
              )}
              {isTurn && isOnline && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:6, textAlign:'center' }}>📱 A telefonján gondolkodik…</div>
              )}
            </div>
          );
        })}
        {bjState.phase === 'dealer' && (
          <div style={{ textAlign:'center', fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color:T.inkSoft, marginTop:8 }}>Az osztó húz… 🎩</div>
        )}
      </div>
    );
  };

  // ── Eredmények ──
  const ResultsView = () => {
    const ds = bjScore(bjState.dealerHand);
    return (
      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginBottom:12, textAlign:'center' }}>Eredmények</div>
        <div style={{ background:'#1a6b3c', borderRadius:18, padding:'12px 14px', marginBottom:14 }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:'rgba(255,255,255,0.85)', textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:8 }}>🎩 Osztó — {ds}{ds > 21 ? ' (besokallt!)' : ''}{bjIsBlackjack(bjState.dealerHand) ? ' 🂡' : ''}</div>
          <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
            {(bjState.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} small />)}
          </div>
        </div>
        {(bjState.participants || []).map(pid => {
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
        </div>
      </div>
    );
  };

  return (
    <div style={{ flex:1, overflowY:'auto', paddingTop:8 }}>
      {isOnline && roomUrl && bjState.phase === 'joining' && (
        <div style={{ display:'flex', justifyContent:'center', marginBottom:8 }}>
          <button onClick={() => setShowQR(true)} style={{ background:'transparent', border:`1.5px solid ${T.surfaceMuted}`, borderRadius:20, padding:'6px 16px', fontFamily:T.font, fontSize:13, color:T.inkSoft, cursor:'pointer', display:'flex', alignItems:'center', gap:6 }}>
            <span>📱</span> QR kód — csatlakozás
          </button>
        </div>
      )}
      {showQR && roomUrl && <QRModal url={roomUrl} onClose={() => setShowQR(false)} />}
      {bjState.phase === 'joining' && <JoiningView />}
      {bjState.phase === 'betting' && <BettingView />}
      {(bjState.phase === 'playing' || bjState.phase === 'dealer') && <PlayingView />}
      {bjState.phase === 'results' && <ResultsView />}
    </div>
  );
}

// ═══════════════ BLACKJACK — játékos (telefon) nézet ═══════════════
function BlackjackObserverView({ room, code, onLeave }) {
  const bj = room.bjState || null;
  const players = room.players || [];
  const taken = room.bjTakenIds || [];
  const [playerId, setPlayerId] = React.useState(null);
  const [pendingId, setPendingId] = React.useState(null);
  const [unlockPressId, setUnlockPressId] = React.useState(null);
  const [unlockProgress, setUnlockProgress] = React.useState(0);
  const unlockTimerRef = React.useRef(null);
  const unlockRafRef = React.useRef(null);
  const unlockStartRef = React.useRef(null);
  const playerIdRef = React.useRef(playerId);
  React.useEffect(() => { playerIdRef.current = playerId; }, [playerId]);

  const releasePlayer = React.useCallback((pid) => {
    if (!pid || !code) return;
    try { firebase.firestore().collection('rooms').doc(code).update({ bjTakenIds: firebase.firestore.FieldValue.arrayRemove(pid) }); } catch(e) {}
  }, [code]);
  React.useEffect(() => () => { releasePlayer(playerIdRef.current); }, []);
  React.useEffect(() => () => {
    cancelAnimationFrame(unlockRafRef.current);
    clearTimeout(unlockTimerRef.current);
  }, []);

  const startUnlockPress = (pid) => {
    setUnlockPressId(pid); setUnlockProgress(0);
    unlockStartRef.current = Date.now();
    const tick = () => {
      const elapsed = Date.now() - unlockStartRef.current;
      const pct = Math.min(100, (elapsed / 2000) * 100);
      setUnlockProgress(pct);
      if (pct < 100) { unlockRafRef.current = requestAnimationFrame(tick); }
    };
    unlockRafRef.current = requestAnimationFrame(tick);
    unlockTimerRef.current = setTimeout(() => {
      setUnlockPressId(null); setUnlockProgress(0);
      releasePlayer(pid);
    }, 2000);
  };
  const cancelUnlockPress = () => {
    clearTimeout(unlockTimerRef.current);
    cancelAnimationFrame(unlockRafRef.current);
    setUnlockPressId(null); setUnlockProgress(0);
  };

  const Header = (
    <div style={{ margin:'10px 16px 4px', display:'flex', alignItems:'center', justifyContent:'space-between', padding:'10px 14px', background:T.surface, borderRadius:14, boxShadow:T.shadow, flexShrink:0 }}>
      <div style={{ display:'flex', alignItems:'center', gap:8 }}>
        <span style={{ width:8, height:8, borderRadius:'50%', background:'#E03A3A', animation:'pulse 1.4s infinite' }}/>
        <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.ink, letterSpacing:'0.08em', textTransform:'uppercase' }}>🂡 Blackjack · {code}</span>
      </div>
      <button onClick={onLeave} style={{ padding:'4px 10px', border:'none', background:T.coralSoft, color:T.coral, borderRadius:999, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, cursor:'pointer', textTransform:'uppercase', letterSpacing:'0.06em' }}>Kilépés</button>
    </div>
  );

  if (!bj) return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, minHeight:0, overflow:'hidden' }}>
      {Header}
      <div style={{ flex:1, display:'grid', placeItems:'center', fontFamily:T.font, fontSize:15, color:T.inkSoft }}>Várakozás az osztóra… 🎩</div>
    </div>
  );

  // ── Névválasztás (claim, mint a busznál) ──
  if (!playerId) {
    const selectable = players.filter(p => p.id !== bj.hostId);
    const confirmSelection = () => {
      if (!pendingId) return;
      setPlayerId(pendingId);
      try { firebase.firestore().collection('rooms').doc(code).update({ bjTakenIds: firebase.firestore.FieldValue.arrayUnion(pendingId) }); } catch(e) {}
    };
    const pendingPlayer = pendingId ? players.find(p => p.id === pendingId) : null;
    return (
      <div style={{ position:'fixed', inset:0, zIndex:200, background:T.bg, display:'flex', flexDirection:'column' }}>
        <div style={{ flexShrink:0, background:T.bg, paddingTop:16, paddingBottom:12 }}>
          <div style={{ textAlign:'center', padding:'0 18px' }}>
            <div style={{ fontSize:48 }}>🂡</div>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, marginTop:6 }}>Ki vagy te?</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:4 }}>Válaszd ki a neved a listából</div>
          </div>
        </div>
        <div style={{ flex:1, minHeight:0, position:'relative' }}>
          <div style={{ height:'100%', overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'0 18px' }}>
            <div style={{ display:'flex', flexDirection:'column', gap:8, paddingBottom:16 }}>
              {selectable.map(p => {
                const isTaken = taken.includes(p.id);
                const selected = pendingId === p.id;
                const pressing = unlockPressId === p.id;
                return (
                  <div key={p.id} style={{ position:'relative', borderRadius:16, overflow:'hidden' }}>
                    <button
                      onClick={!isTaken ? () => setPendingId(p.id) : undefined}
                      onMouseDown={isTaken ? () => startUnlockPress(p.id) : undefined}
                      onMouseUp={isTaken ? cancelUnlockPress : undefined}
                      onMouseLeave={isTaken ? cancelUnlockPress : undefined}
                      onTouchStart={isTaken ? (e) => { e.preventDefault(); startUnlockPress(p.id); } : undefined}
                      onTouchEnd={isTaken ? cancelUnlockPress : undefined}
                      onTouchCancel={isTaken ? cancelUnlockPress : undefined}
                      style={{ display:'flex', alignItems:'center', gap:12, padding:'14px 16px', background: pressing ? `${T.coral}10` : selected ? `${p.color}18` : T.surface, border:`2px solid ${pressing ? T.coral : selected ? p.color : isTaken ? T.coral+'30' : 'transparent'}`, borderRadius:16, cursor: isTaken ? 'default' : 'pointer', boxShadow: selected ? `0 0 0 1px ${p.color}40, ${T.shadow}` : T.shadow, textAlign:'left', width:'100%', opacity: isTaken && !pressing ? 0.5 : 1, transition:'background .15s, border-color .15s', WebkitUserSelect:'none' }}>
                      <BJAvatar p={p} size={42} />
                      <div style={{ flex:1 }}>
                        <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, color:T.ink }}>{p.name}</div>
                        <div style={{ fontFamily:T.font, fontSize:12, color: isTaken ? T.coral : T.inkSoft, marginTop:2 }}>{pressing ? '🔓 Tartsd nyomva…' : isTaken ? '🔒 Foglalt' : 'Elérhető'}</div>
                      </div>
                      {selected && <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill={p.color}/><path d="M7 13l3 3 7-7" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                    </button>
                    {pressing && <div style={{ position:'absolute', bottom:0, left:0, height:3, background:T.coral, borderRadius:999, width:`${unlockProgress}%`, transition:'none' }} />}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        <div style={{ flexShrink:0, padding:'8px 18px', paddingBottom:'max(16px, env(safe-area-inset-bottom))' }}>
          <button onClick={confirmSelection} disabled={!pendingId} style={{ width:'100%', padding:'15px', borderRadius:16, border:'none', background: pendingId ? (pendingPlayer?.color || T.mint) : T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor: pendingId ? 'pointer' : 'default' }}>
            {pendingPlayer ? `Én vagyok ${pendingPlayer.name}!` : 'Válassz nevet'}
          </button>
        </div>
      </div>
    );
  }

  const me = players.find(p => p.id === playerId);
  const inRound = (bj.participants || []).includes(playerId);
  const myHand = (bj.hands || {})[playerId] || [];
  const myScore = bjScore(myHand);
  const myBet = (bj.bets || {})[playerId] || 1;
  const isMyTurn = bj.phase === 'playing' && bj.currentTurn === playerId;
  const revealed = bj.phase === 'dealer' || bj.phase === 'results';

  const setMyBet = (v) => bjWrite(code, { ...bj, bets: { ...bj.bets, [playerId]: Math.max(1, Math.min(10, v)) } });
  const confirmBet = () => bjWrite(code, { ...bj, betsDone: { ...bj.betsDone, [playerId]: true } });

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, minHeight:0, overflow:'hidden' }}>
      {Header}
      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'12px 16px 24px' }}>

        {/* Én sáv */}
        <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:12 }}>
          <BJAvatar p={me} size={34} />
          <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, color:T.ink }}>{me?.name}</span>
          {bj.phase !== 'joining' && inRound && <span style={{ marginLeft:'auto', fontFamily:T.font, fontSize:13, color:T.inkSoft }}>Tét: {myBet} korty 🍺</span>}
        </div>

        {bj.phase === 'joining' && (
          <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:44 }}>✅</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginTop:8 }}>Csatlakoztál!</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:6 }}>Várj, amíg az osztó elindítja a játékot…</div>
          </div>
        )}

        {bj.phase !== 'joining' && !inRound && (
          <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:44 }}>⏳</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginTop:8 }}>Ebből a körből kimaradtál</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:6 }}>A következő körben már játszol!</div>
          </div>
        )}

        {bj.phase === 'betting' && inRound && (
          <div style={{ background:T.surface, borderRadius:18, padding:'20px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, marginBottom:4 }}>Mennyit teszel fel? 🍺</div>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:16 }}>Ha veszítesz, ennyit iszol — ha nyersz, ennyit osztasz ki!</div>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:18, marginBottom:18 }}>
              <button onClick={() => !bj.betsDone[playerId] && setMyBet(myBet - 1)} disabled={!!bj.betsDone[playerId]} style={{ width:52, height:52, borderRadius:14, border:'none', background:T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:26, cursor:'pointer', color:T.ink, opacity: bj.betsDone[playerId] ? 0.4 : 1 }}>−</button>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:44, color:T.ink, lineHeight:1 }}>{myBet}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>korty</div>
              </div>
              <button onClick={() => !bj.betsDone[playerId] && setMyBet(myBet + 1)} disabled={!!bj.betsDone[playerId]} style={{ width:52, height:52, borderRadius:14, border:'none', background:T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:26, cursor:'pointer', color:T.ink, opacity: bj.betsDone[playerId] ? 0.4 : 1 }}>+</button>
            </div>
            {!bj.betsDone[playerId] ? (
              <button onClick={confirmBet} style={{ width:'100%', padding:'14px', borderRadius:16, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor:'pointer' }}>Tét megerősítése ✓</button>
            ) : (
              <div style={{ fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.mint }}>✓ Kész — várakozás a többiekre…</div>
            )}
          </div>
        )}

        {(bj.phase === 'playing' || bj.phase === 'dealer' || bj.phase === 'results') && inRound && (
          <React.Fragment>
            {/* Osztó */}
            <div style={{ background:'#1a6b3c', borderRadius:18, padding:'12px 14px', marginBottom:12 }}>
              <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:12, color:'rgba(255,255,255,0.85)', textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:8 }}>🎩 Osztó{revealed ? ` — ${bjScore(bj.dealerHand)}${bjScore(bj.dealerHand) > 21 ? ' (besokallt!)' : ''}` : ''}</div>
              <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
                {(bj.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} faceDown={i === 1 && !revealed} small />)}
              </div>
            </div>

            {/* Saját kéz */}
            <div style={{ background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, border: isMyTurn ? `2px solid ${T.mint}` : '2px solid transparent', marginBottom:12 }}>
              <div style={{ display:'flex', alignItems:'center', marginBottom:8 }}>
                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em' }}>A lapjaid</span>
                <span style={{ marginLeft:'auto', fontFamily:T.font, fontWeight:900, fontSize:20, color: bj.bust[playerId] ? T.coral : bjIsBlackjack(myHand) ? T.mint : T.ink }}>
                  {bj.bust[playerId] ? `${myScore} 💀` : bjIsBlackjack(myHand) ? '21 🂡' : myScore}
                </span>
              </div>
              <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
                {myHand.map((c, i) => <BJCardEl key={i} card={c} />)}
              </div>
              {isMyTurn && (
                <div style={{ display:'flex', gap:8, marginTop:14 }}>
                  <button onClick={() => bjWrite(code, bjDoHit(bj, playerId))} style={{ flex:1, padding:'14px 6px', borderRadius:14, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>Hit 🃏</button>
                  <button onClick={() => bjWrite(code, bjDoStand(bj, playerId))} style={{ flex:1, padding:'14px 6px', borderRadius:14, background:'#555', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>Stand ✋</button>
                  {myHand.length === 2 && !bj.doubled[playerId] && (
                    <button onClick={() => bjWrite(code, bjDoDouble(bj, playerId))} style={{ flex:1, padding:'14px 6px', borderRadius:14, background:'#c07a10', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>2×</button>
                  )}
                </div>
              )}
              {bj.phase === 'playing' && !isMyTurn && !bj.stood[playerId] && !bj.bust[playerId] && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:8, textAlign:'center' }}>Várj a körödre… ({players.find(p => p.id === bj.currentTurn)?.name || '?'} jön)</div>
              )}
              {bj.phase === 'results' && (() => {
                const res = bjResultFor(bj, playerId);
                return (
                  <div style={{ marginTop:12, padding:'12px', borderRadius:14, background: res.drink > 0 ? T.coralSoft : res.give > 0 ? `${T.mint}20` : T.surfaceMuted, textAlign:'center' }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color: res.drink > 0 ? T.coral : res.give > 0 ? T.mint : T.ink }}>{res.label}</div>
                    {res.drink > 0 && <div style={{ fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color:T.coral, marginTop:4 }}>Igyál {res.drink} kortyot! 🍺</div>}
                    {res.give > 0 && <div style={{ fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color:T.mint, marginTop:4 }}>Kioszthatsz {res.give} kortyot! 🎁</div>}
                  </div>
                );
              })()}
            </div>

            {/* Többiek */}
            <div style={{ background:T.surface, borderRadius:18, padding:'12px 14px', boxShadow:T.shadow }}>
              <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>Többiek</div>
              {(bj.participants || []).filter(pid => pid !== playerId).map(pid => {
                const p = players.find(pp => pp.id === pid);
                const hand = (bj.hands || {})[pid] || [];
                const score = bjScore(hand);
                const isTurn = bj.phase === 'playing' && bj.currentTurn === pid;
                return (
                  <div key={pid} style={{ display:'flex', alignItems:'center', gap:8, padding:'5px 0', borderBottom:`1px solid ${T.surfaceMuted}` }}>
                    <BJAvatar p={p} size={24} />
                    <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.ink, flex:1 }}>{p?.name || pid}{isTurn ? ' 👈' : ''}</span>
                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color: bj.bust[pid] ? T.coral : bjIsBlackjack(hand) ? T.mint : T.inkSoft }}>
                      {bj.bust[pid] ? '💀' : bjIsBlackjack(hand) ? 'BJ 🂡' : bj.phase === 'results' || bj.stood[pid] ? score : hand.length + ' lap'}
                    </span>
                  </div>
                );
              })}
              {(bj.participants || []).filter(pid => pid !== playerId).length === 0 && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, textAlign:'center', padding:'6px 0' }}>Egyedül játszol az osztó ellen</div>
              )}
            </div>
          </React.Fragment>
        )}
      </div>
    </div>
  );
}
'''

content = content[:si] + NEW_BJ + content[ei:]

# ── 3. ObserverView routing: blackjack branch before busz block ───────────────
OLD_ROUTE = "  if (_ovCurG === 'kisebb') return <KisebbObserverView code={code} room={room} observerName={observerName} />;"
NEW_ROUTE = OLD_ROUTE + "\n  if (_ovCurG === 'blackjack') return <BlackjackObserverView room={room} code={code} onLeave={onLeave} />;"
assert OLD_ROUTE in content, "observer route anchor not found"
content = content.replace(OLD_ROUTE, NEW_ROUTE, 1)

# ── 4. Version bump ───────────────────────────────────────────────────────────
import re
content = re.sub(r'v9\\.777', 'v9.778', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.778")
