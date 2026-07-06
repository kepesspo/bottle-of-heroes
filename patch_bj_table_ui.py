#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v9.809 — Blackjack table UI: green felt design, labeled seats, OSZTÓ naming.
# UI-only redesign of playing/dealer/results phases (host + observer). No logic/state changes.
import io

P = 'index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global c
    assert old in c, 'MISSING OLD: ' + old[:90]
    assert c.count(old) == count, 'COUNT %d != %d: %s' % (c.count(old), count, old[:90])
    c = c.replace(old, new)

def rep_block(start_marker, end_marker, new_block):
    """Replace text from start_marker (inclusive) up to end_marker (exclusive)."""
    global c
    assert start_marker in c and c.count(start_marker) == 1, 'BLOCK START: ' + start_marker[:80]
    i = c.index(start_marker)
    j = c.index(end_marker, i + len(start_marker))
    c = c[:i] + new_block + c[j:]

# ── 1) BJCardEl: new `big` prop ──
rep("function BJCardEl({ card, faceDown, small, animate }) {\n  const W = small ? 36 : 48, H = small ? 52 : 70;",
    "function BJCardEl({ card, faceDown, small, big, animate }) {\n  const W = big ? 56 : small ? 36 : 48, H = big ? 80 : small ? 52 : 70;")
rep("fontSize:small?18:24", "fontSize:big?28:small?18:24")
rep("fontSize:small?13:15", "fontSize:big?18:small?13:15")
rep("fontSize:small?16:20", "fontSize:big?24:small?16:20")

# ── 2) OSZTÓ naming (blackjack-only strings) ──
rep("return { label:'Gép Blackjack 🤖', delta: -bet };",
    "return { label:'Osztó Blackjack 🎩', delta: -bet };")
rep("return { label:'A gép besokallt — nyert! 🏆', delta: bet };",
    "return { label:'Az osztó besokallt — nyert! 🏆', delta: bet };")
rep("A játékosok a telefonjukon csatlakoznak — mindenki a gép ellen játszik!",
    "A játékosok a telefonjukon csatlakoznak — mindenki az osztó (a ház) ellen játszik!")
rep("// ═══════════════ BLACKJACK — host nézet (a gép oszt) ═══════════════",
    "// ═══════════════ BLACKJACK — host nézet (az osztó oszt) ═══════════════")
rep("// Offline: mindenki a host telefonján játszik, a gép oszt",
    "// Offline: mindenki a host telefonján játszik, az osztó oszt")

