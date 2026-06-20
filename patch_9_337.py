#!/usr/bin/env python3
"""v9.337 — Fix bottom color strip: gradient outer div handles max(14px,safe-area), footer paddingBottom:0"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Outer div: add max(14px, env) so gradient covers the full zone (no color mismatch)
old_outer = "flex:1, display:'flex', flexDirection:'column', background: T.playBg || T.bg"
new_outer = "flex:1, display:'flex', flexDirection:'column', background: T.playBg || T.bg, paddingBottom:'max(14px, env(safe-area-inset-bottom))'"
assert old_outer in html, "FAIL: outer div"
html = html.replace(old_outer, new_outer, 1)

# Footer wrapper: paddingBottom:0 — pill sits flush to inner bottom of outer div
old_footer = "padding:'8px 16px', paddingBottom:'max(14px, env(safe-area-inset-bottom))', background:'transparent'"
new_footer = "padding:'8px 16px', paddingBottom:0, background:'transparent'"
assert old_footer in html, "FAIL: footer wrapper"
html = html.replace(old_footer, new_footer, 1)

html = html.replace("const APP_VERSION = 'v9.336';", "const APP_VERSION = 'v9.337';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.337 — outer div gradient covers safe area zone, no color strip in browser or PWA")
