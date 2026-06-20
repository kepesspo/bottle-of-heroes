#!/usr/bin/env python3
"""v9.327 — Architectural safe area fix: move inset handling to root screen container"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════════════════
# STRATEGY:
#  OLD: Every screen handles its own safe area padding individually
#  NEW: Screen container gets paddingTop/Bottom with box-sizing:border-box
#       All child screens naturally start below status bar / above home indicator
#       Body background (var(--app-bg) = T.bg) fills the safe area zones
#       Fixed overlays (position:fixed; inset:0) need explicit safe area padding
# ══════════════════════════════════════════════════════════════════════

# ── 1. ROOT SCREEN CONTAINER — add safe area padding
old_screen_container = "style={{ height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}"
new_screen_container = "style={{ height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', paddingTop:'env(safe-area-inset-top)', paddingBottom:'env(safe-area-inset-bottom)', boxSizing:'border-box', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}"
assert old_screen_container in html, "FAIL: screen container"
html = html.replace(old_screen_container, new_screen_container, 1)

# ── 2. AppBar CSS — remove safe area padding (now handled at root)
old_appbar_css = ".appbar-shell { position:sticky; top:0; z-index:10; background:#FFFFFF; padding-top:env(safe-area-inset-top); box-shadow:0 4px 18px rgba(20,30,50,0.05); border-bottom-left-radius:24px; border-bottom-right-radius:24px; }"
new_appbar_css = ".appbar-shell { position:sticky; top:0; z-index:10; background:#FFFFFF; box-shadow:0 4px 18px rgba(20,30,50,0.05); border-bottom-left-radius:24px; border-bottom-right-radius:24px; }"
assert old_appbar_css in html, "FAIL: appbar-shell CSS"
html = html.replace(old_appbar_css, new_appbar_css, 1)

# ── 3. BottomBar component — remove safe area paddingBottom
old_bottombar_pad = "      paddingBottom:'max(16px, calc(env(safe-area-inset-bottom) + 2px))',"
new_bottombar_pad = "      paddingBottom:14,"
assert old_bottombar_pad in html, "FAIL: BottomBar paddingBottom"
html = html.replace(old_bottombar_pad, new_bottombar_pad, 1)

# ── 4. BottomBar CSS — remove safe area
old_bottombar_css = ".bottombar-shell { padding:14px 0 max(16px, calc(env(safe-area-inset-bottom) + 2px)); }"
new_bottombar_css = ".bottombar-shell { padding:14px 0 14px; }"
assert old_bottombar_css in html, "FAIL: bottombar-shell CSS"
html = html.replace(old_bottombar_css, new_bottombar_css, 1)

# ── 5. BottomBar CSS landscape override — remove safe area
old_bottombar_landscape = ".bottombar-shell { padding:6px 0 max(10px, calc(env(safe-area-inset-bottom) + 6px)); }"
new_bottombar_landscape = ".bottombar-shell { padding:6px 0 8px; }"
assert old_bottombar_landscape in html, "FAIL: bottombar-shell landscape CSS"
html = html.replace(old_bottombar_landscape, new_bottombar_landscape, 1)

# ── 6. PlayScreen top bar — remove safe area paddingTop, remove tint overlay
old_play_topbar = "paddingTop:'max(16px, calc(env(safe-area-inset-top) + 16px))', paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960"
new_play_topbar = "paddingTop:12, paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960"
assert old_play_topbar in html, "FAIL: PlayScreen top bar"
html = html.replace(old_play_topbar, new_play_topbar, 1)

# ── 7. Remove status bar tint overlay (added in v9.326, now unnecessary)
old_tint = "      {/* Status bar tint — ensures status bar text readable in PWA black-translucent mode */}\n      <div style={{ position:'fixed', top:0, left:0, right:0, height:'env(safe-area-inset-top)', background:'linear-gradient(to bottom, rgba(0,0,0,0.28) 0%, rgba(0,0,0,0) 100%)', zIndex:50, pointerEvents:'none' }} />\n\n      {/* ── Resume offer ── */"
new_tint = "\n      {/* ── Resume offer ── */"
assert old_tint in html, "FAIL: tint overlay"
html = html.replace(old_tint, new_tint, 1)

# ── 8. PlayScreen footer — remove safe area paddingBottom
old_play_footer = "padding:'8px 16px', paddingBottom:'max(20px, calc(env(safe-area-inset-bottom) + 10px))', background:'transparent'"
new_play_footer = "padding:'8px 16px', paddingBottom:8, background:'transparent'"
assert old_play_footer in html, "FAIL: PlayScreen footer"
html = html.replace(old_play_footer, new_play_footer, 1)

# ── 9. Game sub-screen top bars — remove safe area
old_sub_topbar = "paddingTop:'max(16px, calc(env(safe-area-inset-top) + 16px))'"
new_sub_topbar = "paddingTop:12"
count = html.count(old_sub_topbar)
assert count >= 1, f"FAIL: sub-screen top bars (found {count})"
html = html.replace(old_sub_topbar, new_sub_topbar)

# ── 10. Game sub-screen footers — remove safe area
old_sub_footer = "padding:'8px 18px', paddingBottom:'max(20px, calc(env(safe-area-inset-bottom) + 10px))'"
new_sub_footer = "padding:'8px 18px', paddingBottom:8"
count2 = html.count(old_sub_footer)
assert count2 >= 1, f"FAIL: sub-screen footers (found {count2})"
html = html.replace(old_sub_footer, new_sub_footer)

# ── 11. Observer footer — remove safe area
old_obs = "padding:'8px 14px 0', paddingBottom:'max(16px, calc(env(safe-area-inset-bottom) + 2px))'"
new_obs = "padding:'8px 14px 0', paddingBottom:8"
assert old_obs in html, "FAIL: observer footer"
html = html.replace(old_obs, new_obs, 1)

# ── 12. EndScreen footer — remove safe area
old_end = "paddingBottom:'max(16px, calc(env(safe-area-inset-bottom) + 2px))', marginTop:'auto'"
new_end = "paddingBottom:12, marginTop:'auto'"
assert old_end in html, "FAIL: end screen footer"
html = html.replace(old_end, new_end, 1)

# ── 13. Home screen — revert safe area on absolute buttons (no longer needed)
old_topleft = "top:'max(14px, calc(env(safe-area-inset-top) + 8px))', left:18, zIndex:10, display:'flex', flexDirection:'column', gap:8, alignItems:'flex-start'"
new_topleft = "top:14, left:18, zIndex:10, display:'flex', flexDirection:'column', gap:8, alignItems:'flex-start'"
assert old_topleft in html, "FAIL: home topleft"
html = html.replace(old_topleft, new_topleft, 1)

old_topright = "top:'max(14px, calc(env(safe-area-inset-top) + 8px))', right:18, zIndex:10, display:'flex', background:T.surface, borderRadius:18, boxShadow:T.shadow, overflow:'hidden'"
new_topright = "top:14, right:18, zIndex:10, display:'flex', background:T.surface, borderRadius:18, boxShadow:T.shadow, overflow:'hidden'"
assert old_topright in html, "FAIL: home topright"
html = html.replace(old_topright, new_topright, 1)

# ── 14. Home inner — revert safe area top padding
old_home_inner = "      gap:28px; padding:max(52px, calc(env(safe-area-inset-top) + 36px)) 22px 44px;"
new_home_inner = "      gap:28px; padding:52px 22px 44px;"
assert old_home_inner in html, "FAIL: home-inner padding"
html = html.replace(old_home_inner, new_home_inner, 1)

# ── 15. PlayScreen top bar: also fix safe area inset reference in line 42373 type
# (the online/busz sub-screen topbars handled in step 9)

# ── 16. ROUND POPUP — add safe area inset to content so it's visible within safe zones
# The overlay itself (position:fixed; inset:0) covers full screen including safe zones
# Make it more opaque so the body T.bg doesn't show as a lighter strip
old_round_overlay = "position:'fixed', inset:0, zIndex:9998, background:'rgba(14,14,24,0.65)', display:'flex', alignItems:'center', justifyContent:'center', backdropFilter:'blur(4px)'"
new_round_overlay = "position:'fixed', inset:0, zIndex:9998, background:'rgba(14,14,24,0.88)', display:'flex', alignItems:'center', justifyContent:'center', backdropFilter:'blur(6px)'"
assert old_round_overlay in html, "FAIL: round popup overlay"
html = html.replace(old_round_overlay, new_round_overlay, 1)

# ── 17. Remove the env(safe-area-inset-bottom) observer home indicator spacer (now root handles it)
old_obs_spacer = "        <div style={{ height:'env(safe-area-inset-bottom, 0px)', background:T.bg }} />"
new_obs_spacer = ""
if old_obs_spacer in html:
    html = html.replace(old_obs_spacer, new_obs_spacer, 1)

html = html.replace("const APP_VERSION = 'v9.326';", "const APP_VERSION = 'v9.327';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.327 — Safe area at root container, all individual screen safe areas removed")
