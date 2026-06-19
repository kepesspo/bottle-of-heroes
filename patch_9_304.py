#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """              <button onClick={onQuickGame} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', gap:10, padding:'0 12px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
                <div style={{ width:36, height:36, borderRadius:'50%', background:'#F59E0B22', display:'grid', placeItems:'center', flexShrink:0 }}>
                  <span style={{ fontSize:18 }}>⚡</span>
                </div>
                <div style={{ textAlign:'left' }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#F59E0B', letterSpacing:'-0.01em' }}>Quick Game</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>2 véletlen játékos</div>
                </div>
              </button>"""

new = """              <button onClick={onQuickGame} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', gap:10, padding:'0 12px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
                <div style={{ width:36, height:36, borderRadius:'50%', background:T.mintSoft, display:'grid', placeItems:'center', flexShrink:0 }}>
                  <span style={{ fontSize:18 }}>⚡</span>
                </div>
                <div style={{ textAlign:'left' }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.mint, letterSpacing:'-0.01em' }}>Quick Game</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>2 véletlen játékos</div>
                </div>
              </button>"""

assert old in html, "FAIL: Quick Game button color"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.303';", "const APP_VERSION = 'v9.304';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.304 — Quick Game gomb T.mint témakövető szín")
