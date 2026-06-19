#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Tab bar: ['állás','vezérlés'] → ['állás','sorrend','vezérlés']
old = "                {['állás','vezérlés'].map(tab => ("
new = "                {['állás','sorrend','vezérlés'].map(tab => ("
assert old in html, "FAIL: tab list"
html = html.replace(old, new, 1)

# ── 2. Tab contents wrapper: add SORREND tab between állás and vezérlés
old = """              {/* VEZÉRLÉS — relative, determines container height */}
              <div style={{ visibility: menuTab==='vezérlés' ? 'visible' : 'hidden', display:'flex', flexDirection:'column', gap:10 }}>"""

new = """              {/* SORREND — drag-and-drop player order */}
              {menuTab==='sorrend' && (() => {
                const [dragIdx, setDragIdx] = React.useState(null);
                const [overIdx, setOverIdx] = React.useState(null);
                const shuffleOrder = () => {
                  const arr = [...players];
                  for (let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]];}
                  setPlayers(arr); setPendingCommit(null);
                };
                const movePlayer = (from, to) => {
                  if (from===to) return;
                  const arr=[...players];
                  const [item]=arr.splice(from,1);
                  arr.splice(to,0,item);
                  setPlayers(arr); setPendingCommit(null);
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
              })()}

              {/* VEZÉRLÉS — relative, determines container height */}
              <div style={{ visibility: menuTab==='vezérlés' ? 'visible' : 'hidden', display:'flex', flexDirection:'column', gap:10 }}>"""

assert old in new or old in html, "sanity"
assert old in html, "FAIL: vezérlés anchor"
html = html.replace(old, new, 1)

# ── 3. Version bump
old_ver = "const APP_VERSION = 'v9.267';"
new_ver = "const APP_VERSION = 'v9.268';"
assert old_ver in html, "FAIL: version"
html = html.replace(old_ver, new_ver, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.268 — Sorrend tab drag&drop + véletlen gomb")
