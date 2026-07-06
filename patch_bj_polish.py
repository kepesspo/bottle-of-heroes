#!/usr/bin/env python3
# v9.799 — Blackjack: rebuy stack picker, card deal animation, prominent gift modal + gift log
import io

P = '/home/user/bottle-of-heroes/index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global c
    assert old in c, 'MISSING: ' + old[:90]
    assert c.count(old) == cnt, 'COUNT %d != %d: %s' % (c.count(old), cnt, old[:90])
    c = c.replace(old, new)

# ── 2a. CSS keyframe ──
OLD = "@keyframes popIn     { from{transform:scale(.7);opacity:0} to{transform:scale(1);opacity:1} }"
rep(OLD, OLD + "\n    @keyframes bjDeal    { from { opacity:0; transform: translateY(-14px) rotate(-6deg) scale(.9); } to { opacity:1; transform:none; } }")

# ── 2b. BJCardEl animation (face-down + face-up) ──
rep("border:'2px solid rgba(255,255,255,0.25)', display:'grid', placeItems:'center', fontSize:small?18:24, flexShrink:0 }}>🂠</div>",
    "border:'2px solid rgba(255,255,255,0.25)', display:'grid', placeItems:'center', fontSize:small?18:24, flexShrink:0, animation:'bjDeal .3s ease-out' }}>🂠</div>")
rep("background:'#fff', border:'2px solid #ddd', display:'flex', flexDirection:'column', padding:'3px 5px', flexShrink:0, userSelect:'none' }}>",
    "background:'#fff', border:'2px solid #ddd', display:'flex', flexDirection:'column', padding:'3px 5px', flexShrink:0, userSelect:'none', animation:'bjDeal .3s ease-out' }}>")

# ── 1a. BJStackPicker component (before BJGiftOverlay) ──
ANCHOR = "// Kiszállási nyereség-kiosztó overlay — kortyok szétosztása a többi játékos közt"
PICKER = """// Készlet-választó újra-beszálláshoz (5/10/20)
function BJStackPicker({ onConfirm, onCancel }) {
  const [sel, setSel] = React.useState(10);
  return (
    <div style={{ marginTop:10, padding:'10px', borderRadius:12, background:T.surfaceMuted }}>
      <div style={{ fontFamily:T.font, fontSize:12, fontWeight:800, color:T.ink, marginBottom:8, textAlign:'center' }}>Mekkora készlettel szállsz be? 🍺</div>
      <div style={{ display:'flex', gap:6 }}>
        {[5, 10, 20].map(v => (
          <button key={v} onClick={() => setSel(v)} style={{ flex:1, padding:'9px 0', borderRadius:10, border:`2px solid ${sel === v ? T.mint : 'transparent'}`, background: sel === v ? T.mintSoft : T.surface, fontFamily:T.font, fontWeight:900, fontSize:15, color: sel === v ? T.mint : T.inkSoft, cursor:'pointer' }}>{v}</button>
        ))}
      </div>
      <div style={{ display:'flex', gap:6, marginTop:8 }}>
        <button onClick={() => onConfirm(sel)} style={{ flex:1, padding:'10px', borderRadius:10, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>Beszállok {sel} 🍺-vel ✓</button>
        <button onClick={onCancel} style={{ padding:'10px 14px', borderRadius:10, border:'none', background:T.surface, fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, cursor:'pointer' }}>✕</button>
      </div>
    </div>
  );
}

"""
rep(ANCHOR, PICKER + ANCHOR)

# ── 1b. Host: hostRebuy takes stack + picker state ──
rep("""  function hostRebuy(pid, mustDrink) {
    const st = stackOf(pid);
    if (mustDrink) bookDrinks(pid, st);
    update({ ...bjState, chips: { ...(bjState.chips || {}), [pid]: st }, cashedOut: { ...(bjState.cashedOut || {}), [pid]: false } });
  }""",
"""  function hostRebuy(pid, mustDrink, newStack) {
    if (mustDrink) bookDrinks(pid, stackOf(pid));
    update({ ...bjState, stacks: { ...(bjState.stacks || {}), [pid]: newStack }, chips: { ...(bjState.chips || {}), [pid]: newStack }, cashedOut: { ...(bjState.cashedOut || {}), [pid]: false } });
  }""")
