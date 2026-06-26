#!/usr/bin/env python3
"""Patch: Blackjack game with Firebase multiplayer + QR joining (v9.653 → v9.654)"""
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()
orig = src

def replace_once(old, new, label):
    global src
    if old not in src:
        print(f'MISSING: {label}'); sys.exit(1)
    if src.count(old) != 1:
        print(f'AMBIGUOUS ({src.count(old)}x): {label}'); sys.exit(1)
    src = src.replace(old, new, 1)
    print(f'OK: {label}')

# ── 1. GAMES array: add blackjack after busz ──────────────────────────────────
replace_once(
    "{ id:'busz',      roundTime:'slow',  name:'Busz',",
    """{ id:'blackjack', roundTime:'slow',  name:'Blackjack',             difficulty:'közepes', category:'Csapat', emoji:'🂡', symbol:null, img:null, banner:null, color:'#1a6b3c', desc:'Mindenki tét helyez kortykban, majd az osztó lapokat oszt. Célod hogy közelebb legyél 21-hez mint az osztó, anélkül hogy túlmennél. Hit, Stand vagy Double Down! Az osztó 17-nél megáll.' },
  { id:'busz',      roundTime:'slow',  name:'Busz',""",
    "GAMES: blackjack entry"
)

# ── 2. BlackjackGame component (before BuszGame) ──────────────────────────────
replace_once(
    "function BuszGame({ players, roomCode, gameIdx, gameMeta, onAdvance, onSetHideFooter, onSetBuszSwitch }) {",
    r"""function BlackjackGame({ players, roomCode, gameIdx, gameMeta, onAdvance, onSetHideFooter }) {
  // ── Card utilities ──────────────────────────────────────────────────────
  const BJ_SUITS = ['♠','♥','♦','♣'];
  const BJ_RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K'];
  function bjNewDeck() {
    const d = [];
    for (const s of BJ_SUITS) for (const r of BJ_RANKS) d.push(r + s);
    // Fisher-Yates shuffle
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
    for (const c of hand) {
      const r = c.replace(/[♠♥♦♣]/g, '');
      total += bjCardValue(r);
      if (r === 'A') aces++;
    }
    while (total > 21 && aces > 0) { total -= 10; aces--; }
    return total;
  }
  function bjIsBlackjack(hand) { return hand.length === 2 && bjScore(hand) === 21; }
  function bjIsRed(card) { return card.endsWith('♥') || card.endsWith('♦'); }

  // ── State ───────────────────────────────────────────────────────────────
  const isOnline = !!roomCode;
  const [bjState, setBjState] = React.useState(null);
  const [myId, setMyId] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [showQR, setShowQR] = React.useState(false);
  const isHost = players && players.length > 0 && players[0] && bjState?.hostId === players[0].id;

  // Identify this client: host = players[0].id, guest = their player id
  React.useEffect(() => {
    if (players && players.length > 0) setMyId(players[0].id);
  }, []);

  // ── Firebase sync ────────────────────────────────────────────────────────
  React.useEffect(() => {
    if (!isOnline) {
      // offline: auto-init with all players as participants
      initGame(null);
      return;
    }
    const ref = window.db?.collection('rooms').doc(roomCode).collection('gameState').doc('blackjack_' + gameIdx);
    if (!ref) { initGame(null); return; }
    const unsub = ref.onSnapshot(snap => {
      if (snap.exists) {
        setBjState(snap.data());
        setLoading(false);
      } else if (players && players[0]?.id === myId) {
        // host initializes
        initGame(ref);
      } else {
        setLoading(false);
      }
    });
    return () => unsub && unsub();
  }, [roomCode, gameIdx]);

  function initGame(ref) {
    const deck = bjNewDeck();
    const hostPlayer = players[0];
    const participants = players.slice(1); // guests play, host deals
    const hands = {};
    const bets = {};
    for (const p of participants) { hands[p.id] = []; bets[p.id] = 1; }
    const state = {
      phase: 'betting', // betting | dealing | playing | dealer | results
      hostId: hostPlayer?.id || 'host',
      deck,
      dealerHand: [],
      hands,
      bets,
      currentTurn: participants[0]?.id || null,
      participants: participants.map(p => p.id),
      doubled: {},
      stood: {},
      bust: {},
    };
    if (ref) {
      ref.set(state).then(() => { setBjState(state); setLoading(false); });
    } else {
      setBjState(state);
      setLoading(false);
    }
  }

  function updateState(patch) {
    const next = { ...bjState, ...patch };
    setBjState(next);
    if (isOnline && roomCode) {
      const ref = window.db?.collection('rooms').doc(roomCode).collection('gameState').doc('blackjack_' + gameIdx);
      ref?.set(next);
    }
  }

  // ── Game actions ─────────────────────────────────────────────────────────
  function startDealing() {
    const deck = [...bjState.deck];
    const hands = {};
    const dealerHand = [];
    // Deal 2 cards to each participant + 2 to dealer
    for (const pid of bjState.participants) hands[pid] = [];
    for (let i = 0; i < 2; i++) {
      for (const pid of bjState.participants) hands[pid].push(deck.pop());
      dealerHand.push(deck.pop());
    }
    // Check for instant blackjacks — skip those players
    const stood = {};
    for (const pid of bjState.participants) {
      if (bjIsBlackjack(hands[pid])) stood[pid] = true;
    }
    const nextTurn = bjState.participants.find(pid => !stood[pid]) || null;
    updateState({ phase: nextTurn ? 'playing' : 'dealer', deck, hands, dealerHand, stood, doubled: {}, bust: {}, currentTurn: nextTurn });
  }

  function nextPlayerOrDealer(state, stoodUpdate) {
    const stood = { ...state.stood, ...stoodUpdate };
    const remaining = state.participants.filter(pid => !stood[pid] && !state.bust[pid]);
    const cur = state.currentTurn;
    const curIdx = remaining.indexOf(cur);
    const next = remaining.find((pid, i) => i > curIdx) || remaining[0] !== cur && remaining[0] || null;
    if (!next || next === cur) {
      // All done → dealer's turn
      return { ...state, stood, phase: 'dealer', currentTurn: null };
    }
    return { ...state, stood, currentTurn: next };
  }

  function doHit() {
    const deck = [...bjState.deck];
    const card = deck.pop();
    const hand = [...(bjState.hands[myId] || []), card];
    const score = bjScore(hand);
    let patch = { deck, hands: { ...bjState.hands, [myId]: hand } };
    if (score > 21) {
      // bust
      const bust = { ...bjState.bust, [myId]: true };
      const next = nextPlayerOrDealer({ ...bjState, ...patch, bust }, {});
      patch = { ...patch, bust, ...next };
    }
    updateState(patch);
  }

  function doStand() {
    const next = nextPlayerOrDealer(bjState, { [myId]: true });
    updateState(next);
  }

  function doDouble() {
    const deck = [...bjState.deck];
    const card = deck.pop();
    const hand = [...(bjState.hands[myId] || []), card];
    const score = bjScore(hand);
    const bets = { ...bjState.bets, [myId]: (bjState.bets[myId] || 1) * 2 };
    const bust = score > 21 ? { ...bjState.bust, [myId]: true } : bjState.bust;
    const stood = { ...bjState.stood, [myId]: true };
    const doubled = { ...bjState.doubled, [myId]: true };
    const next = nextPlayerOrDealer({ ...bjState, deck, hands: { ...bjState.hands, [myId]: hand }, bets, bust, stood, doubled }, {});
    updateState({ ...next, bets, doubled });
  }

  function setBet(pid, val) {
    updateState({ bets: { ...bjState.bets, [pid]: Math.max(1, Math.min(20, val)) } });
  }

  // ── Host: play dealer hand ───────────────────────────────────────────────
  React.useEffect(() => {
    if (!bjState || bjState.phase !== 'dealer') return;
    if (!isHost && isOnline) return; // only host runs dealer logic
    let deck = [...bjState.deck];
    let dealerHand = [...bjState.dealerHand];
    while (bjScore(dealerHand) < 17) dealerHand.push(deck.pop());
    const timeout = setTimeout(() => {
      updateState({ deck, dealerHand, phase: 'results' });
    }, 1200);
    return () => clearTimeout(timeout);
  }, [bjState?.phase]);

  // ── UI helpers ───────────────────────────────────────────────────────────
  function getPlayer(pid) { return players.find(p => p.id === pid); }
  function CardEl({ card, faceDown }) {
    if (faceDown) return (
      <div style={{ width:44, height:64, borderRadius:8, background:'#1a3a5c', border:'2px solid rgba(255,255,255,0.2)', display:'grid', placeItems:'center', fontSize:24, flexShrink:0 }}>🂠</div>
    );
    const isRed = bjIsRed(card);
    const rank = card.replace(/[♠♥♦♣]/g, '');
    const suit = card.slice(-1);
    return (
      <div style={{ width:44, height:64, borderRadius:8, background:'#fff', border:'2px solid #ddd', display:'flex', flexDirection:'column', padding:'3px 5px', flexShrink:0, userSelect:'none' }}>
        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color: isRed ? '#c02828' : '#111', lineHeight:1 }}>{rank}</span>
        <div style={{ flex:1, display:'grid', placeItems:'center' }}>
          <span style={{ fontSize:20, color: isRed ? '#c02828' : '#111' }}>{suit}</span>
        </div>
      </div>
    );
  }
  function HandRow({ hand, faceDown1, score, label, bet, color, img }) {
    const showScore = hand.length > 0 && !faceDown1;
    return (
      <div style={{ marginBottom:14 }}>
        <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}>
          {img ? (
            <div style={{ width:28, height:28, borderRadius:'50%', background:color||'#333', overflow:'hidden', flexShrink:0 }}>
              <img src={img} style={{ width:28, height:28, objectFit:'cover' }} />
            </div>
          ) : (
            <div style={{ width:28, height:28, borderRadius:'50%', background:color||'#555', display:'grid', placeItems:'center', flexShrink:0 }}>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{(label||'?').charAt(0).toUpperCase()}</span>
            </div>
          )}
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.text }}>{label}</span>
          {bet !== undefined && <span style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginLeft:4 }}>Tét: {bet} korty 🍺</span>}
          {showScore && <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color: bjScore(hand)>21?'#e84040':T.mint, marginLeft:'auto' }}>{bjScore(hand)}{bjIsBlackjack(hand)?' 🂡':''}</span>}
        </div>
        <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
          {hand.map((c, i) => <CardEl key={i} card={c} faceDown={i===0 && faceDown1} />)}
          {hand.length === 0 && <span style={{ fontFamily:T.font, fontSize:13, color:T.sub }}>—</span>}
        </div>
      </div>
    );
  }

  // ── Render results ────────────────────────────────────────────────────────
  function ResultsView() {
    const ds = bjScore(bjState.dealerHand);
    const dealerBJ = bjIsBlackjack(bjState.dealerHand);
    return (
      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.text, marginBottom:12, textAlign:'center' }}>Eredmények</div>
        <HandRow hand={bjState.dealerHand} label="Osztó" color="#555" score={ds} />
        <div style={{ height:1, background:T.border, margin:'12px 0' }} />
        {bjState.participants.map(pid => {
          const p = getPlayer(pid);
          const hand = bjState.hands[pid] || [];
          const ps = bjScore(hand);
          const bust = bjState.bust[pid];
          const pBJ = bjIsBlackjack(hand);
          const bet = bjState.bets[pid] || 1;
          let result, drinks = 0;
          if (bust) { result = 'Bust 💀'; drinks = bet; }
          else if (pBJ && !dealerBJ) { result = 'Blackjack! 🂡'; drinks = 0; }
          else if (dealerBJ && !pBJ) { result = 'Osztó Blackjack'; drinks = bet * 2; }
          else if (ds > 21) { result = 'Osztó bust — nyertél!'; drinks = 0; }
          else if (ps > ds) { result = 'Nyertél! 🏆'; drinks = 0; }
          else if (ps === ds) { result = 'Döntetlen'; drinks = 0; }
          else { result = 'Vesztettél'; drinks = bet; }
          return (
            <div key={pid} style={{ marginBottom:14 }}>
              <HandRow hand={hand} label={p?.name||pid} color={p?.color} img={p?.img} bet={bet} score={ps} />
              <div style={{ display:'flex', alignItems:'center', gap:8, marginLeft:36 }}>
                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color: drinks>0?'#e84040':T.mint }}>{result}</span>
                {drinks > 0 && <span style={{ fontFamily:T.font, fontSize:13, color:T.sub }}>→ {drinks} korty 🍺</span>}
              </div>
            </div>
          );
        })}
        <button onClick={onAdvance} style={{ marginTop:16, width:'100%', padding:'14px', borderRadius:16, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor:'pointer' }}>
          Következő játék →
        </button>
      </div>
    );
  }

  // ── Betting phase ─────────────────────────────────────────────────────────
  function BettingView() {
    return (
      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.text, marginBottom:4, textAlign:'center' }}>Tét beállítása</div>
        <div style={{ fontFamily:T.font, fontSize:13, color:T.sub, marginBottom:16, textAlign:'center' }}>Mennyi kortyt teszel fel?</div>
        {bjState.participants.map(pid => {
          const p = getPlayer(pid);
          const bet = bjState.bets[pid] || 1;
          const canEdit = !isOnline || pid === myId;
          return (
            <div key={pid} style={{ display:'flex', alignItems:'center', gap:12, marginBottom:12, background:T.card, borderRadius:14, padding:'10px 14px' }}>
              {p?.img ? (
                <div style={{ width:32, height:32, borderRadius:'50%', background:p.color, overflow:'hidden', flexShrink:0 }}>
                  <img src={p.img} style={{ width:32, height:32, objectFit:'cover' }} />
                </div>
              ) : (
                <div style={{ width:32, height:32, borderRadius:'50%', background:p?.color||'#555', display:'grid', placeItems:'center', flexShrink:0 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff' }}>{(p?.name||'?').charAt(0).toUpperCase()}</span>
                </div>
              )}
              <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.text, flex:1 }}>{p?.name||pid}</span>
              <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                {canEdit && <button onClick={() => setBet(pid, bet-1)} style={{ width:30, height:30, borderRadius:8, border:'none', background:T.border, fontFamily:T.font, fontWeight:900, fontSize:18, cursor:'pointer', color:T.text }}>−</button>}
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.text, minWidth:28, textAlign:'center' }}>{bet}</span>
                {canEdit && <button onClick={() => setBet(pid, bet+1)} style={{ width:30, height:30, borderRadius:8, border:'none', background:T.border, fontFamily:T.font, fontWeight:900, fontSize:18, cursor:'pointer', color:T.text }}>+</button>}
                <span style={{ fontFamily:T.font, fontSize:13, color:T.sub }}>🍺</span>
              </div>
            </div>
          );
        })}
        {isHost && (
          <button onClick={startDealing} style={{ marginTop:8, width:'100%', padding:'14px', borderRadius:16, background:'#1a6b3c', border:'none', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor:'pointer' }}>
            Lapok osztása 🂡
          </button>
        )}
        {!isHost && isOnline && <div style={{ textAlign:'center', fontFamily:T.font, fontSize:13, color:T.sub, marginTop:8 }}>Várakozás az osztóra…</div>}
      </div>
    );
  }

  // ── Playing phase (per player) ───────────────────────────────────────────
  function PlayingView() {
    const isMyTurn = bjState.currentTurn === myId;
    const myHand = bjState.hands[myId] || [];
    const myScore = bjScore(myHand);
    const canDouble = myHand.length === 2 && !bjState.doubled[myId];
    const dealerVisible = bjState.dealerHand[1]; // second card is face-up, first is hidden
    return (
      <div style={{ padding:'0 16px 16px' }}>
        {/* Dealer row */}
        <div style={{ marginBottom:16 }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.sub, marginBottom:6 }}>Osztó</div>
          <div style={{ display:'flex', gap:6 }}>
            <CardEl card={bjState.dealerHand[0]} faceDown={true} />
            {bjState.dealerHand.slice(1).map((c, i) => <CardEl key={i+1} card={c} />)}
          </div>
        </div>
        <div style={{ height:1, background:T.border, marginBottom:14 }} />
        {/* All players */}
        {bjState.participants.map(pid => {
          const p = getPlayer(pid);
          const hand = bjState.hands[pid] || [];
          const score = bjScore(hand);
          const isTurn = bjState.currentTurn === pid;
          const isStood = bjState.stood[pid];
          const isBust = bjState.bust[pid];
          const isBJ = bjIsBlackjack(hand);
          return (
            <div key={pid} style={{ marginBottom:10, background: isTurn ? T.card : 'transparent', borderRadius:12, padding: isTurn ? '10px 12px' : '4px 0', border: isTurn ? `2px solid ${T.mint}` : '2px solid transparent' }}>
              <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}>
                {p?.img ? (
                  <div style={{ width:26, height:26, borderRadius:'50%', background:p.color, overflow:'hidden', flexShrink:0 }}><img src={p.img} style={{ width:26, height:26, objectFit:'cover' }} /></div>
                ) : (
                  <div style={{ width:26, height:26, borderRadius:'50%', background:p?.color||'#555', display:'grid', placeItems:'center', flexShrink:0 }}>
                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>{(p?.name||'?').charAt(0).toUpperCase()}</span>
                  </div>
                )}
                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.text, flex:1 }}>{p?.name||pid}</span>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color: isBust?'#e84040':isBJ?T.mint:T.text }}>
                  {isBust ? 'Bust 💀' : isBJ ? 'BJ! 🂡' : isStood ? `${score} (megáll)` : score}
                </span>
              </div>
              <div style={{ display:'flex', gap:5, flexWrap:'wrap' }}>
                {hand.map((c, i) => <CardEl key={i} card={c} />)}
              </div>
              {isTurn && isMyTurn && (
                <div style={{ display:'flex', gap:8, marginTop:10 }}>
                  <button onClick={doHit} style={{ flex:1, padding:'10px', borderRadius:12, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Hit</button>
                  <button onClick={doStand} style={{ flex:1, padding:'10px', borderRadius:12, background:'#555', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Stand</button>
                  {canDouble && <button onClick={doDouble} style={{ flex:1, padding:'10px', borderRadius:12, background:'#c07a10', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Double</button>}
                </div>
              )}
              {isTurn && !isMyTurn && isOnline && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:6, textAlign:'center' }}>A te köröd…</div>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  // ── Hide footer while playing ─────────────────────────────────────────────
  React.useEffect(() => { onSetHideFooter && onSetHideFooter(true); }, []);
  React.useEffect(() => () => { onSetHideFooter && onSetHideFooter(false); }, []);

  if (loading) return (
    <div style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center' }}>
      <span style={{ fontFamily:T.font, fontSize:16, color:T.sub }}>Betöltés…</span>
    </div>
  );

  const roomUrl = roomCode ? (window.location.origin + window.location.pathname + '?room=' + roomCode) : null;

  return (
    <div style={{ flex:1, overflowY:'auto', paddingTop:8 }}>
      {/* QR join button — host only */}
      {isHost && roomUrl && (
        <div style={{ display:'flex', justifyContent:'center', marginBottom:8 }}>
          <button onClick={() => setShowQR(true)} style={{ background:'transparent', border:`1.5px solid ${T.border}`, borderRadius:20, padding:'6px 16px', fontFamily:T.font, fontSize:13, color:T.sub, cursor:'pointer', display:'flex', alignItems:'center', gap:6 }}>
            <span>📱</span> QR kód — csatlakozás
          </button>
        </div>
      )}
      {showQR && roomUrl && (
        <QRModal url={roomUrl} onClose={() => setShowQR(false)} />
      )}

      {bjState?.phase === 'betting' && <BettingView />}
      {(bjState?.phase === 'playing' || bjState?.phase === 'dealer') && <PlayingView />}
      {bjState?.phase === 'results' && <ResultsView />}
    </div>
  );
}

function BuszGame({ players, roomCode, gameIdx, gameMeta, onAdvance, onSetHideFooter, onSetBuszSwitch }) {""",
    "BlackjackGame component"
)

# ── 3. Game routing: add blackjack before busz ────────────────────────────────
replace_once(
    "  if (gameId === 'busz') return <BuszGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={roomCode} gameMeta={gameMeta} onAdvance={onAdvance} onSetHideFooter={onSetHideFooter} onSetBuszSwitch={onSetBuszSwitch} />;",
    """  if (gameId === 'blackjack') return <BlackjackGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={roomCode} gameMeta={gameMeta} onAdvance={onAdvance} onSetHideFooter={onSetHideFooter} />;
  if (gameId === 'busz') return <BuszGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={roomCode} gameMeta={gameMeta} onAdvance={onAdvance} onSetHideFooter={onSetHideFooter} onSetBuszSwitch={onSetBuszSwitch} />;""",
    "game routing: blackjack"
)

# ── Version bump ──────────────────────────────────────────────────────────────
replace_once(
    "const APP_VERSION = 'v9.653';",
    "const APP_VERSION = 'v9.654';",
    "version bump 9.653 → 9.654"
)

assert src != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print("\nAll patches applied.")
