#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. SFX fix: wait for resume() Promise before playing
old = """  let ctx = null;
  const ac = () => {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  };
  const play = (fn) => { try { fn(ac()); } catch(e) {} };"""
new = """  let ctx = null;
  const ac = () => {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    return ctx;
  };
  const play = (fn) => {
    try {
      const c = ac();
      if (c.state === 'suspended') {
        c.resume().then(() => { try { fn(c); } catch(e) {} }).catch(() => {});
      } else {
        fn(c);
      }
    } catch(e) {}
  };"""
assert old in html, "FAIL: SFX play"
html = html.replace(old, new, 1)

# ── 2. Sorrend reorder: also reorder pendingCommit.newPlayers
old = """                const reorder = (arr) => {
                  const curId = players[turn % players.length]?.id;
                  const newTurnIdx = arr.findIndex(p => p.id === curId);
                  setPlayers(arr);
                  if (newTurnIdx >= 0) setTurn(newTurnIdx);
                };"""
new = """                const reorder = (arr) => {
                  const curId = players[turn % players.length]?.id;
                  const newTurnIdx = arr.findIndex(p => p.id === curId);
                  setPlayers(arr);
                  if (newTurnIdx >= 0) setTurn(newTurnIdx);
                  setPendingCommit(pc => {
                    if (!pc) return pc;
                    const reorderedNew = arr.map(p => pc.newPlayers.find(np => np.id === p.id) || p);
                    const curIdInNew = pc.newPlayers[pc.newTurn % pc.newPlayers.length]?.id;
                    const newPcTurn = reorderedNew.findIndex(p => p.id === curIdInNew);
                    return { ...pc, newPlayers: reorderedNew, newTurn: newPcTurn >= 0 ? newPcTurn : pc.newTurn };
                  });
                };"""
assert old in html, "FAIL: reorder"
html = html.replace(old, new, 1)

# ── 3. Bottomsheet: sorrend tab same height as vezérlés (absolute positioned)
old = """              {/* SORREND — drag-and-drop player order */}
              {menuTab==='sorrend' && (() => {
                const reorder = (arr) => {
                  const curId = players[turn % players.length]?.id;
                  const newTurnIdx = arr.findIndex(p => p.id === curId);
                  setPlayers(arr);
                  if (newTurnIdx >= 0) setTurn(newTurnIdx);
                  setPendingCommit(pc => {
                    if (!pc) return pc;
                    const reorderedNew = arr.map(p => pc.newPlayers.find(np => np.id === p.id) || p);
                    const curIdInNew = pc.newPlayers[pc.newTurn % pc.newPlayers.length]?.id;
                    const newPcTurn = reorderedNew.findIndex(p => p.id === curIdInNew);
                    return { ...pc, newPlayers: reorderedNew, newTurn: newPcTurn >= 0 ? newPcTurn : pc.newTurn };
                  });
                };
                const shuffleOrder = () => {
                  const arr = [...players];
                  for (let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]];}
                  reorder(arr);
                };
                const movePlayer = (from, to) => {
                  if (from===to) return;
                  const arr=[...players];
                  const [item]=arr.splice(from,1);
                  arr.splice(to,0,item);
                  reorder(arr);
                };
                return (
                  <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                    <button onClick={shuffleOrder} style={{ width:'100%', padding:'13px', borderRadius:16, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
                      <span>🔀</span><span>Véletlen sorrend</span>
                    </button>
                    {players.map((p,i) => (
                      <div key={p.id}
                        draggable
                        onDragStart={() => setDragIdx(i)}
                        onDragOver={e => { e.preventDefault(); setOverIdx(i); }}
                        onDrop={() => { movePlayer(dragIdx, i); setDragIdx(null); setOverIdx(null); }}
                        onDragEnd={() => { setDragIdx(null); setOverIdx(null); }}
                        onTouchStart={e => { e.currentTarget._startY=e.touches[0].clientY; e.currentTarget._idx=i; setDragIdx(i); }}
                        onTouchMove={e => {
                          const dy = e.touches[0].clientY - e.currentTarget._startY;
                          const target = Math.max(0, Math.min(players.length-1, i + Math.round(dy/60)));
                          setOverIdx(target);
                        }}
                        onTouchEnd={() => { if(overIdx!==null) movePlayer(dragIdx, overIdx); setDragIdx(null); setOverIdx(null); }}
                        style={{ display:'flex', alignItems:'center', gap:12, padding:'12px 14px', borderRadius:14,
                          background: overIdx===i ? T.mintSoft : T.bgSoft,
                          border: `1.5px solid ${overIdx===i ? T.mint : 'transparent'}`,
                          opacity: dragIdx===i ? 0.5 : 1,
                          cursor:'grab', transition:'background .12s, border .12s' }}>
                        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkMute, minWidth:22, textAlign:'center' }}>{i+1}</span>
                        <div style={{ width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>
                        <div style={{ flex:1, fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{p.name}</div>
                        <span style={{ fontSize:18, color:T.inkMute }}>☰</span>
                      </div>
                    ))}
                    <div style={{ height:8 }} />
                  </div>
                );
              })()}"""
