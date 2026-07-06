#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v9.792 — Busz host-mode fixes:
# 1) unseen-sip badge on the PlayScreen busz switch button
# 2) back-to-host button on the "not riding the bus" screen
# 3) back-to-host button in bus intro + bus riding view
# 4) closable "busz kész" done screen (host: back, guest: dismiss)
# 5) giver name stored in drink event + recipient toast + feed line
# 6) batched sip distribution (single Firestore write on Kész)

import io

PATH = '/home/user/bottle-of-heroes/index.html'
with io.open(PATH, 'r', encoding='utf-8') as f:
    c = f.read()

def rep(old, new, count=1):
    global c
    assert old in c, 'OLD not found: ' + old[:120]
    assert c.count(old) == count, 'OLD not unique (%d): %s' % (c.count(old), old[:120])
    c = c.replace(old, new, count)

# ── Version bump ────────────────────────────────────────────────────────────
rep("const APP_VERSION = 'v9.791';", "const APP_VERSION = 'v9.792';")

# ── 1a) BuszGame: unseen-sip counter + register {fn, badge} object ──────────
OLD = """  const canShowSwitch = !!(hostPlaysEnabled && hostPlayerId);
  React.useEffect(() => { onSetBuszSwitch && onSetBuszSwitch(canShowSwitch ? (() => setHostViewMode('player')) : null); }, [canShowSwitch]);"""
NEW = """  const canShowSwitch = !!(hostPlaysEnabled && hostPlayerId);
  // Unseen sips: count sips the host-player receives while on the host (pyramid) screen
  const [unseenSips, setUnseenSips] = useState(0);
  const hostDrinksNow = hostPlayerId ? ((players.find(p => p.id === hostPlayerId)?.drinks) || 0) : 0;
  const prevHostDrinksRef = React.useRef(null);
  const hostViewModeRef = React.useRef(hostViewMode);
  React.useEffect(() => { hostViewModeRef.current = hostViewMode; }, [hostViewMode]);
  React.useEffect(() => {
    if (!hostPlayerId) { prevHostDrinksRef.current = null; return; }
    if (prevHostDrinksRef.current === null) { prevHostDrinksRef.current = hostDrinksNow; return; }
    const diff = hostDrinksNow - prevHostDrinksRef.current;
    prevHostDrinksRef.current = hostDrinksNow;
    if (diff > 0 && hostViewModeRef.current === 'host') setUnseenSips(n => n + diff);
  }, [hostDrinksNow, hostPlayerId]);
  React.useEffect(() => { onSetBuszSwitch && onSetBuszSwitch(canShowSwitch ? { fn: () => { setUnseenSips(0); setHostViewMode('player'); }, badge: unseenSips } : null); }, [canShowSwitch, unseenSips]);"""
rep(OLD, NEW)

# ── 1b) PlayScreen: accept object registration ──────────────────────────────
rep("onSetBuszSwitch={(fn) => setBuszSwitchFn(fn ? () => fn : null)}",
    "onSetBuszSwitch={(obj) => setBuszSwitchFn(obj || null)}")

# ── 1c) PlayScreen: render badge on the switch button ───────────────────────
OLD = """              <div style={{ width:54, height:54, flexShrink:0, display:'grid', placeItems:'center' }}>
                <button onClick={buszSwitchFn} style={{ width:44, height:44, borderRadius:'50%', background:T.surface, border:'none', boxShadow:'0 2px 10px rgba(0,0,0,0.12)', cursor:'pointer', display:'grid', placeItems:'center', padding:0, fontSize:20 }}>\U0001F3AE</button>
              </div>"""
