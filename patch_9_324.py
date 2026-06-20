#!/usr/bin/env python3
"""v9.324 — PWA fix: restore black-translucent, fix excessive bottom padding"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Restore black-translucent (correct for PWA standalone fullscreen)
old_status = '<meta name="apple-mobile-web-app-status-bar-style" content="default"/>'
new_status = '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>'
assert old_status in html, "FAIL: status bar"
html = html.replace(old_status, new_status, 1)

# ── 2. BottomBar component — reduce bottom padding
# env(safe-area-inset-bottom) ≈ 34px → old: 34+8=42px, new: 34+2=36px (tighter)
old_bottombar_pad = "      paddingBottom:'max(20px, calc(env(safe-area-inset-bottom) + 8px))',"
new_bottombar_pad = "      paddingBottom:'max(16px, calc(env(safe-area-inset-bottom) + 2px))',"
assert old_bottombar_pad in html, "FAIL: BottomBar paddingBottom"
html = html.replace(old_bottombar_pad, new_bottombar_pad, 1)

# ── 3. PlayScreen footer — reduce bottom padding
old_play_footer_pad = "      {!hideFooter && <div style={{ flexShrink:0, padding:'8px 16px', paddingBottom:'max(20px, calc(env(safe-area-inset-bottom) + 8px))', background:'transparent' }}>"
new_play_footer_pad = "      {!hideFooter && <div style={{ flexShrink:0, padding:'8px 16px', paddingBottom:'max(16px, calc(env(safe-area-inset-bottom) + 2px))', background:'transparent' }}>"
assert old_play_footer_pad in html, "FAIL: play footer pad"
html = html.replace(old_play_footer_pad, new_play_footer_pad, 1)

# ── 4. Busz/ringfire screens footer padding
old_game_footer1 = "        <div style={{ flexShrink:0, padding:'8px 18px', paddingBottom:'max(20px, calc(env(safe-area-inset-bottom) + 8px))' }}>"
new_game_footer1 = "        <div style={{ flexShrink:0, padding:'8px 18px', paddingBottom:'max(16px, calc(env(safe-area-inset-bottom) + 2px))' }}>"
count1 = html.count(old_game_footer1)
assert count1 >= 1, f"FAIL: game footer1 (found {count1})"
html = html.replace(old_game_footer1, new_game_footer1)

# ── 5. Observer footer
old_obs_footer = "      <div style={{ flexShrink:0, background:T.bg, padding:'8px 14px 0', paddingBottom:'max(20px, calc(env(safe-area-inset-bottom) + 10px))' }}>"
new_obs_footer = "      <div style={{ flexShrink:0, background:T.bg, padding:'8px 14px 0', paddingBottom:'max(16px, calc(env(safe-area-inset-bottom) + 2px))' }}>"
assert old_obs_footer in html, "FAIL: obs footer"
html = html.replace(old_obs_footer, new_obs_footer, 1)

# ── 6. EndScreen / other footers with + 10px
old_end_footer = "          <div style={{ paddingTop:10, paddingLeft:16, paddingRight:16, paddingBottom:'max(22px, calc(env(safe-area-inset-bottom) + 10px))', marginTop:'auto' }}>"
new_end_footer = "          <div style={{ paddingTop:10, paddingLeft:16, paddingRight:16, paddingBottom:'max(16px, calc(env(safe-area-inset-bottom) + 2px))', marginTop:'auto' }}>"
assert old_end_footer in html, "FAIL: end footer"
html = html.replace(old_end_footer, new_end_footer, 1)

# ── 7. CSS .bottombar-shell — also reduce
old_bottombar_shell = "    .bottombar-shell { padding:14px 0 max(28px, calc(env(safe-area-inset-bottom) + 18px)); }"
new_bottombar_shell = "    .bottombar-shell { padding:14px 0 max(16px, calc(env(safe-area-inset-bottom) + 2px)); }"
assert old_bottombar_shell in html, "FAIL: bottombar-shell"
html = html.replace(old_bottombar_shell, new_bottombar_shell, 1)

html = html.replace("const APP_VERSION = 'v9.323';", "const APP_VERSION = 'v9.324';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.324 — PWA: black-translucent restored, bottom padding reduced (34+2=36px vs 34+8=42px)")
