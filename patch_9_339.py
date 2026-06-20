#!/usr/bin/env python3
"""v9.339 — Fix color mismatch: outer div uses T.bg (solid) not T.playBg (gradient)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Game components inside scroll area use T.bg (solid color).
# Footer wrapper is transparent → shows outer div background.
# If outer div uses T.playBg (gradient), footer area color ≠ game content color.
# Fix: outer div uses T.bg (same solid color as game components).
old_outer = "flex:1, display:'flex', flexDirection:'column', background: T.playBg || T.bg, paddingBottom:'max(14px, env(safe-area-inset-bottom))'"
new_outer = "flex:1, display:'flex', flexDirection:'column', background: T.bg, paddingBottom:'max(14px, env(safe-area-inset-bottom))'"
assert old_outer in html, "FAIL: outer div background"
html = html.replace(old_outer, new_outer, 1)

html = html.replace("const APP_VERSION = 'v9.338';", "const APP_VERSION = 'v9.339';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.339 — outer div uses T.bg solid color, footer matches game content background")
