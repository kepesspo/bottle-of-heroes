#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Inject SorrendTab component before APP ROUTER
anchor = "// ─── APP ROUTER ───────────────────────────────────────────────"
assert anchor in html, "FAIL: anchor"

sorrend_component = '''function SorrendTab({ players, setPlayers, turn, setTurn, pendingCommit, setPendingCommit }) {
  // Local copy so UI is always responsive
  const [localOrder, setLocalOrder] = React.useState(players);
  const [saved, setSaved] = React.useState(false);

  // Keep local in sync if players change externally (new round etc)
  const prevPlayersRef = React.useRef(players);
  React.useEffect(() => {
    // Only sync if IDs changed (new player added/removed), not on reorder
    const prevIds = prevPlayersRef.current.map(p=>p.id).join(',');
    const nextIds = players.map(p=>p.id).join(',');
    if (prevIds !== nextIds) {
      setLocalOrder(players);
    }
    prevPlayersRef.current = players;
  }, [players]);

  const applyOrder = (arr) => {
    setLocalOrder(arr);
    setSaved(true);
    setTimeout(() => setSaved(false), 1200);
    // Find current player in new order
    const curId = players[turn % Math.max(players.length,1)]?.id;
    const newTurnIdx = arr.findIndex(p => p.id === curId);
    setPlayers(arr);
    if (newTurnIdx >= 0) setTurn(newTurnIdx);
    setPendingCommit(pc => {
      if (!pc) return pc;
      const reorderedNew = arr.map(p => pc.newPlayers.find(np => np.id === p.id) || p);
      const curIdInNew = pc.newPlayers[pc.newTurn % Math.max(pc.newPlayers.length,1)]?.id;
      const newPcTurn = reorderedNew.findIndex(p => p.id === curIdInNew);
      return { ...pc, newPlayers: reorderedNew, newTurn: newPcTurn >= 0 ? newPcTurn : pc.newTurn };
    });
  };

  const moveUp = (i) => {
    if (i <= 0) return;
    const arr = [...localOrder];
    [arr[i-1], arr[i]] = [arr[i], arr[i-1]];
    applyOrder(arr);
  };
  const moveDown = (i) => {
    if (i >= localOrder.length - 1) return;
    const arr = [...localOrder];
    [arr[i], arr[i+1]] = [arr[i+1], arr[i]];
    applyOrder(arr);
  };
  const shuffle = () => {
    const arr = [...localOrder];
    for (let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]];}
    applyOrder(arr);
  };

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
      <button onClick={shuffle} style={{ width:'100%', padding:'13px', borderRadius:16, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
        <span>🔀</span><span>Véletlen sorrend</span>
      </button>
      {saved && <div style={{ textAlign:'center', fontFamily:T.font, fontSize:13, fontWeight:700, color:T.mint, padding:'4px 0' }}>✓ Sorrend frissítve</div>}
      {localOrder.map((p,i) => (
        <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 12px', borderRadius:14, background:T.bgSoft }}>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkMute, minWidth:20, textAlign:'center' }}>{i+1}</span>
          <div style={{ width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>
          <div style={{ flex:1, fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{p.name}</div>
          <div style={{ display:'flex', flexDirection:'column', gap:4 }}>
            <button
              onPointerDown={e => { e.stopPropagation(); moveUp(i); }}
              disabled={i===0}
              style={{ width:36, height:32, border:'none', borderRadius:8, background: i===0 ? T.surfaceMuted : T.surface, color: i===0 ? T.inkMute : T.ink, fontSize:16, cursor: i===0 ? 'default' : 'pointer', display:'grid', placeItems:'center', boxShadow: i===0 ? 'none' : '0 1px 4px rgba(0,0,0,0.15)', WebkitTapHighlightColor:'transparent' }}>▲</button>
            <button
              onPointerDown={e => { e.stopPropagation(); moveDown(i); }}
              disabled={i===localOrder.length-1}
              style={{ width:36, height:32, border:'none', borderRadius:8, background: i===localOrder.length-1 ? T.surfaceMuted : T.surface, color: i===localOrder.length-1 ? T.inkMute : T.ink, fontSize:16, cursor: i===localOrder.length-1 ? 'default' : 'pointer', display:'grid', placeItems:'center', boxShadow: i===localOrder.length-1 ? 'none' : '0 1px 4px rgba(0,0,0,0.15)', WebkitTapHighlightColor:'transparent' }}>▼</button>
          </div>
        </div>
      ))}
      <div style={{ height:8 }} />
    </div>
  );
}

'''
html = html.replace(anchor, sorrend_component + anchor, 1)

# ── 2. Replace the sorrend IIFE in the menu with <SorrendTab />
old_sorrend_div = """              {/* SORREND — absolute overlay, same height as vezérlés */}
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
                        <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 12px', borderRadius:14, background:T.bgSoft }}>
                          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkMute, minWidth:20, textAlign:'center' }}>{i+1}</span>
                          <div style={{ width:36, height:36, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff', flexShrink:0 }}>{(p.name||'?').charAt(0).toUpperCase()}</div>
                          <div style={{ flex:1, fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{p.name}</div>
                          <div style={{ display:'flex', flexDirection:'column', gap:4 }}>
                            <button onClick={() => movePlayer(i, i-1)} disabled={i===0}
                              style={{ width:32, height:28, border:'none', borderRadius:8, background: i===0 ? T.surfaceMuted : T.surface, color: i===0 ? T.inkMute : T.ink, fontSize:14, cursor: i===0 ? 'default' : 'pointer', display:'grid', placeItems:'center', boxShadow: i===0 ? 'none' : '0 1px 4px rgba(0,0,0,0.12)' }}>▲</button>
                            <button onClick={() => movePlayer(i, i+1)} disabled={i===players.length-1}
                              style={{ width:32, height:28, border:'none', borderRadius:8, background: i===players.length-1 ? T.surfaceMuted : T.surface, color: i===players.length-1 ? T.inkMute : T.ink, fontSize:14, cursor: i===players.length-1 ? 'default' : 'pointer', display:'grid', placeItems:'center', boxShadow: i===players.length-1 ? 'none' : '0 1px 4px rgba(0,0,0,0.12)' }}>▼</button>
                          </div>
                        </div>
                      ))}
                      <div style={{ height:8 }} />
                    </div>
                  );
                })()}
              </div>"""
new_sorrend_div = """              {/* SORREND — standalone component */}
              <div style={{ visibility: menuTab==='sorrend' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto' }}>
                {menuTab==='sorrend' && <SorrendTab players={players} setPlayers={setPlayers} turn={turn} setTurn={setTurn} pendingCommit={pendingCommit} setPendingCommit={setPendingCommit} />}
              </div>"""
assert old_sorrend_div in html, "FAIL: sorrend div"
html = html.replace(old_sorrend_div, new_sorrend_div, 1)

# ── version bump
html = html.replace("const APP_VERSION = 'v9.279';", "const APP_VERSION = 'v9.280';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.280 — SorrendTab önálló komponens, onPointerDown, localOrder state")
