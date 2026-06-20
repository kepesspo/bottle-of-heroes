#!/usr/bin/env python3
"""v9.329 — Fix double bottom padding: root container handles safe area, footers use visual only"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Root container already adds paddingBottom:env(safe-area-inset-bottom)
# So all individual footers must NOT add it again — just visual spacing

# ── 1. BottomBar component
old_bb = "      paddingBottom:'max(14px, env(safe-area-inset-bottom))',"
new_bb = "      paddingBottom:14,"
assert old_bb in html, "FAIL: BottomBar pad"
html = html.replace(old_bb, new_bb, 1)

# ── 2. BottomBar CSS
old_bb_css = ".bottombar-shell { padding:14px 0 max(14px, env(safe-area-inset-bottom)); }"
new_bb_css = ".bottombar-shell { padding:14px 0 14px; }"
assert old_bb_css in html, "FAIL: bottombar CSS"
html = html.replace(old_bb_css, new_bb_css, 1)

# ── 3. BottomBar landscape CSS
old_bb_land = ".bottombar-shell { padding:6px 0 max(8px, env(safe-area-inset-bottom)); }"
new_bb_land = ".bottombar-shell { padding:6px 0 8px; }"
assert old_bb_land in html, "FAIL: bottombar landscape"
html = html.replace(old_bb_land, new_bb_land, 1)

# ── 4. PlayScreen footer
old_pf = "padding:'8px 16px', paddingBottom:'max(8px, env(safe-area-inset-bottom))', background:'transparent'"
new_pf = "padding:'8px 16px', paddingBottom:8, background:'transparent'"
assert old_pf in html, "FAIL: PlayScreen footer"
html = html.replace(old_pf, new_pf, 1)

# ── 5. Game sub-screen footers
old_sf = "padding:'8px 18px', paddingBottom:'max(8px, env(safe-area-inset-bottom))'"
new_sf = "padding:'8px 18px', paddingBottom:8"
count = html.count(old_sf)
assert count >= 1, f"FAIL: sub footers ({count})"
html = html.replace(old_sf, new_sf)

# ── 6. Observer footer
old_of = "padding:'8px 14px 0', paddingBottom:'max(8px, env(safe-area-inset-bottom))'"
new_of = "padding:'8px 14px 0', paddingBottom:8"
assert old_of in html, "FAIL: obs footer"
html = html.replace(old_of, new_of, 1)

# ── 7. End screen footer
old_ef = "paddingBottom:'max(12px, env(safe-area-inset-bottom))', marginTop:'auto'"
new_ef = "paddingBottom:12, marginTop:'auto'"
assert old_ef in html, "FAIL: end footer"
html = html.replace(old_ef, new_ef, 1)

html = html.replace("const APP_VERSION = 'v9.328';", "const APP_VERSION = 'v9.329';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.329 — double bottom padding fixed, root container handles safe area")