rep("  const [giftFor, setGiftFor] = React.useState(null); // { pid, pool } — kiszálló nyereség-kiosztása",
    "  const [giftFor, setGiftFor] = React.useState(null); // { pid, pool } — kiszálló nyereség-kiosztása\n  const [hostRebuyPick, setHostRebuyPick] = React.useState(null); // pid — újra-beszállás készlet-választó")

# ── 1c. Host ResultsView broke row: rebuy button opens picker ──
rep("""                  {!isOnline && (
                    <div style={{ display:'flex', gap:8, marginTop:8 }}>
                      <button onClick={() => hostRebuy(pid, true)} style={{ flex:1, padding:'9px', borderRadius:10, border:'none', background:T.mint, fontFamily:T.font, fontWeight:800, fontSize:12, color:'#fff', cursor:'pointer' }}>🔄 Megitta — újra beszáll</button>
                      <button onClick={() => update({ ...bjState, cashedOut: { ...(bjState.cashedOut || {}), [pid]: true } })} style={{ flex:1, padding:'9px', borderRadius:10, border:'none', background:'#555', fontFamily:T.font, fontWeight:800, fontSize:12, color:'#fff', cursor:'pointer' }}>🚪 Megitta — kiszáll</button>
                    </div>
                  )}""",
"""                  {!isOnline && hostRebuyPick !== pid && (
                    <div style={{ display:'flex', gap:8, marginTop:8 }}>
                      <button onClick={() => setHostRebuyPick(pid)} style={{ flex:1, padding:'9px', borderRadius:10, border:'none', background:T.mint, fontFamily:T.font, fontWeight:800, fontSize:12, color:'#fff', cursor:'pointer' }}>🔄 Megitta — újra beszáll</button>
                      <button onClick={() => update({ ...bjState, cashedOut: { ...(bjState.cashedOut || {}), [pid]: true } })} style={{ flex:1, padding:'9px', borderRadius:10, border:'none', background:'#555', fontFamily:T.font, fontWeight:800, fontSize:12, color:'#fff', cursor:'pointer' }}>🚪 Megitta — kiszáll</button>
                    </div>
                  )}
                  {!isOnline && hostRebuyPick === pid && (
                    <BJStackPicker onConfirm={v => { hostRebuy(pid, true, v); setHostRebuyPick(null); }} onCancel={() => setHostRebuyPick(null)} />
                  )}""")

# ── 3a. Host: giftLog append in hostConfirmGift (both branches share lastGift) ──
rep("""    const lastGift = { giverId: g.pid, giverName: giver?.name || '?', assigned, ts: Date.now() };
    if (isOnline) {
      bjBookDrinksRemoteMulti(roomCode, assigned, { bjState: { ...bjState, lastGift, cashedOut: { ...(bjState.cashedOut || {}), [g.pid]: true } } });""",
"""    const lastGift = { giverId: g.pid, giverName: giver?.name || '?', assigned, ts: Date.now() };
    const giftLog = [...(bjState.giftLog || []), { giverName: lastGift.giverName, assigned, ts: lastGift.ts }].slice(-10);
    if (isOnline) {
      bjBookDrinksRemoteMulti(roomCode, assigned, { bjState: { ...bjState, lastGift, giftLog, cashedOut: { ...(bjState.cashedOut || {}), [g.pid]: true } } });""")
rep("      update({ ...bjState, lastGift, cashedOut: { ...(bjState.cashedOut || {}), [g.pid]: true } });",
    "      update({ ...bjState, lastGift, giftLog, cashedOut: { ...(bjState.cashedOut || {}), [g.pid]: true } });")

# ── 3b. Guest: giftLog append in guestConfirmGift ──
rep("""  const guestConfirmGift = (assigned) => {
    setGiftPool(null);
    bjBookDrinksRemoteMulti(code, assigned, {
      bjState: { ...bj, lastGift: { giverId: playerId, giverName: me?.name || '?', assigned, ts: Date.now() }, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } }
    });
  };""",
"""  const guestConfirmGift = (assigned) => {
    setGiftPool(null);
    const ts = Date.now();
    const giftLog = [...(bj.giftLog || []), { giverName: me?.name || '?', assigned, ts }].slice(-10);
    bjBookDrinksRemoteMulti(code, assigned, {
      bjState: { ...bj, lastGift: { giverId: playerId, giverName: me?.name || '?', assigned, ts }, giftLog, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } }
    });
  };""")

