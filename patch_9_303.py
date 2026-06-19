#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """            <button onClick={onStartGame || (() => go('players'))} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:14, padding:'24px 12px 20px', border:'none', background:T.mint, borderRadius:20, cursor:'pointer', boxShadow:`0 6px 24px ${T.mint}55` }}>
              <div style={{ width:64, height:64, borderRadius:'50%', background:'rgba(255,255,255,0.25)', display:'grid', placeItems:'center' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="white"><polygon points="5,3 19,12 5,21"/></svg>
              </div>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff', letterSpacing:'-0.01em' }}>{t('play')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.75)', marginTop:3 }}>{t('newRound')}</div>
              </div>
            </button>
            <div style={{ flex:1, display:'flex', flexDirection:'column', gap:12 }}>
              <button onClick={() => go('observer')} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:8, padding:'12px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
                <div style={{ width:44, height:44, borderRadius:'50%', background:`${T.coral}18`, display:'grid', placeItems:'center' }}>
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={T.coral} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
                </div>
                <div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.coral, letterSpacing:'-0.01em' }}>{t('join')}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>{t('enterCode')}</div>
                </div>
              </button>
              <button onClick={onQuickGame} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:8, padding:'12px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
                <div style={{ width:44, height:44, borderRadius:'50%', background:'#F59E0B22', display:'grid', placeItems:'center' }}>
                  <span style={{ fontSize:22 }}>⚡</span>
                </div>
                <div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#F59E0B', letterSpacing:'-0.01em' }}>Quick Game</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>2 véletlen játékos</div>
                </div>
              </button>
            </div>"""

new = """            <button onClick={onStartGame || (() => go('players'))} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:14, padding:'24px 12px 20px', border:'none', background:T.mint, borderRadius:20, cursor:'pointer', boxShadow:`0 6px 24px ${T.mint}55` }}>
              <div style={{ width:64, height:64, borderRadius:'50%', background:'rgba(255,255,255,0.25)', display:'grid', placeItems:'center' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="white"><polygon points="5,3 19,12 5,21"/></svg>
              </div>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff', letterSpacing:'-0.01em' }}>{t('play')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.75)', marginTop:3 }}>{t('newRound')}</div>
              </div>
            </button>
            <div style={{ flex:1, display:'flex', flexDirection:'column', gap:12, alignSelf:'stretch' }}>
              <button onClick={() => go('observer')} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', gap:10, padding:'0 12px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
                <div style={{ width:36, height:36, borderRadius:'50%', background:`${T.coral}18`, display:'grid', placeItems:'center', flexShrink:0 }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={T.coral} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
                </div>
                <div style={{ textAlign:'left' }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.coral, letterSpacing:'-0.01em' }}>{t('join')}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>{t('enterCode')}</div>
                </div>
              </button>
              <button onClick={onQuickGame} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', gap:10, padding:'0 12px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
                <div style={{ width:36, height:36, borderRadius:'50%', background:'#F59E0B22', display:'grid', placeItems:'center', flexShrink:0 }}>
                  <span style={{ fontSize:18 }}>⚡</span>
                </div>
                <div style={{ textAlign:'left' }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#F59E0B', letterSpacing:'-0.01em' }}>Quick Game</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>2 véletlen játékos</div>
                </div>
              </button>
            </div>"""

assert old in html, "FAIL: home actions layout"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.302';", "const APP_VERSION = 'v9.303';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.303 — JÁTÉK gomb eredeti mérete, jobb oldali gombok vízszintes elrendezéssel igazodnak")
