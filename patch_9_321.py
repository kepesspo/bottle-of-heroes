#!/usr/bin/env python3
"""v9.321 — Fix: home screen top buttons hidden under status bar (black-translucent)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix .home-inner top padding — needs safe-area-inset-top buffer for logo
old_home_inner = "      gap:28px; padding:52px 22px 44px;"
new_home_inner = "      gap:28px; padding:max(52px, calc(env(safe-area-inset-top) + 36px)) 22px 44px;"
assert old_home_inner in html, "FAIL: home-inner padding"
html = html.replace(old_home_inner, new_home_inner, 1)

# Fix top-left absolute (version chip) — top:14 → safe area aware
old_topleft = "        <div style={{ position:'absolute', top:14, left:18, zIndex:10, display:'flex', flexDirection:'column', gap:8, alignItems:'flex-start' }}>"
new_topleft = "        <div style={{ position:'absolute', top:'max(14px, calc(env(safe-area-inset-top) + 8px))', left:18, zIndex:10, display:'flex', flexDirection:'column', gap:8, alignItems:'flex-start' }}>"
assert old_topleft in html, "FAIL: topleft"
html = html.replace(old_topleft, new_topleft, 1)

# Fix top-right absolute (settings/stats pill) — top:14 → safe area aware
old_topright = "        <div style={{ position:'absolute', top:14, right:18, zIndex:10, display:'flex', background:T.surface, borderRadius:18, boxShadow:T.shadow, overflow:'hidden' }}>"
new_topright = "        <div style={{ position:'absolute', top:'max(14px, calc(env(safe-area-inset-top) + 8px))', right:18, zIndex:10, display:'flex', background:T.surface, borderRadius:18, boxShadow:T.shadow, overflow:'hidden' }}>"
assert old_topright in html, "FAIL: topright"
html = html.replace(old_topright, new_topright, 1)

html = html.replace("const APP_VERSION = 'v9.320';", "const APP_VERSION = 'v9.321';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.321 — Home screen top buttons safe-area fix")
