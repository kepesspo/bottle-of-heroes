#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove SFX block entirely
old_sfx_start = "// ─── Sound Effects (WAV blob — same engine as lóverseny) ────────\nconst SFX = (() => {"
old_sfx_end = "})();\n"
s = html.find(old_sfx_start)
assert s != -1, "FAIL: SFX start"
e = html.find(old_sfx_end, s) + len(old_sfx_end)
html = html[:s] + html[e:]

# Remove SFX calls
html = html.replace("SFX.win(); ", "")
html = html.replace("SFX.lose(); ", "")
html = html.replace("SFX.ding();\n", "")
html = html.replace("    SFX.tap();\n", "")

# version bump
html = html.replace("const APP_VERSION = 'v9.278';", "const APP_VERSION = 'v9.279';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.279 — hangok eltávolítva")