# ── 3c. Observer: gift effect — persistent modal, localStorage seen-ts, mount catch-up ──
rep("""  const [giftNotice, setGiftNotice] = React.useState(null); // { name, n, ts } — ki adott nekem kortyot
  const bjGiftTsRef = React.useRef(undefined);
  React.useEffect(() => {
    const lg = bj && bj.lastGift;
    if (bjGiftTsRef.current === undefined) { bjGiftTsRef.current = lg ? lg.ts : null; return; }
    if (!lg || lg.ts === bjGiftTsRef.current) return;
    bjGiftTsRef.current = lg.ts;
    if (!playerId) return;
    const n = (lg.assigned || {})[playerId] || 0;
    if (n > 0 && lg.giverId !== playerId) {
      const ts = lg.ts;
      setGiftNotice({ name: lg.giverName || '?', n, ts });
      setTimeout(() => setGiftNotice(cur => (cur && cur.ts === ts) ? null : cur), 4500);
    }
  }, [bj && bj.lastGift && bj.lastGift.ts, playerId]);""",
"""  const [giftNotice, setGiftNotice] = React.useState(null); // { name, n, ts } — ki adott nekem kortyot (modal, amíg le nem OK-zza)
  React.useEffect(() => {
    const lg = bj && bj.lastGift;
    if (!playerId || !lg || !lg.ts) return;
    const n = (lg.assigned || {})[playerId] || 0;
    if (n <= 0 || lg.giverId === playerId) return;
    let seen = 0;
    try { seen = parseInt(localStorage.getItem('bj_gift_seen_' + playerId) || '0', 10) || 0; } catch(e) {}
    if (lg.ts <= seen) return;
    setGiftNotice({ name: lg.giverName || '?', n, ts: lg.ts });
  }, [bj && bj.lastGift && bj.lastGift.ts, playerId]);
  const dismissGift = () => {
    if (giftNotice) { try { localStorage.setItem('bj_gift_seen_' + playerId, String(giftNotice.ts)); } catch(e) {} }
    setGiftNotice(null);
  };""")

# ── 3d. Observer: toast → full-screen centered modal ──
rep("""      {giftNotice && (
        <div style={{ position:'fixed', top:'max(14px, env(safe-area-inset-top))', left:'50%', transform:'translateX(-50%)', zIndex:620, background:T.coral, color:'#fff', borderRadius:999, padding:'10px 18px', fontFamily:T.font, fontWeight:700, fontSize:14, boxShadow:'0 6px 20px rgba(0,0,0,0.3)', animation:'popIn .25s', whiteSpace:'nowrap' }}>
          {giftNotice.name} adott {giftNotice.n} kortyot 🍺
        </div>
      )}""",
"""      {giftNotice && (
        <div style={{ position:'fixed', inset:0, zIndex:620, background:'rgba(0,0,0,0.72)', display:'flex', alignItems:'center', justifyContent:'center', padding:24 }}>
          <div style={{ width:'100%', maxWidth:340, background:T.surface, borderRadius:24, padding:'28px 22px', textAlign:'center', boxShadow:'0 12px 40px rgba(0,0,0,0.4)', animation:'popIn .25s' }}>
            <div style={{ fontSize:64 }}>🍺</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, marginTop:10 }}>{giftNotice.name} adott Neked {giftNotice.n} kortyot!</div>
            <button onClick={dismissGift} style={{ marginTop:18, width:'100%', padding:'14px', borderRadius:16, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', cursor:'pointer' }}>OK, iszom! ✓</button>
          </div>
        </div>
      )}""")

