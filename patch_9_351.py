#!/usr/bin/env python3
"""v9.351 — Install button: secondary style (outlined), not competing with main CTA"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_btn = """          {!isStandalone && (
            <button onClick={() => setShowInstall(true)} style={{ display:'flex', alignItems:'center', gap:14, width:'100%', padding:'16px 20px', background:T.mint, border:'none', borderRadius:20, cursor:'pointer', textAlign:'left', boxShadow:`0 4px 0 ${T.mintDeep}, 0 6px 24px ${T.mint}55` }}>
              <div style={{ width:48, height:48, borderRadius:14, background:'rgba(255,255,255,0.22)', display:'grid', placeItems:'center', flexShrink:0 }}>
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v13M8 12l4 4 4-4"/><rect x="3" y="18" width="18" height="3" rx="1.5" fill="#fff" stroke="none"/></svg>
              </div>
              <div style={{ flex:1 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', letterSpacing:'-0.01em' }}>{t('addToHome')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.82)', marginTop:2 }}>{t('installHomeBtn')}</div>
              </div>
              <svg width="20" height="20" viewBox="0 0 18 18" fill="none"><path d="M7 4l5 5-5 5" stroke="rgba(255,255,255,0.7)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/></svg>
            </button>
          )}"""

new_btn = """          {!isStandalone && (
            <button onClick={() => setShowInstall(true)} style={{ display:'flex', alignItems:'center', gap:12, width:'100%', padding:'12px 16px', background:T.surface, border:`1.5px solid ${T.mint}55`, borderRadius:18, cursor:'pointer', textAlign:'left', boxShadow:T.shadow }}>
              <div style={{ width:36, height:36, borderRadius:10, background:T.mintSoft, display:'grid', placeItems:'center', flexShrink:0 }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={T.mint} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v13M8 12l4 4 4-4"/><rect x="3" y="18" width="18" height="3" rx="1.5" fill={T.mint} stroke="none"/></svg>
              </div>
              <div style={{ flex:1 }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.mint }}>{t('addToHome')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:1 }}>{t('installHomeBtn')}</div>
              </div>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M7 4l5 5-5 5" stroke={T.inkSoft} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
            </button>
          )}"""

assert old_btn in html, "FAIL: install button"
html = html.replace(old_btn, new_btn, 1)

html = html.replace("const APP_VERSION = 'v9.350';", "const APP_VERSION = 'v9.351';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.351 — install button secondary style, white bg + mint border/accent")
