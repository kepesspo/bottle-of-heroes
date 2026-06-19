#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """                {/* Action buttons */}
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => { undoLast(); setShowMenu(false); }} disabled={!undoRef.current} style={{ flex:1, minHeight:56, border:`1.5px solid ${undoRef.current ? T.inkMute+'66' : T.inkMute+'22'}`, background:T.surface, color: undoRef.current ? T.ink : T.inkMute+'55', fontFamily:T.font, fontWeight:700, fontSize:13, borderRadius:14, cursor: undoRef.current ? 'pointer' : 'default', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:3 }}>
                    <span style={{ fontSize:18 }}>↩</span>
                    <span>Vissza</span>
                  </button>
                  <button onClick={() => { setPendingCommit(null); setGameRestartKey(k=>k+1); setShowMenu(false); }} style={{ flex:1, minHeight:56, border:`1.5px solid ${T.inkMute}44`, background:T.surface, color:T.ink, fontFamily:T.font, fontWeight:700, fontSize:13, borderRadius:14, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:3 }}>
                    <span style={{ fontSize:18 }}>🔄</span>
                    <span>Újra</span>
                  </button>
                  <button onClick={() => { setGameIdx(g=>g+1); setShowMenu(false); }} style={{ flex:1, minHeight:56, border:`1.5px solid ${T.ink}`, background:T.surface, color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, borderRadius:14, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:3 }}>
                    <span style={{ fontSize:18 }}>⏭</span>
                    <span>Következő</span>
                  </button>
                </div>

                <button onClick={() => { setShowMenu(false); saveCurrentGameStats(); if (setLastGameRound) setLastGameRound(round); try { localStorage.removeItem('boh_session'); } catch(e) {} go('end'); }} style={{ width:'100%', minHeight:52, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, borderRadius:14, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
                  <span>🏁</span><span>Kilépés</span>
                </button>"""
new = """                {/* Action buttons — A design: inline icon+text, Következő hangsúlyos */}
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => { undoLast(); setShowMenu(false); }} disabled={!undoRef.current}
                    style={{ flex:1, height:52, border:'none', borderRadius:16,
                      background: undoRef.current ? T.bgSoft : T.surfaceMuted,
                      color: undoRef.current ? T.ink : T.inkMute,
                      fontFamily:T.font, fontWeight:800, fontSize:14,
                      cursor: undoRef.current ? 'pointer' : 'default',
                      display:'flex', alignItems:'center', justifyContent:'center', gap:7,
                      opacity: undoRef.current ? 1 : 0.5 }}>
                    <span style={{ fontSize:17 }}>↩</span><span>Vissza</span>
                  </button>
                  <button onClick={() => { setPendingCommit(null); setGameRestartKey(k=>k+1); setShowMenu(false); }}
                    style={{ flex:1, height:52, border:'none', borderRadius:16,
                      background:T.bgSoft, color:T.ink,
                      fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer',
                      display:'flex', alignItems:'center', justifyContent:'center', gap:7 }}>
                    <span style={{ fontSize:17 }}>🔄</span><span>Újra</span>
                  </button>
                  <button onClick={() => { setGameIdx(g=>g+1); setShowMenu(false); }}
                    style={{ flex:2, height:52, border:'none', borderRadius:16,
                      background:T.mint, color:'#fff',
                      fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer',
                      display:'flex', alignItems:'center', justifyContent:'center', gap:8,
                      boxShadow:`0 4px 14px ${T.mint}44` }}>
                    <span style={{ fontSize:17 }}>⏭</span><span>Következő</span>
                  </button>
                </div>

                <button onClick={() => { setShowMenu(false); saveCurrentGameStats(); if (setLastGameRound) setLastGameRound(round); try { localStorage.removeItem('boh_session'); } catch(e) {} go('end'); }}
                  style={{ width:'100%', height:52, border:'none', background:T.mint, color:'#fff',
                    fontFamily:T.font, fontWeight:900, fontSize:15, borderRadius:16, cursor:'pointer',
                    display:'flex', alignItems:'center', justifyContent:'center', gap:8,
                    boxShadow:`0 4px 14px ${T.mint}44` }}>
                  <span>🏁</span><span>Kilépés</span>
                </button>"""

assert old in html, "FAIL: action buttons"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.280';", "const APP_VERSION = 'v9.281';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.281 — menü gombok A design (inline, Következő hangsúlyos)")