# ── 3) HOST PlayingView — green felt table ──
NEW_PLAYING = """  // ── Játék fázis (zöld filc asztal) ──
  const PlayingView = () => {
    const revealed = bjState.phase === 'dealer' || bjState.phase === 'results';
    const curPid = bjState.phase === 'playing' ? bjState.currentTurn : null;
    const curP = curPid ? getPlayer(curPid) : null;
    const curHand = curPid ? (bjState.hands[curPid] || []) : [];
    const canDouble = curPid && curHand.length === 2 && !bjState.doubled[curPid];
    return (
      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ background:'radial-gradient(ellipse at 50% 0%, rgba(255,255,255,0.10), rgba(255,255,255,0) 60%), #1E6E44', border:'6px solid #175636', borderRadius:'150px 150px 22px 22px', padding:'26px 12px 18px', boxShadow:'inset 0 2px 12px rgba(0,0,0,0.25)' }}>
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:8, marginBottom:16 }}>
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', letterSpacing:'0.12em', textTransform:'uppercase' }}>🎩 OSZTÓ</span>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', background:'#0e3d26', borderRadius:999, padding:'3px 10px' }}>{revealed ? bjScore(bjState.dealerHand) : '?'}</span>
            </div>
            <div style={{ display:'flex', gap:6, flexWrap:'wrap', justifyContent:'center' }}>
              {(bjState.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} faceDown={i === 1 && !revealed} animate={i >= 1 && revealed} />)}
            </div>
          </div>
          <div style={{ display:'flex', flexWrap:'wrap', justifyContent:'center', gap:10 }}>
            {(bjState.participants || []).map(pid => {
              const p = getPlayer(pid);
              const hand = bjState.hands[pid] || [];
              const score = bjScore(hand);
              const isTurn = bjState.currentTurn === pid && bjState.phase === 'playing';
              const isStood = bjState.stood[pid];
              const isBust = bjState.bust[pid];
              const isBJ = bjIsBlackjack(hand);
              const rowChips = (bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid);
              const status = isBust ? { t:`💀 ${score}`, c:'#FF9C86' } : isBJ ? { t:'BJ! 🂡', c:'#7CF0BF' } : isTurn ? { t:'⏳ GONDOLKODIK…', c:'#F4D46B' } : isStood ? { t:`✋ ${score}`, c:'#F4D46B' } : { t:String(score), c:'#F4D46B' };
              const lblS = { fontFamily:T.font, fontSize:8, fontWeight:800, letterSpacing:'0.08em', textTransform:'uppercase', color:'rgba(255,255,255,0.7)', marginTop:2 };
              return (
                <div key={pid} style={{ width:106, display:'flex', flexDirection:'column', alignItems:'center', gap:5, background:'rgba(255,255,255,0.08)', border:`1.5px solid ${isTurn ? '#F4D46B' : 'rgba(255,255,255,0.18)'}`, borderRadius:14, padding:'10px 6px 8px', boxShadow: isTurn ? '0 0 0 2px #F4D46B66' : 'none' }}>
                  <BJAvatar p={p} size={30} />
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', maxWidth:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p?.name || pid}</span>
                  <div style={{ display:'flex', gap:3, flexWrap:'wrap', justifyContent:'center', minHeight:52 }}>
                    {hand.map((c, i) => <BJCardEl key={i} card={c} small />)}
                  </div>
                  <div style={{ display:'flex', alignItems:'flex-start', gap:10 }}>
                    <div style={{ display:'flex', flexDirection:'column', alignItems:'center' }}>
                      <span style={{ width:26, height:26, borderRadius:'50%', background:T.coral, border:'1.5px dashed rgba(255,255,255,0.9)', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', boxSizing:'border-box' }}>{bjState.bets[pid] || 1}</span>
                      <span style={lblS}>TÉT</span>
                    </div>
                    <div style={{ display:'flex', flexDirection:'column', alignItems:'center' }}>
                      <span style={{ display:'inline-flex', alignItems:'center', gap:3, height:26 }}><BJChipStack count={rowChips} size={20} hideCount /><span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>{rowChips}</span></span>
                      <span style={lblS}>KÉSZLET</span>
                    </div>
                  </div>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9.5, color:status.c, letterSpacing:'0.04em' }}>{status.t}</span>
                </div>
              );
            })}
          </div>
        </div>
        {bjState.phase === 'playing' && curPid && (
          <div style={{ marginTop:12 }}>
            <div style={{ fontFamily:T.font, fontSize:12, fontWeight:T.weightTitle, color:T.inkSoft, textAlign:'center', marginBottom:8 }}>{curP?.name || '?'} jön</div>
            <div style={{ display:'flex', gap:8 }}>
              <button onClick={() => update(bjDoHit(bjState, curPid))} style={{ flex:1, padding:'10px', borderRadius:12, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Hit 🃏</button>
              <button onClick={() => update(bjDoStand(bjState, curPid))} style={{ flex:1, padding:'10px', borderRadius:12, background:'#555', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Stand ✋</button>
              {canDouble && <button onClick={() => update(bjDoDouble(bjState, curPid))} style={{ flex:1, padding:'10px', borderRadius:12, background:'#c07a10', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Double 2×</button>}
            </div>
            {isOnline && (
              <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:6, textAlign:'center' }}>📱 A telefonján is léphet — vagy üsd le itt helyette</div>
            )}
          </div>
        )}
        {bjState.phase === 'dealer' && (
          <div style={{ textAlign:'center', fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color:T.inkSoft, marginTop:12 }}>Az osztó húz… 🎩</div>
        )}
      </div>
    );
  };

"""
rep_block("  // ── Játék fázis (asztal nézet) ──", "  // ── Eredmények ──", NEW_PLAYING)

