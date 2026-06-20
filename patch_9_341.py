#!/usr/bin/env python3
"""v9.341 — OnboardingOverlay: extend behind status bar in PWA mode"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# In PWA on iOS 17+, app content shows behind status bar but position:fixed inset:0
# starts at viewport top (below status bar). Extend overlay upward to cover full screen.
old_overlay = "position:'fixed', inset:0, zIndex:9999, background:'rgba(14,14,24,0.75)', display:'flex', alignItems:'flex-end', justifyContent:'center', padding:'0 16px 40px', backdropFilter:'blur(6px)'"
new_overlay = "position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, zIndex:9999, background:'rgba(14,14,24,0.82)', display:'flex', alignItems:'flex-end', justifyContent:'center', padding:`0 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))`, backdropFilter:'blur(8px)'"
assert old_overlay in html, "FAIL: overlay style"
html = html.replace(old_overlay, new_overlay, 1)

html = html.replace("const APP_VERSION = 'v9.340';", "const APP_VERSION = 'v9.341';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.341 — overlay extends behind status bar, card respects home indicator")
