#!/usr/bin/env python3
"""v9.335 — Revert content centering, lower footer pill to match BottomBar position"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Revert game content inner div: remove justifyContent + minHeight (top-align content)
old_content = "display:'flex', flexDirection:'column', justifyContent:'center', padding:'8px 24px 20px', gap:18, maxWidth:960, margin:'0 auto', width:'100%', boxSizing:'border-box', minHeight:'100%'"
new_content = "display:'flex', flexDirection:'column', padding:'8px 24px 20px', gap:18, maxWidth:960, margin:'0 auto', width:'100%', boxSizing:'border-box'"
assert old_content in html, "FAIL: content inner div"
html = html.replace(old_content, new_content, 1)

# ── 2. Footer wrapper: remove paddingBottom:8 so pill sits at same height as BottomBar pill
old_footer = "padding:'8px 16px', paddingBottom:8, background:'transparent'"
new_footer = "padding:'8px 16px', paddingBottom:0, background:'transparent'"
assert old_footer in html, "FAIL: footer wrapper paddingBottom"
html = html.replace(old_footer, new_footer, 1)

html = html.replace("const APP_VERSION = 'v9.334';", "const APP_VERSION = 'v9.335';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.335 — content top-aligned, footer pill lowered to match BottomBar")
