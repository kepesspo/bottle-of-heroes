#!/usr/bin/env python3
"""v9.322 — Fix: PlayScreen top bar hidden under status bar"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# PlayScreen main top bar — missing safe-area-inset-top
old_topbar = "      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, padding:`10px 16px 6px`, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>"
new_topbar = "      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, paddingTop:'max(10px, calc(env(safe-area-inset-top) + 6px))', paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>"
assert old_topbar in html, "FAIL: PlayScreen topbar"
html = html.replace(old_topbar, new_topbar, 1)

html = html.replace("const APP_VERSION = 'v9.321';", "const APP_VERSION = 'v9.322';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.322 — PlayScreen top bar safe-area fix")
