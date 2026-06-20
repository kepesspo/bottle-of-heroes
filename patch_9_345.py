#!/usr/bin/env python3
"""v9.345 — Design fix: overlay gradient fades FROM app color (matching status bar) TO dark
   Instead of fighting iOS status bar limitation, embrace it with a smooth gradient."""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. OnboardingOverlay: gradient from T.bg at top → dark below (status bar blends in)
old_onboard = "position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, zIndex:9999, background:'rgba(14,14,24,0.82)', display:'flex', alignItems:'flex-end', justifyContent:'center', padding:`0 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))`, backdropFilter:'blur(8px)'"
new_onboard = "position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, zIndex:9999, background:`linear-gradient(to bottom, ${T.bg} 0%, rgba(14,14,24,0.92) 90px)`, display:'flex', alignItems:'flex-end', justifyContent:'center', padding:`0 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))`"
assert old_onboard in html, "FAIL: onboarding overlay"
html = html.replace(old_onboard, new_onboard, 1)

# 2. Round popup overlay: same gradient treatment
old_round = "position:'fixed', inset:0, zIndex:9998, background:'rgba(14,14,24,0.88)', display:'flex', alignItems:'center', justifyContent:'center', backdropFilter:'blur(6px)'"
new_round = "position:'fixed', inset:0, zIndex:9998, background:`linear-gradient(to bottom, ${T.bg} 0%, rgba(14,14,24,0.92) 90px)`, display:'flex', alignItems:'center', justifyContent:'center'"
assert old_round in html, "FAIL: round popup overlay"
html = html.replace(old_round, new_round, 1)

html = html.replace("const APP_VERSION = 'v9.344';", "const APP_VERSION = 'v9.345';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.345 — overlay gradient matches status bar at top, blends to dark below")