new = """              {/* SORREND — absolute overlay, same height as vezérlés */}
              <div style={{ visibility: menuTab==='sorrend' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto' }}>
                {(() => {
                  const reorder = (arr) => {
                    const curId = players[turn % players.length]?.id;
                    const newTurnIdx = arr.findIndex(p => p.id === curId);
                    setPlayers(arr);
                    if (newTurnIdx >= 0) setTurn(newTurnIdx);
                    setPendingCommit(pc => {
                      if (!pc) return pc;
                      const reorderedNew = arr.map(p => pc.newPlayers.find(np => np.id === p.id) || p);
                      const curIdInNew = pc.newPlayers[pc.newTurn % pc.newPlayers.length]?.id;
                      const newPcTurn = reorderedNew.findIndex(p => p.id === curIdInNew);
                      return { ...pc, newPlayers: reorderedNew, newTurn: newPcTurn >= 0 ? newPcTurn : pc.newTurn };
                    });
                  };
                  const shuffleOrder = () => {
                    const arr = [...players];
                    for (let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]];}
                    reorder(arr);
                  };
                  const movePlayer = (from, to) => {
                    if (from===to) return;
                    const arr=[...players];
                    const [item]=arr.splice(from,1);
                    arr.splice(to,0,item);
                    reorder(arr);
                  };
                  return (
                    <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                      <button onClick={shuffleOrder} style={{ width:'100%', padding:'13px', borderRadius:16, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
                        <span>🔀</span><span>Véletlen sorrend</span>
                      </button>
                      {players.map((p,i) => (
                        <div key={p.id}
                          draggable
                          onDragStart={() => setDragIdx(i)}
                          onDragOver={e => { e.preventDefault(); setOverIdx(i); }}
                          onDrop={() => { movePlayer(dragIdx, i); setDragIdx(null); setOverIdx(null); }}
                          onDragEnd={() => { setDragIdx(null); setOverIdx(null); }}
                          onTouchStart={e => { e.currentTarget._startY=e.touches[0].clientY; setDragIdx(i); }}
                          onTouchMove={e => {
                            e.preventDefault();
                            const dy = e.touches[0].clientY - e.currentTarget._startY;
                            const target = Math.max(0, Math.min(players.length-1, i + Math.round(dy/60)));
                            setOverIdx(target);
                          }}
                          onTouchEnd={e => { const oi = overIdx; const di = dragIdx; setDragIdx(null); setOverIdx(null); if(oi!==null && di!==null) movePlayer(di, oi); }}
                          style={{ display:'flex', alignItems:'center', gap:12, padding:'12px 14px', borderRadius:14,
                            background: overIdx===i ? T.mintSoft : T.bgSoft,
                            border: `1.5px solid ${overIdx===i ? T.mint : 'transparent'}`,
                            opacity: dragIdx===i ? 0.5 : 1,
                            cursor:'grab', transition:'background .12s, border .12s',
                            touchAction:'none' }}>
                          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkMute, minWidth:22, textAlign:'center' }}>{i+1}</span>
                          <div style={{ width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>
                          <div style={{ flex:1, fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{p.name}</div>
                          <span style={{ fontSize:18, color:T.inkMute }}>☰</span>
                        </div>
                      ))}
                      <div style={{ height:8 }} />
                    </div>
                  );
                })()}
              </div>"""
assert old in html, "FAIL: sorrend tab"
html = html.replace(old, new, 1)

# ── version bump
old_v = "const APP_VERSION = 'v9.275';"
new_v = "const APP_VERSION = 'v9.276';"
assert old_v in html, "FAIL: version"
html = html.replace(old_v, new_v, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.276 — SFX async fix, sorrend pendingCommit sync, bottomsheet magasság")
