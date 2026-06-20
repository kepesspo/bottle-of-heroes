#!/usr/bin/env python3
"""v9.326 — PWA safe area fix: status bar tint overlay, bigger top/bottom buffers"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════════════════
# 1. PlayScreen top bar — increase buffer +6 → +16px
#    Dynamic Island: env(safe-area-inset-top) ≈ 59px → 59+16=75px (clear)
#    Notch iPhone: 44+16=60px (clear)
# ══════════════════════════════════════════════════════════════════════
old_play_topbar = "paddingTop:'max(10px, calc(env(safe-area-inset-top) + 6px))', paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960"
new_play_topbar = "paddingTop:'max(16px, calc(env(safe-area-inset-top) + 16px))', paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960"
assert old_play_topbar in html, "FAIL: PlayScreen top bar padding"
html = html.replace(old_play_topbar, new_play_topbar, 1)

# ══════════════════════════════════════════════════════════════════════
# 2. Game sub-screens top bars (busz/ringfire type) — same fix
# ══════════════════════════════════════════════════════════════════════
old_sub_topbar = "paddingTop:'max(14px, calc(env(safe-area-inset-top) + 6px))'"
new_sub_topbar = "paddingTop:'max(16px, calc(env(safe-area-inset-top) + 16px))'"
count = html.count(old_sub_topbar)
assert count >= 1, f"FAIL: sub-screen top bars (found {count})"
html = html.replace(old_sub_topbar, new_sub_topbar)

# ══════════════════════════════════════════════════════════════════════
# 3. PlayScreen footer — increase bottom buffer +2 → +10px
#    Home indicator: 34+10=44px total (comfortable)
# ══════════════════════════════════════════════════════════════════════
old_play_footer = "padding:'8px 16px', paddingBottom:'max(16px, calc(env(safe-area-inset-bottom) + 2px))', background:'transparent'"
new_play_footer = "padding:'8px 16px', paddingBottom:'max(20px, calc(env(safe-area-inset-bottom) + 10px))', background:'transparent'"
assert old_play_footer in html, "FAIL: PlayScreen footer padding"
html = html.replace(old_play_footer, new_play_footer, 1)

# ══════════════════════════════════════════════════════════════════════
# 4. Game sub-screen footers (busz/ringfire) — same fix
# ══════════════════════════════════════════════════════════════════════
old_sub_footer = "padding:'8px 18px', paddingBottom:'max(16px, calc(env(safe-area-inset-bottom) + 2px))'"
new_sub_footer = "padding:'8px 18px', paddingBottom:'max(20px, calc(env(safe-area-inset-bottom) + 10px))'"
count2 = html.count(old_sub_footer)
assert count2 >= 1, f"FAIL: sub-screen footers (found {count2})"
html = html.replace(old_sub_footer, new_sub_footer)

# ══════════════════════════════════════════════════════════════════════
# 5. STATUS BAR TINT — add a thin dark gradient overlay at top of PlayScreen
#    Fixes: black-translucent forces white text, but warm background makes
#    it invisible. A subtle dark-to-transparent gradient ensures readability.
#    Insert right after the PlayScreen root div opening.
# ══════════════════════════════════════════════════════════════════════
old_play_root = "    <div style={{ flex:1, display:'flex', flexDirection:'column', background: T.playBg || T.bg }}>\n\n      {/* ── Resume offer ── */"
new_play_root = "    <div style={{ flex:1, display:'flex', flexDirection:'column', background: T.playBg || T.bg }}>\n      {/* Status bar tint — ensures status bar text readable in PWA black-translucent mode */}\n      <div style={{ position:'fixed', top:0, left:0, right:0, height:'env(safe-area-inset-top)', background:'linear-gradient(to bottom, rgba(0,0,0,0.28) 0%, rgba(0,0,0,0) 100%)', zIndex:50, pointerEvents:'none' }} />\n\n      {/* ── Resume offer ── */"
assert old_play_root in html, "FAIL: PlayScreen root div"
html = html.replace(old_play_root, new_play_root, 1)

# ══════════════════════════════════════════════════════════════════════
# 6. Home screen top buttons — also need the tint overlay
#    (absolute buttons at top of HomeScreen)
# ══════════════════════════════════════════════════════════════════════

html = html.replace("const APP_VERSION = 'v9.325';", "const APP_VERSION = 'v9.326';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.326 — PWA safe area: top buffer +16px, bottom +10px, status bar tint overlay")
