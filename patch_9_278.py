#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Sorrend: replace drag-and-drop with up/down buttons (reliable on mobile)
old = """                  return (
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
                          onTouchStart={e => { e.currentTarget._startY=e.touches[0].clientY; dragIdxRef.current=i; overIdxRef.current=i; setDragIdx(i); }}
                          onTouchMove={e => {
                            e.preventDefault();
                            const dy = e.touches[0].clientY - e.currentTarget._startY;
                            const target = Math.max(0, Math.min(players.length-1, i + Math.round(dy/60)));
                            overIdxRef.current = target; setOverIdx(target);
                          }}
                          onTouchEnd={e => { const di=dragIdxRef.current, oi=overIdxRef.current; dragIdxRef.current=null; overIdxRef.current=null; setDragIdx(null); setOverIdx(null); if(di!==null && oi!==null && di!==oi) movePlayer(di, oi); }}
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
                  );"""
new = """                  return (
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
                  );"""
assert old in html, "FAIL: sorrend list"
html = html.replace(old, new, 1)

# ── 2. Végtelen gyűrű: teli piros háttér, körvonalak, középen körvonal animáció opcionálisan
old = """                <circle cx="27" cy="27" r={rOuter} fill="none" stroke={ringColor} strokeWidth="2.5"
                  strokeDasharray={circOuter}
                  strokeDashoffset={isInfinite ? circOuter * 0.25 : circOuter - dashOuter}
                  strokeLinecap="round"
                  style={{ transition:'stroke-dashoffset 0.5s ease', animation:'none' }} />
                {/* Inner ring: static background */}
                <circle cx="27" cy="27" r={rInner} fill="none" stroke={T.inkMute} strokeWidth="2" opacity="0.12" />
              </svg>
              <div style={{ position:'absolute', inset:6, background:T.surface, borderRadius:'50%', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
                {isInfinite ? (
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.coral, lineHeight:1, animation:'pulse 1.4s infinite' }}>∞</div>
                ) : (<>
                  <div style={{ fontFamily:T.font, fontSize:8, fontWeight:700, color:T.inkSoft, letterSpacing:'0.07em', lineHeight:1 }}>{t('roundLabel')}</div>
                  <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:T.ink, lineHeight:1.1, fontVariantNumeric:'tabular-nums' }}>{round}</div>
                </>)}
              </div>"""
new = """                {isInfinite ? (
                  <circle cx="27" cy="27" r={rOuter} fill={T.coral} opacity="0.15" />
                ) : null}
                <circle cx="27" cy="27" r={rOuter} fill="none" stroke={ringColor} strokeWidth="2.5"
                  strokeDasharray={circOuter}
                  strokeDashoffset={isInfinite ? 0 : circOuter - dashOuter}
                  strokeLinecap="round"
                  style={{ transition:'stroke-dashoffset 0.5s ease' }} />
                {/* Inner ring: static background */}
                <circle cx="27" cy="27" r={rInner} fill="none" stroke={T.inkMute} strokeWidth="2" opacity="0.12" />
              </svg>
              <div style={{ position:'absolute', inset:6, background:T.surface, borderRadius:'50%', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
                <div style={{ fontFamily:T.font, fontSize:8, fontWeight:700, color: isInfinite ? T.coral : T.inkSoft, letterSpacing:'0.07em', lineHeight:1 }}>{t('roundLabel')}</div>
                <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color: isInfinite ? T.coral : T.ink, lineHeight:1.1, fontVariantNumeric:'tabular-nums' }}>{round}</div>
              </div>"""
assert old in html, "FAIL: ring"
html = html.replace(old, new, 1)

# ── version bump
old_v = "const APP_VERSION = 'v9.277';"
new_v = "const APP_VERSION = 'v9.278';"
assert old_v in html, "FAIL: version"
html = html.replace(old_v, new_v, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.278 — sorrend nyilak, végtelen gyűrű piros teli")
