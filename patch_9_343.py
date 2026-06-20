#!/usr/bin/env python3
"""v9.343 — Switch to black-translucent + paddingTop safe area on screen container
   With black-translucent: overlay dark bg shows THROUGH status bar during onboarding.
   Screen container paddingTop pushes all content below status bar for normal use."""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Switch status bar style to black-translucent
old_meta = '<meta name="apple-mobile-web-app-status-bar-style" content="black"/>'
new_meta = '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>'
assert old_meta in html, "FAIL: status bar meta"
html = html.replace(old_meta, new_meta, 1)

# 2. Screen container: add paddingTop safe area so content stays below status bar
old_container = 'height:\'100dvh\', width:\'100%\', display:\'flex\', flexDirection:\'column\', overflow:\'hidden\', boxSizing:\'border-box\', animation:`slide${dir>0?\'In\':\'Back\'} .35s cubic-bezier(.2,.85,.3,1.05)`'
new_container = 'height:\'100dvh\', width:\'100%\', display:\'flex\', flexDirection:\'column\', overflow:\'hidden\', boxSizing:\'border-box\', paddingTop:\'env(safe-area-inset-top)\', animation:`slide${dir>0?\'In\':\'Back\'} .35s cubic-bezier(.2,.85,.3,1.05)`'
assert old_container in html, "FAIL: screen container"
html = html.replace(old_container, new_container, 1)

# 3. Remove body bg darkening from OnboardingOverlay (no longer needed)
old_effect = '''  React.useEffect(() => {
    const prev = document.body.style.background;
    document.body.style.background = 'rgb(14,14,24)';
    return () => { document.body.style.background = prev; };
  }, []);'''
new_effect = ''
assert old_effect in html, "FAIL: body effect"
html = html.replace(old_effect, new_effect, 1)

html = html.replace("const APP_VERSION = 'v9.342';", "const APP_VERSION = 'v9.343';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.343 — black-translucent + screen container paddingTop, overlay covers status bar")