# ── 4) HOST ResultsView — felt + result seats, compact controls below ──
NEW_RESULTS = """  // ── Eredmények ──
  const ResultsView = () => {
    const ds = bjScore(bjState.dealerHand);
    return (
      <div style={{ padding:'0 16px 16px' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginBottom:12, textAlign:'center' }}>Eredmények</div>
        <div style={{ background:'radial-gradient(ellipse at 50% 0%, rgba(255,255,255,0.10), rgba(255,255,255,0) 60%), #1E6E44', border:'6px solid #175636', borderRadius:'150px 150px 22px 22px', padding:'26px 12px 18px', boxShadow:'inset 0 2px 12px rgba(0,0,0,0.25)', marginBottom:14 }}>
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:8, marginBottom:16 }}>
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', letterSpacing:'0.12em', textTransform:'uppercase' }}>🎩 OSZTÓ</span>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', background:'#0e3d26', borderRadius:999, padding:'3px 10px' }}>{ds}{ds > 21 ? ' 💀' : ''}{bjIsBlackjack(bjState.dealerHand) ? ' 🂡' : ''}</span>
            </div>
            <div style={{ display:'flex', gap:6, flexWrap:'wrap', justifyContent:'center' }}>
              {(bjState.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} small animate={i >= 1} />)}
            </div>
          </div>
          <div style={{ display:'flex', flexWrap:'wrap', justifyContent:'center', gap:10 }}>
            {(bjState.participants || []).map(pid => {
              const p = getPlayer(pid);
              const hand = bjState.hands[pid] || [];
              const res = bjResultFor(bjState, pid);
              const rowChips = (bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid);
              const out = !!(bjState.cashedOut || {})[pid];
              const status = res.delta > 0 ? { t:`+${res.delta} 🍺`, c:'#7CF0BF' } : res.delta < 0 ? { t:`−${-res.delta} 🍺`, c:'#FF9C86' } : { t:'=', c:'#F4D46B' };
              const lblS = { fontFamily:T.font, fontSize:8, fontWeight:800, letterSpacing:'0.08em', textTransform:'uppercase', color:'rgba(255,255,255,0.7)', marginTop:2 };
              return (
                <div key={pid} style={{ width:106, display:'flex', flexDirection:'column', alignItems:'center', gap:5, background:'rgba(255,255,255,0.08)', border:'1.5px solid rgba(255,255,255,0.18)', borderRadius:14, padding:'10px 6px 8px', opacity: out ? 0.6 : 1 }}>
                  <BJAvatar p={p} size={30} />
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', maxWidth:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p?.name || pid}{out ? ' 🚪' : ''}</span>
                  <div style={{ display:'flex', gap:3, flexWrap:'wrap', justifyContent:'center', minHeight:52 }}>
                    {hand.map((c, i) => <BJCardEl key={i} card={c} small />)}
                  </div>
                  <div style={{ display:'flex', alignItems:'flex-start', gap:10 }}>
                    <div style={{ display:'flex', flexDirection:'column', alignItems:'center' }}>
                      <span style={{ width:26, height:26, borderRadius:'50%', background:T.coral, border:'1.5px dashed rgba(255,255,255,0.9)', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', boxSizing:'border-box' }}>{bjState.bets[pid] || 1}</span>
                      <span style={lblS}>TÉT</span>
                    </div>
                    <div style={{ display:'flex', flexDirection:'column', alignItems:'center' }}>
                      <span style={{ display:'inline-flex', alignItems:'center', gap:3, height:26 }}><BJChipStack count={rowChips} size={20} hideCount /><span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>{rowChips}</span></span>
                      <span style={lblS}>KÉSZLET</span>
                    </div>
                  </div>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9.5, color:status.c, letterSpacing:'0.04em' }}>{status.t}</span>
                </div>
              );
            })}
          </div>
        </div>
        {(bjState.participants || []).map(pid => {
          const p = getPlayer(pid);
          const startStack = stackOf(pid);
          const chips = (bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : startStack;
          const out = !!(bjState.cashedOut || {})[pid];
          const broke = !out && chips === 0;
          const diff = chips - startStack;
          if (broke) return (
            <div key={pid} style={{ marginBottom:8, padding:'10px 12px', borderRadius:12, background:T.coralSoft }}>
              <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                <BJAvatar p={p} size={24} />
                <span style={{ fontFamily:T.font, fontSize:12.5, fontWeight:900, color:T.coral }}>💀 {p?.name || pid} — elfogyott a készlete, igyon {startStack} kortyot!</span>
              </div>
              {!isOnline && hostRebuyPick !== pid && (
                <div style={{ display:'flex', gap:8, marginTop:8 }}>
                  <button onClick={() => setHostRebuyPick(pid)} style={{ flex:1, padding:'9px', borderRadius:10, border:'none', background:T.mint, fontFamily:T.font, fontWeight:800, fontSize:12, color:'#fff', cursor:'pointer' }}>🔄 Megitta — újra beszáll</button>
                  <button onClick={() => update({ ...bjState, cashedOut: { ...(bjState.cashedOut || {}), [pid]: true }, brokeDrank: { ...(bjState.brokeDrank || {}), [pid]: true } })} style={{ flex:1, padding:'9px', borderRadius:10, border:'none', background:'#555', fontFamily:T.font, fontWeight:800, fontSize:12, color:'#fff', cursor:'pointer' }}>🚪 Megitta — kiszáll</button>
                </div>
              )}
              {!isOnline && hostRebuyPick === pid && (
                <BJStackPicker onConfirm={v => { hostRebuy(pid, true, v); setHostRebuyPick(null); }} onCancel={() => setHostRebuyPick(null)} />
              )}
            </div>
          );
          if (!out && !isOnline) return (
            <div key={pid} style={{ display:'flex', alignItems:'center', gap:8, marginBottom:8 }}>
              <BJAvatar p={p} size={24} />
              <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.ink, flexShrink:0 }}>{p?.name || pid}</span>
              <button onClick={() => hostCashOut(pid)} style={{ flex:1, minWidth:0, padding:'7px 8px', borderRadius:10, border:`1.5px solid ${T.surfaceMuted}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft, cursor:'pointer' }}>
                🚪 Kiszáll {diff < 0 ? `— iszik ${-diff} kortyot` : diff > 0 ? `— kioszt ${diff} kortyot` : '— nullán van'}
              </button>
            </div>
          );
          if (out) return (
            <div key={pid} style={{ display:'flex', alignItems:'center', gap:8, marginBottom:8, opacity:0.6 }}>
              <BJAvatar p={p} size={24} />
              <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.inkSoft }}>{p?.name || pid} · kiszállt 🚪</span>
            </div>
          );
          return null;
        })}
        <button onClick={hostNewRound} style={{ width:'100%', padding:'14px', borderRadius:16, background:'#1a6b3c', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer', marginTop:14 }}>Új kör 🔄</button>
      </div>
    );
  };

"""
rep_block("  // ── Eredmények ──", "  return (\n    <div style={{ flex:1, overflowY:'auto', paddingTop:8 }}>", NEW_RESULTS)

