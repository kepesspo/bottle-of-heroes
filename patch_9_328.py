#!/usr/bin/env python3
"""v9.328 — Status bar: black style + simplified safe area (bottom only)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════════════════
# STRATEGY:
#  black-translucent: content starts at y=0, status bar text WHITE
#    → Problem: white text on white AppBar = invisible
#    → Problem: env(safe-area-inset-top) needed everywhere = complex
#
#  black: solid black status bar, content starts BELOW it
#    → env(safe-area-inset-top) = 0, NO top padding needed anywhere
#    → Only env(safe-area-inset-bottom) needed for home indicator (~34px)
#    → Clean, simple, always readable
# ══════════════════════════════════════════════════════════════════════

# ── 1. Change status bar style to 'black'
old_status = '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>'
new_status = '<meta name="apple-mobile-web-app-status-bar-style" content="black"/>'
assert old_status in html, "FAIL: status bar meta"
html = html.replace(old_status, new_status, 1)

# ── 2. Root screen container — remove top padding (black style puts content below status bar)
#    Keep only bottom padding for home indicator
old_screen_container = "paddingTop:'env(safe-area-inset-top)', paddingBottom:'env(safe-area-inset-bottom)', boxSizing:'border-box', animation:"
new_screen_container = "paddingBottom:'env(safe-area-inset-bottom)', boxSizing:'border-box', animation:"
assert old_screen_container in html, "FAIL: screen container padding"
html = html.replace(old_screen_container, new_screen_container, 1)

# ── 3. BottomBar — restore proper bottom padding for home indicator
old_bottombar_pad = "      paddingBottom:14,"
new_bottombar_pad = "      paddingBottom:'max(14px, env(safe-area-inset-bottom))',"
assert old_bottombar_pad in html, "FAIL: BottomBar pad"
html = html.replace(old_bottombar_pad, new_bottombar_pad, 1)

# ── 4. BottomBar CSS — restore bottom safe area
old_bottombar_css = ".bottombar-shell { padding:14px 0 14px; }"
new_bottombar_css = ".bottombar-shell { padding:14px 0 max(14px, env(safe-area-inset-bottom)); }"
assert old_bottombar_css in html, "FAIL: bottombar CSS"
html = html.replace(old_bottombar_css, new_bottombar_css, 1)

# ── 5. BottomBar landscape CSS
old_bottombar_landscape = ".bottombar-shell { padding:6px 0 8px; }"
new_bottombar_landscape = ".bottombar-shell { padding:6px 0 max(8px, env(safe-area-inset-bottom)); }"
assert old_bottombar_landscape in html, "FAIL: bottombar landscape CSS"
html = html.replace(old_bottombar_landscape, new_bottombar_landscape, 1)

# ── 6. PlayScreen footer — restore bottom safe area
old_play_footer = "padding:'8px 16px', paddingBottom:8, background:'transparent'"
new_play_footer = "padding:'8px 16px', paddingBottom:'max(8px, env(safe-area-inset-bottom))', background:'transparent'"
assert old_play_footer in html, "FAIL: PlayScreen footer"
html = html.replace(old_play_footer, new_play_footer, 1)

# ── 7. Game sub-screen footers
old_sub_footer = "padding:'8px 18px', paddingBottom:8"
new_sub_footer = "padding:'8px 18px', paddingBottom:'max(8px, env(safe-area-inset-bottom))'"
count = html.count(old_sub_footer)
assert count >= 1, f"FAIL: sub footers ({count})"
html = html.replace(old_sub_footer, new_sub_footer)

# ── 8. Observer footer
old_obs = "padding:'8px 14px 0', paddingBottom:8"
new_obs = "padding:'8px 14px 0', paddingBottom:'max(8px, env(safe-area-inset-bottom))'"
assert old_obs in html, "FAIL: obs footer"
html = html.replace(old_obs, new_obs, 1)

# ── 9. End screen footer
old_end = "paddingBottom:12, marginTop:'auto'"
new_end = "paddingBottom:'max(12px, env(safe-area-inset-bottom))', marginTop:'auto'"
assert old_end in html, "FAIL: end footer"
html = html.replace(old_end, new_end, 1)

# ── 10. Home screen bottom safe area (if any scrollable content)
# home-inner padding bottom was 44px — keep as is, safe area handled by root container

html = html.replace("const APP_VERSION = 'v9.327';", "const APP_VERSION = 'v9.328';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.328 — black status bar, bottom-only safe area, clean layout")
