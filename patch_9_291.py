#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Tab sorrend: Profil, Játékok, Beer Pong, Busz
old = """          {[
            { k:'profil', icon:<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6"/></svg>, l:'Profil' },
            { k:'bp',   icon:<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 3h14l-1 9H6L5 3z"/><path d="M8 21h8M12 12v9"/><path d="M19 3c0 0 1 2 1 4s-1 4-1 4"/></svg>, l:'Beer Pong' },
            { k:'busz', icon:<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="5" width="20" height="14" rx="3"/><path d="M2 10h20"/><circle cx="7" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/></svg>, l:'Busz' },
            { k:'games', icon:<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="6" width="20" height="12" rx="3"/><path d="M8 12h2m-1-1v2M15 12h2M12 10v4"/></svg>, l:'Játékok' },
          ].map(t => ("""
new = """          {[
            { k:'profil', icon:<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6"/></svg>, l:'Profil' },
            { k:'games', icon:<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="6" width="20" height="12" rx="3"/><path d="M8 12h2m-1-1v2M15 12h2M12 10v4"/></svg>, l:'Játékok' },
            { k:'bp',   icon:<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 3h14l-1 9H6L5 3z"/><path d="M8 21h8M12 12v9"/><path d="M19 3c0 0 1 2 1 4s-1 4-1 4"/></svg>, l:'Beer Pong' },
            { k:'busz', icon:<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="5" width="20" height="14" rx="3"/><path d="M2 10h20"/><circle cx="7" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/></svg>, l:'Busz' },
          ].map(t => ("""
assert old in html, "FAIL: tab sorrend"
html = html.replace(old, new, 1)

# ── 2. Profil kártya jobb felső: pont helyett win rate → pont
old2 = """                      <div style={{ textAlign:'right', flexShrink:0 }}>
                        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:wrColor, lineHeight:1 }}>{wr !== null ? wr+'%' : '–'}</div>
                        <div style={{ fontFamily:T.font, fontSize:9, color:T.inkMute, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.08em' }}>WIN RATE</div>
                      </div>"""
new2 = """                      <div style={{ textAlign:'right', flexShrink:0 }}>
                        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.yellow||'#F59E0B', lineHeight:1 }}>{s.totalPoints||0}</div>
                        <div style={{ fontFamily:T.font, fontSize:9, color:T.inkMute, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.08em' }}>PONT</div>
                      </div>"""
assert old2 in html, "FAIL: profil kártya pont"
html = html.replace(old2, new2, 1)

html = html.replace("const APP_VERSION = 'v9.290';", "const APP_VERSION = 'v9.291';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.291 — stat tab sorrend: Profil/Játékok/BP/Busz, profil kártya: pont a jobb felső sarokban")