# ── 5) OBSERVER — mini felt table (dealer + others) replaces Osztó block ──
NEW_MINI_TABLE = """            {/* Mini asztal — osztó + többiek */}
            <div style={{ background:'radial-gradient(ellipse at 50% 0%, rgba(255,255,255,0.10), rgba(255,255,255,0) 60%), #1E6E44', border:'4px solid #175636', borderRadius:'90px 90px 18px 18px', padding:'18px 10px 12px', marginBottom:12 }}>
              <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:6, marginBottom:10 }}>
                <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', letterSpacing:'0.12em', textTransform:'uppercase' }}>🎩 OSZTÓ</span>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', background:'#0e3d26', borderRadius:999, padding:'2px 9px' }}>{revealed ? `${bjScore(bj.dealerHand)}${bjScore(bj.dealerHand) > 21 ? ' 💀' : ''}` : '?'}</span>
                </div>
                <div style={{ display:'flex', gap:5, flexWrap:'wrap', justifyContent:'center' }}>
                  {(bj.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} faceDown={i === 1 && !revealed} small animate={i >= 1 && revealed} />)}
                </div>
              </div>
              <div style={{ display:'flex', flexWrap:'wrap', justifyContent:'center', gap:8 }}>
                {(bj.participants || []).filter(pid => pid !== playerId).map(pid => {
                  const p = players.find(pp => pp.id === pid);
                  const hand = (bj.hands || {})[pid] || [];
                  const score = bjScore(hand);
                  const isTurn = bj.phase === 'playing' && bj.currentTurn === pid;
                  const status = bj.phase === 'results'
                    ? { t:`Lapok: ${bj.bust[pid] ? '💀' : bjIsBlackjack(hand) ? 'BJ 🂡' : score} · Zseton: ${(bj.chips || {})[pid] !== undefined ? bj.chips[pid] : stackOf(pid)} 🍺`, c:'#fff' }
                    : bj.bust[pid] ? { t:'💀', c:'#FF9C86' }
                    : bjIsBlackjack(hand) ? { t:'BJ! 🂡', c:'#7CF0BF' }
                    : bj.stood[pid] ? { t:`${score} ✋`, c:'#F4D46B' }
                    : { t:`${hand.length} LAP`, c:'#F4D46B' };
                  return (
                    <div key={pid} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:3, background:'rgba(255,255,255,0.08)', border:`1.5px solid ${isTurn ? '#F4D46B' : 'rgba(255,255,255,0.18)'}`, borderRadius:12, padding:'7px 8px', minWidth:66, maxWidth:140, boxShadow: isTurn ? '0 0 0 2px #F4D46B66' : 'none' }}>
                      <BJAvatar p={p} size={24} />
                      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', maxWidth:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p?.name || pid}</span>
                      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, color:status.c, letterSpacing:'0.04em', textAlign:'center' }}>{status.t}</span>
                    </div>
                  );
                })}
                {(bj.participants || []).filter(pid => pid !== playerId).length === 0 && (
                  <div style={{ fontFamily:T.font, fontSize:11, color:'rgba(255,255,255,0.75)', textAlign:'center', padding:'2px 0' }}>Egyedül játszol az osztó ellen</div>
                )}
              </div>
            </div>

"""
rep_block("            {/* Osztó */}", "            {/* Saját kéz */}", NEW_MINI_TABLE)

# ── 6) OBSERVER — own hand: TE JÖSSZ tag + big cards ──
rep("<span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em' }}>A lapjaid</span>",
    "<span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em' }}>A lapjaid</span>\n                {isMyTurn && <span style={{ marginLeft:8, fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff', background:T.mint, borderRadius:999, padding:'3px 8px', letterSpacing:'0.06em' }}>TE JÖSSZ!</span>}")
rep("{myHand.map((c, i) => <BJCardEl key={i} card={c} />)}",
    "{myHand.map((c, i) => <BJCardEl key={i} card={c} big />)}")

# ── 7) OBSERVER — remove old \"Többiek\" list (moved into mini felt) ──
rep_block("            {/* Többiek */}", "            {/* Kapott kortyok log */}", "")

# ── 8) Version bump ──
assert c.count("'v9.808'") == 1
rep("const APP_VERSION = 'v9.808';", "const APP_VERSION = 'v9.809';")

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
