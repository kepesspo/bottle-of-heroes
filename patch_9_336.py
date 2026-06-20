#!/usr/bin/env python3
"""v9.336 — Align footer pill with BottomBar: same max(14px, safe-area) formula"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Move safe area from outer div to footer wrapper so pill uses identical formula as BottomBar
# Outer div: remove paddingBottom (gradient still fills full height via flex:1)
old_outer = "flex:1, display:'flex', flexDirection:'column', background: T.playBg || T.bg, paddingBottom:'env(safe-area-inset-bottom)'"
new_outer = "flex:1, display:'flex', flexDirection:'column', background: T.playBg || T.bg"
assert old_outer in html, "FAIL: outer div"
html = html.replace(old_outer, new_outer, 1)

# Footer wrapper: use same formula as BottomBar (padding:'8px 16px' + paddingBottom override)
old_footer = "padding:'8px 16px', paddingBottom:0, background:'transparent'"
new_footer = "padding:'8px 16px', paddingBottom:'max(14px, env(safe-area-inset-bottom))', background:'transparent'"
assert old_footer in html, "FAIL: footer wrapper"
html = html.replace(old_footer, new_footer, 1)

html = html.replace("const APP_VERSION = 'v9.335';", "const APP_VERSION = 'v9.336';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.336 — footer pill now uses identical max(14px, env(safe-area-inset-bottom)) as BottomBar")