NEW = """              <div style={{ width:54, height:54, flexShrink:0, display:'grid', placeItems:'center', position:'relative' }}>
                <button onClick={buszSwitchFn.fn} style={{ width:44, height:44, borderRadius:'50%', background:T.surface, border:'none', boxShadow:'0 2px 10px rgba(0,0,0,0.12)', cursor:'pointer', display:'grid', placeItems:'center', padding:0, fontSize:20 }}>\U0001F3AE</button>
                {buszSwitchFn.badge > 0 && (
                  <div style={{ position:'absolute', top:0, right:0, minWidth:18, height:18, borderRadius:999, background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:11, display:'grid', placeItems:'center', padding:'0 5px', boxSizing:'border-box', boxShadow:'0 1px 4px rgba(0,0,0,0.25)', pointerEvents:'none' }}>{buszSwitchFn.badge}</div>
                )}
              </div>"""
rep(OLD, NEW)

# ── 5a) BuszPlayerView: gift-notice state + done-dismiss state + effect ─────
OLD = """  const busResultTimerRef = React.useRef(null);
  const playerIdRef = React.useRef(playerId);
  React.useEffect(() => { playerIdRef.current = playerId; }, [playerId]);"""
NEW = """  const busResultTimerRef = React.useRef(null);
  const playerIdRef = React.useRef(playerId);
  React.useEffect(() => { playerIdRef.current = playerId; }, [playerId]);
  const [giftNotice, setGiftNotice] = useState(null); // { name, n, ts } — who gave me sips
  const [doneDismissed, setDoneDismissed] = useState(false);
  const lastGiftTsRef = React.useRef(undefined);
  React.useEffect(() => {
    const lg = buszState && buszState.lastGift;
    if (lastGiftTsRef.current === undefined) { lastGiftTsRef.current = lg ? lg.ts : null; return; }
    if (!lg || lg.ts === lastGiftTsRef.current) return;
    lastGiftTsRef.current = lg.ts;
    if (!playerId) return;
    const n = (lg.assigned||{})[playerId] || 0;
    if (n > 0 && lg.giverId !== playerId) {
      const ts = lg.ts;
      setGiftNotice({ name: lg.giverName || '?', n, ts });
      setTimeout(() => setGiftNotice(cur => (cur && cur.ts === ts) ? null : cur), 4500);
    }
  }, [buszState && buszState.lastGift && buszState.lastGift.ts, playerId]);"""
rep(OLD, NEW)

# ── 4) Done screen: closable (host: back, guest: dismiss) ───────────────────
OLD = """  if (buszState.phase === 'done' && !busGuessResult) {
    return (
      <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg }}>
        <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:14, padding:24 }}>
          <div style={{ fontSize:52 }}>\U0001F389</div>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.mint, textTransform:'uppercase', letterSpacing:T.letterDisplay }}>{t('busDone')}</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>A buszjárat véget ért!</div>
        </div>
      </div>
    );
  }"""
NEW = """  if (buszState.phase === 'done' && !busGuessResult) {
    if (doneDismissed && !onSwitchToHost) return (
      <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:14, padding:24, background:T.bg }}>
        <div style={{ width:54, height:54, borderRadius:'50%', background:player?.color||T.mint, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:22, color:'#fff', overflow:'hidden' }}>{player?.img ? <img src={player.img} style={{width:54,height:54,objectFit:'cover'}} /> : (player?.name||'?').charAt(0).toUpperCase()}</div>
        <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center' }}>Várakozás a következő játékra…</div>
        <div style={{ display:'flex', gap:6 }}>{[0,1,2].map(i=><span key={i} style={{ width:8, height:8, borderRadius:'50%', background:T.mint, animation:`dotBounce 1.2s ${i*0.15}s infinite ease-in-out` }}/>)}</div>
      </div>
    );
    return (
      <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg }}>
        <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:14, padding:24 }}>
          <div style={{ fontSize:52 }}>\U0001F389</div>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.mint, textTransform:'uppercase', letterSpacing:T.letterDisplay }}>{t('busDone')}</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>A buszjárat véget ért!</div>
          <button onClick={onSwitchToHost ? onSwitchToHost : () => setDoneDismissed(true)} style={{ marginTop:8, padding:'13px 26px', borderRadius:999, border:'none', background:T.surface, color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, cursor:'pointer', boxShadow:T.shadow }}>{onSwitchToHost ? '← Vissza a host nézethez' : 'Bezárás'}</button>
        </div>
      </div>
    );
  }"""
