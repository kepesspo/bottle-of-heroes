#!/usr/bin/env python3
"""v9.386 — Splash: visszaállítja az opaque t.bg hátteret (transparent = tört)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS: transparent → #F4C57E (JS felülírja theme szerint) ────────────────
old_splash_bg_css = """      background: transparent;
      transition: opacity 0.25s ease; overflow: hidden;"""

new_splash_bg_css = """      background: #F4C57E;
      transition: opacity 0.25s ease; overflow: hidden;"""

assert old_splash_bg_css in html, "FAIL: splash bg css"
html = html.replace(old_splash_bg_css, new_splash_bg_css, 1)

# ── 2. Init script: visszaállítja splash.style.background = t.bg ──────────────
old_bg_js = """  // Splash transparent — a body bg (már t.bg-re van állítva) mutat át"""

new_bg_js = """  // Theme colors — sima flat szín, mint az app (nincs gradient = nincs ugrás)
  splash.style.background = t.bg;"""

assert old_bg_js in html, "FAIL: bg js"
html = html.replace(old_bg_js, new_bg_js, 1)

html = html.replace("const APP_VERSION = 'v9.385';", "const APP_VERSION = 'v9.386';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.386 — Splash opaque t.bg háttér visszaállítva, seamless átmenet")