# ── 1d. Observer: guestRebuy takes stack; rebuy/visszaszállás buttons open picker ──
rep("""  const guestRebuy = (drinkN) => {
    if (drinkN > 0) bjBookDrinksRemote(code, playerId, drinkN);
    bjWrite(code, { ...bj, chips: { ...(bj.chips || {}), [playerId]: startStack }, cashedOut: { ...(bj.cashedOut || {}), [playerId]: false } });
  };""",
"""  const guestRebuy = (drinkN, newStack) => {
    if (drinkN > 0) bjBookDrinksRemote(code, playerId, drinkN);
    bjWrite(code, { ...bj, stacks: { ...(bj.stacks || {}), [playerId]: newStack }, chips: { ...(bj.chips || {}), [playerId]: newStack }, cashedOut: { ...(bj.cashedOut || {}), [playerId]: false } });
    setRebuyPick(null);
  };""")
rep("  const [giftPool, setGiftPool] = React.useState(null); // kiszállási nyereség kiosztása",
    "  const [giftPool, setGiftPool] = React.useState(null); // kiszállási nyereség kiosztása\n  const [rebuyPick, setRebuyPick] = React.useState(null); // { drinkN } — újra-beszállás készlet-választó")

# cashed-out "Visszaszállok"
rep("""            {amOut && (
              <button onClick={() => guestRebuy(0)} style={{ marginTop:14, width:'100%', padding:'13px', borderRadius:14, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>🔄 Visszaszállok ({startStack} 🍺 készlettel)</button>
            )}""",
"""            {amOut && !rebuyPick && (
              <button onClick={() => setRebuyPick({ drinkN: 0 })} style={{ marginTop:14, width:'100%', padding:'13px', borderRadius:14, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>🔄 Visszaszállok</button>
            )}
            {amOut && rebuyPick && (
              <BJStackPicker onConfirm={v => guestRebuy(rebuyPick.drinkN, v)} onCancel={() => setRebuyPick(null)} />
            )}""")

# broke rebuy
rep("""                        <div style={{ display:'flex', gap:8, marginTop:10 }}>
                          <button onClick={() => guestRebuy(startStack)} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🔄 Megittam — újra beszállok</button>""",
"""                        {!rebuyPick && (
                        <div style={{ display:'flex', gap:8, marginTop:10 }}>
                          <button onClick={() => setRebuyPick({ drinkN: startStack })} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🔄 Megittam — újra beszállok</button>""")
rep("""                          <button onClick={() => { bjBookDrinksRemote(code, playerId, startStack); bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } }); }} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:'#555', fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🚪 Kiszállok</button>
                        </div>""",
"""                          <button onClick={() => { bjBookDrinksRemote(code, playerId, startStack); bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } }); }} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:'#555', fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🚪 Kiszállok</button>
                        </div>
                        )}
                        {rebuyPick && (
                          <BJStackPicker onConfirm={v => guestRebuy(rebuyPick.drinkN, v)} onCancel={() => setRebuyPick(null)} />
                        )}""")

# ── 3e. Observer: gift log card under "Többiek" ──
rep("""              {(bj.participants || []).filter(pid => pid !== playerId).length === 0 && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, textAlign:'center', padding:'6px 0' }}>Egyedül játszol az osztó ellen</div>
              )}
            </div>
          </React.Fragment>""",
"""              {(bj.participants || []).filter(pid => pid !== playerId).length === 0 && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, textAlign:'center', padding:'6px 0' }}>Egyedül játszol az osztó ellen</div>
              )}
            </div>

            {/* Kapott kortyok log */}
            {(() => {
              const entries = (bj.giftLog || []).filter(g => ((g.assigned || {})[playerId] || 0) > 0).slice(-10).reverse();
              if (!entries.length) return null;
              return (
                <div style={{ background:T.surface, borderRadius:18, padding:'12px 14px', boxShadow:T.shadow, marginTop:12 }}>
                  <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>🍺 Kapott kortyok</div>
                  {entries.map((g, i) => {
                    const mins = Math.max(0, Math.round((Date.now() - (g.ts || 0)) / 60000));
                    return (
                      <div key={i} style={{ fontFamily:T.font, fontSize:12, color:T.ink, padding:'3px 0' }}>
                        <b>{g.giverName}</b> → {(g.assigned || {})[playerId]} korty <span style={{ color:T.inkSoft }}>· {mins} perce</span>
                      </div>
                    );
                  })}
                </div>
              );
            })()}
          </React.Fragment>""")

# ── Version bump ──
assert c.count("'v9.798'") == 1
rep("const APP_VERSION = 'v9.798';", "const APP_VERSION = 'v9.799';")

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