rep(OLD, NEW)

# ── 2) Not-riding screen: back-to-host button ───────────────────────────────
OLD = """          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center', lineHeight:1.6, maxWidth:260 }}>{nm.sub}</div>
        </div>
      );
    }"""
NEW = """          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center', lineHeight:1.6, maxWidth:260 }}>{nm.sub}</div>
          {onSwitchToHost && (
            <button onClick={onSwitchToHost} style={{ marginTop:8, padding:'13px 26px', borderRadius:999, border:'none', background:T.surface, color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, cursor:'pointer', boxShadow:T.shadow }}>← Vissza a host nézethez</button>
          )}
        </div>
      );
    }"""
rep(OLD, NEW)

# ── 3a) Bus intro screen: back-to-host button ───────────────────────────────
OLD = """          <PrimaryButton tone="coral" onClick={()=>{ setBusIntroShown(true); onBusIntroShown && onBusIntroShown(); }}>Kezdjük! \U0001F68C</PrimaryButton>
        </div>"""
NEW = """          <PrimaryButton tone="coral" onClick={()=>{ setBusIntroShown(true); onBusIntroShown && onBusIntroShown(); }}>Kezdjük! \U0001F68C</PrimaryButton>
          {onSwitchToHost && (
            <button onClick={onSwitchToHost} style={{ background:'transparent', border:'none', color:T.inkSoft, fontFamily:T.font, fontWeight:700, fontSize:13, cursor:'pointer', padding:'4px 0' }}>← Vissza a host nézethez</button>
          )}
        </div>"""
rep(OLD, NEW)

# ── 3b) Bus riding view header: switch-to-host button ───────────────────────
OLD = """          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:8 }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:canGuess?T.mint:myPendingGuess?T.ink:T.inkSoft, letterSpacing:T.letterDisplay, textTransform:'uppercase', lineHeight:1.1 }}>"""
NEW = """          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:8 }}>
            {onSwitchToHost && (
              <button onClick={onSwitchToHost} style={{ width:36, height:36, borderRadius:'50%', background:T.surface, border:'none', cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0, fontSize:18, boxShadow:T.shadow }}>\U0001F3AE</button>
            )}
            <div style={{ flex:1, fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:canGuess?T.mint:myPendingGuess?T.ink:T.inkSoft, letterSpacing:T.letterDisplay, textTransform:'uppercase', lineHeight:1.1 }}>"""
rep(OLD, NEW)

# ── 6a) Batched distribution: local-only +/- and single-write commit ────────
OLD = """  const giveOneDrink = async (targetId) => {
    if (!giftTarget || giftTarget.pool <= 0) return;
    if (typeof window.triggerHaptic === 'function') window.triggerHaptic();
    setGiftTarget(g => ({...g, pool:g.pool-1, assigned:{...g.assigned, [targetId]:(g.assigned[targetId]||0)+1}}));
    try {
      const db = firebase.firestore();
      const ref = db.collection('rooms').doc(roomCode);
      await db.runTransaction(async t => {
        const snap = await t.get(ref);
        const ps = snap.data()?.players || [];
        t.update(ref, { players: ps.map(p => p.id===targetId ? {...p, drinks:(p.drinks||0)+1} : p) });
      });
    } catch(e) { console.error('giveOneDrink', e); }
  };

  const takeOneDrink = async (targetId) => {
    if (!giftTarget || (giftTarget.assigned[targetId]||0) <= 0) return;
    setGiftTarget(g => ({...g, pool:g.pool+1, assigned:{...g.assigned, [targetId]:g.assigned[targetId]-1}}));
    try {
      const db = firebase.firestore();
      const ref = db.collection('rooms').doc(roomCode);
      await db.runTransaction(async t => {
        const snap = await t.get(ref);
        const ps = snap.data()?.players || [];
        t.update(ref, { players: ps.map(p => p.id===targetId ? {...p, drinks:Math.max(0,(p.drinks||0)-1)} : p) });
      });
    } catch(e) { console.error('takeOneDrink', e); }
  };"""
