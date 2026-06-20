#!/usr/bin/env python3
"""v9.394 — Játékváltás: slide animáció (kicsúszik balra, bejön jobbról)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS keyframes hozzáadása ───────────────────────────────────────────────
old_play_actions_css = """    .play-actions { display:flex; gap:12px; padding:0 24px 16px; }"""

new_play_actions_css = """    @keyframes gameSlideOut { 0%{opacity:1;transform:translateX(0)} 100%{opacity:0;transform:translateX(-48px)} }
    @keyframes gameSlideIn  { 0%{opacity:0;transform:translateX(48px)} 100%{opacity:1;transform:translateX(0)} }
    .play-actions { display:flex; gap:12px; padding:0 24px 16px; }"""

assert old_play_actions_css in html, "FAIL: play-actions css"
html = html.replace(old_play_actions_css, new_play_actions_css, 1)

# ── 2. A belső scrollable div-et key+animációval látjuk el ───────────────────
old_scroll_inner = """      {/* ── Scrollable content ── */}
      <div style={{ flex:'1 1 0', minHeight:0, overflowY:'scroll', WebkitOverflowScrolling:'touch', background:'transparent' }}>
        <div style={{ display:'flex', flexDirection:'column', padding:'8px 24px 20px', gap:18, maxWidth:960, margin:'0 auto', width:'100%', boxSizing:'border-box' }}>"""

new_scroll_inner = """      {/* ── Scrollable content ── */}
      <div style={{ flex:'1 1 0', minHeight:0, overflowY:'scroll', WebkitOverflowScrolling:'touch', background:'transparent', overflow:'hidden' }}>
        <div key={gameIdx} style={{ display:'flex', flexDirection:'column', padding:'8px 24px 20px', gap:18, maxWidth:960, margin:'0 auto', width:'100%', boxSizing:'border-box', animation: transitioning ? 'gameSlideOut 0.22s ease forwards' : 'gameSlideIn 0.28s cubic-bezier(0.2,0.9,0.3,1)' }}>"""

assert old_scroll_inner in html, "FAIL: scroll inner"
html = html.replace(old_scroll_inner, new_scroll_inner, 1)

html = html.replace("const APP_VERSION = 'v9.393';", "const APP_VERSION = 'v9.394';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.394 — Játékváltás slide animáció")