NEW = """  const giveOneDrink = (targetId) => {
    if (!giftTarget || giftTarget.pool <= 0) return;
    if (typeof window.triggerHaptic === 'function') window.triggerHaptic();
    setGiftTarget(g => ({...g, pool:g.pool-1, assigned:{...g.assigned, [targetId]:(g.assigned[targetId]||0)+1}}));
  };

  const takeOneDrink = (targetId) => {
    if (!giftTarget || (giftTarget.assigned[targetId]||0) <= 0) return;
    setGiftTarget(g => ({...g, pool:g.pool+1, assigned:{...g.assigned, [targetId]:g.assigned[targetId]-1}}));
  };

  // Commit all locally assigned sips in ONE Firestore write, with giver info
  const commitGift = async () => {
    if (!giftTarget || giftTarget.pool > 0) return;
    const assigned = {...(giftTarget.assigned||{})};
    setGiftTarget(null);
    const total = Object.values(assigned).reduce((s,n)=>s+(n||0),0);
    if (total <= 0) return;
    try {
      const db = firebase.firestore();
      const ref = db.collection('rooms').doc(roomCode);
      await db.runTransaction(async tr => {
        const snap = await tr.get(ref);
        const ps = snap.data()?.players || [];
        tr.update(ref, {
          players: ps.map(p => (assigned[p.id]||0) > 0 ? {...p, drinks:(p.drinks||0)+assigned[p.id]} : p),
          'buszState.lastGift': { giverId: playerId, giverName: player?.name || '?', assigned, ts: Date.now() },
        });
      });
    } catch(e) { console.error('commitGift', e); }
  };"""
rep(OLD, NEW)

# ── 6b) Kész button commits the batch ───────────────────────────────────────
rep("onClick={()=>{ if(giftTarget.pool>0) return; setGiftTarget(null); }}",
    "onClick={()=>{ if(giftTarget.pool>0) return; commitGift(); }}")

# ── 5b) Recipient toast in the hand view ────────────────────────────────────
OLD = """  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden', background:T.bg }}>
      {/* ── Scrollable content ── */}
      <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'12px 14px 8px', display:'flex', flexDirection:'column', gap:10 }}>"""
NEW = """  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden', background:T.bg }}>
      {/* Gift notice toast — who gave me sips */}
      {giftNotice && (
        <div style={{ position:'fixed', top:'max(14px, env(safe-area-inset-top))', left:'50%', transform:'translateX(-50%)', zIndex:120, background:T.coral, color:'#fff', borderRadius:999, padding:'10px 18px', fontFamily:T.font, fontWeight:700, fontSize:14, boxShadow:'0 6px 20px rgba(0,0,0,0.3)', animation:'popIn .25s', whiteSpace:'nowrap' }}>
          {giftNotice.name} adott {giftNotice.n} kortyot \U0001F37A
        </div>
      )}
      {/* ── Scrollable content ── */}
      <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'12px 14px 8px', display:'flex', flexDirection:'column', gap:10 }}>"""
rep(OLD, NEW)

# ── 5c) Giver line in the "Kiosztott kortyok" feed ──────────────────────────
OLD = """                {totalExpected > 0 && <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft }}>{totalGiven} / {totalExpected} korty</div>}
              </div>
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:6 }}>"""
NEW = """                {totalExpected > 0 && <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft }}>{totalGiven} / {totalExpected} korty</div>}
              </div>
              {buszState.lastGift && buszState.lastGift.giverName && (
                <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginBottom:6 }}>Utoljára osztott: <b style={{ color:T.ink }}>{buszState.lastGift.giverName}</b></div>
              )}
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:6 }}>"""
rep(OLD, NEW)

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(c)
print('patch_busz_hostmode OK — all replacements applied')
